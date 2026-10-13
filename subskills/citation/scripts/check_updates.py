"""Check Crossref update notices pointing to cited DOIs; never infer a clean bill of health."""

from __future__ import annotations

import argparse
import sys
import urllib.parse
from pathlib import Path

from citation_common import clean_doi, parse_inputs, report_base, valid_doi, write_report
from verify_metadata import LookupUnavailable, MetadataClient


def check_entry(entry: dict, client: MetadataClient) -> dict:
    doi = clean_doi(entry.get("doi", ""))
    result = {"key": entry["ID"], "doi": doi, "status": "NO_DOI", "notices": []}
    start = len(client.evidence)
    if doi and not valid_doi(doi):
        result["status"] = "INVALID_DOI"
    elif doi:
        url = "https://api.crossref.org/works?" + urllib.parse.urlencode({"filter": f"updates:{doi}", "rows": 100})
        try:
            payload = client.get_json(url)
            message = payload.get("message") if isinstance(payload, dict) else None
            if not isinstance(message, dict) or not isinstance(message.get("items"), list):
                raise LookupUnavailable("Invalid Crossref updates response")
            total = message.get("total-results")
            if not isinstance(total, int) or total < 0:
                raise LookupUnavailable("Missing updates result count")
            for item in message["items"]:
                for update in item.get("update-to", []):
                    # update-to points FROM the notice TO the affected work.
                    # Never label a cited notice itself as a retracted paper.
                    if clean_doi(update.get("DOI", "")) == doi:
                        result["notices"].append({"notice_doi": item.get("DOI", ""),
                                                  "title": item.get("title", []),
                                                  "type": update.get("type", "unknown"),
                                                  "source": update.get("source", "unknown"),
                                                  "updated": update.get("updated", {})})
            result["status"] = "UPDATE_NOTICE" if result["notices"] else "NO_UPDATE_FOUND"
            result["complete"] = total <= len(message["items"])
            if not result["complete"]:
                result["status"] = "PARTIAL"
            elif message["items"] and not result["notices"]:
                raise LookupUnavailable("Returned updates lack a verifiable link to the queried DOI")
        except (LookupUnavailable, TypeError, KeyError, AttributeError) as error:
            result.update(status="UNAVAILABLE", error=str(error), complete=False)
    result["evidence"] = client.evidence[start:]
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bib", type=Path)
    parser.add_argument("--aux", type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--online", action="store_true")
    mode.add_argument("--cache-only", action="store_true")
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--cache-hours", type=float, default=24)
    parser.add_argument("--timeout", type=float, default=20)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.timeout <= 0 or args.cache_hours < 0 or (args.limit is not None and args.limit <= 0):
        parser.error("Timeout/limit must be positive; cache-hours must be nonnegative")
    try:
        all_entries, entries, _, missing = parse_inputs(args.bib, args.aux)
        if missing or not entries or len({e['ID'] for e in entries}) != len(entries):
            raise ValueError("Missing, duplicate or empty citation selection; run offline audit first.")
        if any((args.out_dir / f"publication-updates.{ext}").exists() for ext in ("json", "md")):
            raise FileExistsError("Report already exists; choose a new --out-dir.")
        report = report_base(args.bib, "updates-online" if args.online else "updates-cache-only")
        report["scope"] = "Crossref indexed update notices only. NO_UPDATE_FOUND does not mean not retracted. Read publisher notices."
        report.update(total_entries=len(all_entries), selection="aux" if args.aux else "all",
                      selected_entries=len(entries), checked_entries=len(entries[:args.limit]),
                      partial=args.limit is not None and len(entries) > args.limit)
        client = MetadataClient(args.cache_dir or args.out_dir / "evidence", online=args.online,
                                timeout=args.timeout, max_age=args.cache_hours * 3600)
        if args.online:
            print("Network: cited DOIs sent to Crossref update search; no manuscript upload.", file=sys.stderr)
        for entry in entries[:args.limit]:
            result = check_entry(entry, client)
            report["entries"].append(result)
            print(f"{entry['ID']}: {result['status']}", file=sys.stderr)
        write_report(report, args.out_dir, "publication-updates")
    except Exception as error:
        print(f"Update check could not complete: {error}", file=sys.stderr)
        return 2
    states = {e["status"] for e in report["entries"]}
    if states & {"UNAVAILABLE", "PARTIAL"}:
        return 2
    if states & {"UPDATE_NOTICE", "INVALID_DOI"} or (args.strict and (states != {"NO_UPDATE_FOUND"} or report["partial"])):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
