"""Offline bibliography audit; never modifies BibTeX or manuscript files."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from citation_common import (authors, clean_doi, issue, normalized, parse_inputs,
                             report_base, valid_doi, write_report)


def audit(bib: Path, aux: Path | None = None, min_count: int | None = None) -> dict:
    all_entries, entries, controls, missing = parse_inputs(bib, aux)
    report = report_base(bib, "offline")
    report.update(total_entries=len(all_entries), selected_entries=len(entries),
                  checked_entries=len(entries), partial=False,
                  control_entries=len(controls), selection="aux" if aux else "all")
    problems = report["issues"]
    for key, count in Counter(e["ID"] for e in all_entries + controls).items():
        if count > 1:
            problems.append(issue("DUPLICATE_KEY", f"Key occurs {count} times.", key, "error"))
    for key in missing:
        problems.append(issue("UNDEFINED_CITATION", "AUX key missing from supplied bibliography.", key, "error"))
    if not entries:
        problems.append(issue("EMPTY_SELECTION", "No bibliography entries selected; check AUX freshness.", severity="error"))
    if min_count is not None and len({e['ID'] for e in entries}) < min_count:
        problems.append(issue("COUNT_BELOW_REQUEST", f"Selected distinct keys below requested {min_count}.", severity="error"))
    dois, titles = defaultdict(list), defaultdict(list)
    for entry in entries:
        key, kind = entry["ID"], entry["ENTRYTYPE"]
        for field in ("title", "year"):
            if not entry.get(field) and not (field == "year" and entry.get("date")):
                problems.append(issue("MISSING_FIELD", f"Missing {field}; inspect source type.", key))
        if not any(entry.get(f) for f in ("author", "editor", "organization", "institution")):
            problems.append(issue("MISSING_CREATOR", "No author/editor/organization/institution.", key))
        container = {"article": "journal", "inproceedings": "booktitle", "incollection": "booktitle"}.get(kind)
        if container and not entry.get(container):
            problems.append(issue("MISSING_CONTAINER", f"Missing {container}.", key))
        year = entry.get("year", "")
        if year and not re.fullmatch(r"\d{4}", year):
            problems.append(issue("YEAR_FORMAT", f"Nonstandard year: {year}.", key))
        if entry.get("crossref"):
            problems.append(issue("CROSSREF_INHERITANCE", "Inherited fields are not merged; review parent record.", key, "info"))
        doi = clean_doi(entry.get("doi", ""))
        if doi:
            if valid_doi(doi):
                dois[doi].append(key)
            else:
                problems.append(issue("INVALID_DOI_SYNTAX", f"Malformed DOI: {doi}.", key, "error"))
        else:
            problems.append(issue("NO_DOI", "No DOI: may be legitimate; online verification needs another source.", key, "info"))
        title = normalized(entry.get("title", ""))
        if title:
            titles[title].append(key)
        if entry.get("author"):
            try:
                _, truncated = authors(entry["author"])
                if truncated:
                    problems.append(issue("TRUNCATED_AUTHORS", "BibTeX contains 'others'; preserve full source list when available.", key))
            except Exception as error:
                problems.append(issue("AUTHOR_PARSE", str(error), key))
        if re.search(r"\d-\d", entry.get("pages", "")):
            problems.append(issue("PAGE_DASH", "Page range uses a single hyphen; verify range before formatting.", key))
        report["entries"].append({"key": key, "type": kind, "doi": doi, "status": "LOCAL_ONLY"})
    for mapping, code in ((dois, "DUPLICATE_DOI"), (titles, "DUPLICATE_TITLE")):
        for value, keys in mapping.items():
            if len(keys) > 1:
                problems.append(issue(code, f"Shared value {value!r}: {', '.join(keys)}. Review versions; do not auto-merge."))
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bib", type=Path)
    parser.add_argument("--aux", type=Path, help="Use compiled citation keys, including child AUX files.")
    parser.add_argument("--min-count", type=int, help="Optional explicit count gate; no default quota.")
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.min_count is not None and args.min_count < 0:
        parser.error("--min-count must be nonnegative")
    try:
        report = audit(args.bib, args.aux, args.min_count)
        write_report(report, args.out_dir, "bibtex-audit")
    except Exception as error:
        print(f"Audit could not complete: {error}", file=sys.stderr)
        return 2
    print(f"Selected {report['selected_entries']} entries; {len(report['issues'])} findings.")
    return 1 if any(p["severity"] == "error" for p in report["issues"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
