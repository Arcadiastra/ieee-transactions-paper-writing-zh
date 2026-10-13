"""Read-only citation utilities. Python 3.10+, UTF-8 throughout."""

from __future__ import annotations

import hashlib
import html
import json
import re
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import splitname
from pylatexenc.latex2text import LatexNodes2Text


def plain(value: str) -> str:
    return " ".join(LatexNodes2Text().latex_to_text(str(value)).split())


def normalized(value: str) -> str:
    value = unicodedata.normalize("NFKD", html.unescape(plain(value))).casefold()
    return " ".join("".join(c if c.isalnum() else " " for c in value
                            if not unicodedata.combining(c)).split())


def clean_doi(value: str) -> str:
    # DOI identifiers are not prose: LaTeX parsing treats raw percent signs as comments.
    value = re.sub(r"\\([%_#&{}])", r"\1", str(value).strip())
    value = re.sub(r"^doi:\s*", "", value, flags=re.I)
    value, is_url = re.subn(r"^https?://(?:dx\.)?doi\.org/", "", value, flags=re.I)
    # Decode URLs once; a bare DOI may contain literal percent-escape-like text.
    if is_url:
        value = unquote(value)
    return value.strip().lower()


def valid_doi(value: str) -> bool:
    return bool(re.fullmatch(r"10\.\d{4,9}/\S+", value))


def read_bib(path: Path) -> tuple[list[dict], list[dict]]:
    parser = BibTexParser(common_strings=True, ignore_nonstandard_types=False,
                          homogenize_fields=False, interpolate_strings=True,
                          add_missing_from_crossref=False)
    database = parser.parse(path.read_text(encoding="utf-8-sig"), partial=False)
    # bibtexparser preserves otherwise unparsed text as comments. An entry-like
    # comment is suspicious: fail closed rather than silently auditing a subset.
    for comment in database.comments:
        if re.search(r"(?m)^\s*@(?:article|book|inproceedings|misc|online|\w+)\s*[{(]", comment):
            raise ValueError("Unparsed entry-like text; inspect BibTeX syntax/comments.")
    controls = [e for e in database.entries if e["ENTRYTYPE"].lower() == "ieeetranbstctl"]
    entries = [e for e in database.entries if e not in controls]
    if not entries:
        raise ValueError("No bibliographic entries found.")
    return entries, controls


def strip_tex_comments(text: str) -> str:
    lines = []
    for line in text.splitlines():
        for index, char in enumerate(line):
            if char == "%":
                preceding = len(line[:index]) - len(line[:index].rstrip("\\"))
                if preceding % 2 == 0:
                    line = line[:index]
                    break
        lines.append(line)
    return "\n".join(lines)


def aux_keys(path: Path) -> set[str]:
    """Read compiled BibTeX/biblatex citation keys, never execute TeX."""
    seen: set[Path] = set()
    keys: set[str] = set()
    boundary = path.resolve().parent

    def visit(current: Path) -> None:
        current = current.resolve()
        if current in seen:
            return
        if not current.is_relative_to(boundary):
            raise ValueError("AUX include leaves the root AUX directory.")
        seen.add(current)
        text = strip_tex_comments(current.read_text(encoding="utf-8-sig"))
        for match in re.finditer(r"\\citation\s*\{([^{}]*)\}", text):
            keys.update(k.strip() for k in match[1].split(",") if k.strip())
        for match in re.finditer(r"\\abx@aux@(cite|nocite)\s*\{[^{}]*\}\s*\{([^{}]*)\}", text):
            keys.update(k.strip() for k in match[2].split(",") if k.strip())
        for match in re.finditer(r"\\@input\s*\{([^{}]+)\}", text):
            included = current.parent / match[1]
            if not included.exists():
                included = boundary / match[1]
            visit(included)

    visit(path)
    return keys


def selection(entries: list[dict], controls: list[dict], aux: Path | None):
    if aux is None:
        return entries, []
    cited = aux_keys(aux)
    known = {e["ID"] for e in entries + controls}
    missing = sorted(cited - known - {"*"})
    selected = entries if "*" in cited else [e for e in entries if e["ID"] in cited]
    return selected, missing


def authors(value: str) -> tuple[list[dict], bool]:
    """Split only top-level BibTeX 'and'; delegate name grammar to the parser."""
    parts, start, depth, i = [], 0, 0, 0
    while i < len(value):
        if value[i] == "\\":
            i += 2
            continue
        if value[i] == "{":
            depth += 1
        elif value[i] == "}":
            depth -= 1
        match = re.match(r"\s+and\s+", value[i:], re.I) if depth == 0 else None
        if match:
            parts.append(value[start:i].strip())
            i += match.end()
            start = i
            continue
        i += 1
    parts.append(value[start:].strip())
    output, truncated = [], False
    for part in filter(None, parts):
        if part.lower() == "others":
            truncated = True
        elif part.startswith("{") and part.endswith("}"):
            output.append({"literal": plain(part)})
        else:
            name = splitname(part)
            output.append({"family": plain(" ".join(name["von"] + name["last"])),
                           "given": plain(" ".join(name["first"]))})
    return output, truncated


def issue(code: str, message: str, key: str = "", severity: str = "warning") -> dict:
    return {"key": key, "severity": severity, "code": code, "message": message}


def report_base(path: Path, mode: str) -> dict:
    return {"schema_version": 1, "mode": mode,
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "input": str(path.resolve()), "input_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "scope": "Bibliographic metadata only; claim support and JCR ranks are not verified.",
            "issues": [], "entries": []}


def cell(value: object) -> str:
    text = json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value)
    return html.escape(text).replace("|", "&#124;").replace("\n", " ").replace("\r", " ")


def write_report(report: dict, out: Path, stem: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    json_path, md_path = out / f"{stem}.json", out / f"{stem}.md"
    if json_path.exists() or md_path.exists():
        raise FileExistsError("Report already exists; choose a new --out-dir.")
    selected = report.get("selected_entries")
    checked = report.get("checked_entries", len(report["entries"]))
    partial = report.get("partial", False) or (selected is not None and checked < selected)
    coverage = "UNKNOWN" if selected is None else "EMPTY" if selected == 0 else "PARTIAL" if partial else "FULL"
    statuses = Counter(record.get("status", "NOT_CHECKED") for record in report["entries"])
    incomplete = (partial or report.get("provider_complete") is False or
                  any(record.get("provider_complete") is False or record.get("complete") is False
                      for record in report["entries"]) or
                  any(status in statuses for status in ("UNAVAILABLE", "PARTIAL", "NOT_CHECKED")))
    if report.get("mode") == "offline":
        completion = "LOCAL_ONLY: offline audit only; publication facts were not verified."
    elif incomplete:
        completion = "INCOMPLETE: selected entries remain unprocessed or source retrieval was incomplete."
    elif coverage in ("EMPTY", "UNKNOWN"):
        completion = "NOT_ESTABLISHED: no nonempty, known selection was checked."
    else:
        completion = "PROCESSING_FINISHED: selected entries processed; see record statuses below."
    lines = [f"# Citation report: {stem}", "", report["scope"], "",
             "## Check scope and completion", "",
             f"- Mode: {cell(report.get('mode', 'unknown'))}",
             f"- Selection: {cell(report.get('selection', 'unknown'))}",
             f"- Bibliography entries: {cell(report.get('total_entries', 'unknown'))}",
             f"- Processed / selected entries: **{checked} / {selected if selected is not None else 'unknown'}**",
             f"- Coverage: **{coverage}** (relative to the selected entries).",
             f"- Completion: {completion}",
             "- Record statuses: " + (", ".join(f"{cell(status)}: {count}" for status, count in sorted(statuses.items()))
                                        or "No records processed."),
             "",
             f"Input SHA-256: `{report['input_sha256']}`", "",
             "Statuses are review aids, not proof of authenticity or fabrication.", "",
             "## Findings", "", "| Key | Severity | Code | Detail |", "| --- | --- | --- | --- |"]
    for row in report["issues"]:
        lines.append("| " + " | ".join(cell(row[k]) for k in ("key", "severity", "code", "message")) + " |")
    if not report["issues"]:
        lines.append("| | | | No local findings reported. |")
    if report["entries"]:
        lines.extend(["", "## Records", "", "| Key | Status | Evidence / details |", "| --- | --- | --- |"])
        for record in report["entries"]:
            lines.append(f"| {cell(record['key'])} | {cell(record.get('status', 'LOCAL_ONLY'))} | {cell(record)} |")
    with json_path.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_inputs(bib: Path, aux: Path | None):
    entries, controls = read_bib(bib)
    selected, missing = selection(entries, controls, aux)
    return entries, selected, controls, missing
