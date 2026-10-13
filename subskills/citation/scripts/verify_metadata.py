"""Opt-in Crossref/DataCite checks with field comparisons and saved evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

from citation_common import (authors, clean_doi, normalized, parse_inputs, plain,
                             report_base, valid_doi, write_report)


class LookupUnavailable(Exception):
    pass


class MetadataClient:
    def __init__(self, cache: Path, *, online=False, timeout=20, retries=2,
                 interval=1.0, max_age=86400, email=None):
        self.cache, self.online = cache, online
        self.timeout, self.retries = timeout, retries
        self.interval, self.max_age = interval, max_age
        self.last_request = 0.0
        self.headers = {"User-Agent": "ieee-transactions-writing-zh-citation/1.0"}
        if email:
            self.headers["User-Agent"] += f" (mailto:{email})"
        self.headers["Accept"] = "application/json"
        self.evidence: list[dict] = []

    def get_json(self, url: str):
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "https" or parsed.netloc not in {"api.crossref.org", "api.datacite.org"}:
            raise LookupUnavailable("Unsupported metadata endpoint")
        path = self.cache / (hashlib.sha256(url.encode("utf-8")).hexdigest() + ".json")
        if path.exists():
            try:
                saved = json.loads(path.read_text(encoding="utf-8"))
                age = time.time() - float(saved["fetched_epoch"])
                if saved["url"] == url and 0 <= age <= self.max_age and saved["http_status"] in (200, 404):
                    self.evidence.append({"url": url, "file": str(path.resolve()),
                                          "cached": True, "fetched_utc": saved["fetched_utc"]})
                    return saved["payload"]
            except (ValueError, KeyError, TypeError):
                pass
        if not self.online:
            raise LookupUnavailable("No fresh cached response (network disabled)")
        for attempt in range(self.retries + 1):
            time.sleep(max(0.0, self.interval - (time.monotonic() - self.last_request)))
            self.last_request = time.monotonic()
            try:
                request = urllib.request.Request(url, headers=self.headers)
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    if urllib.parse.urlparse(response.geturl()).netloc not in {"api.crossref.org", "api.datacite.org"}:
                        raise LookupUnavailable("Unexpected metadata redirect")
                    raw = response.read(8 * 1024 * 1024 + 1)
                    if len(raw) > 8 * 1024 * 1024:
                        raise LookupUnavailable("Metadata response exceeds size limit")
                    payload, status = json.loads(raw.decode("utf-8")), 200
                break
            except urllib.error.HTTPError as error:
                if error.code == 404:
                    payload, status = None, 404
                    break
                if (error.code == 429 or error.code >= 500) and attempt < self.retries:
                    delay = error.headers.get("Retry-After", "") if error.headers else ""
                    time.sleep(min(float(delay), 30) if delay.isdigit() else 2 ** attempt)
                    continue
                raise LookupUnavailable(f"HTTP {error.code}") from error
            except (urllib.error.URLError, TimeoutError, OSError) as error:
                if attempt < self.retries:
                    time.sleep(2 ** attempt)
                    continue
                raise LookupUnavailable(f"Network unavailable: {type(error).__name__}") from error
            except (ValueError, UnicodeDecodeError) as error:
                raise LookupUnavailable("Non-JSON or malformed response") from error
        self.cache.mkdir(parents=True, exist_ok=True)
        saved = {"url": url, "http_status": status, "fetched_epoch": time.time(),
                 "fetched_utc": datetime.now(timezone.utc).isoformat(), "payload": payload}
        path.write_text(json.dumps(saved, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self.evidence.append({"url": url, "file": str(path.resolve()),
                              "cached": False, "fetched_utc": saved["fetched_utc"]})
        return payload


def crossref_record(payload: dict) -> dict:
    data = payload.get("message")
    if payload.get("status") != "ok" or not isinstance(data, dict) or not data.get("DOI") or not data.get("title"):
        raise LookupUnavailable("Incomplete Crossref metadata")
    years = {}
    for field in ("published-print", "published-online", "issued", "published"):
        parts = data.get(field, {}).get("date-parts", [[]])
        if parts and parts[0]:
            years[field] = str(parts[0][0])
    return {"doi": data["DOI"], "title": data["title"][0], "years": years,
            "authors": [{"family": a.get("family", ""), "given": a.get("given", ""),
                         "literal": a.get("name", "")} for a in data.get("author", [])],
            "venue": (data.get("container-title") or [""])[0],
            "volume": data.get("volume", ""), "number": data.get("issue", ""),
            "pages": data.get("page", ""), "eid": data.get("article-number", ""),
            "type": data.get("type", "")}


def datacite_record(payload: dict) -> dict:
    data = payload.get("data", {}).get("attributes")
    if not isinstance(data, dict) or not data.get("doi") or not data.get("titles"):
        raise LookupUnavailable("Incomplete DataCite metadata")
    people = []
    for author in data.get("creators", []):
        if author.get("familyName"):
            people.append({"family": author["familyName"], "given": author.get("givenName", "")})
        else:
            people.append({"literal": author.get("name", "")})
    return {"doi": data["doi"], "title": data["titles"][0].get("title", ""),
            "years": {"publicationYear": str(data["publicationYear"])} if data.get("publicationYear") else {},
            "authors": people, "venue": "", "volume": "", "number": "", "pages": "", "eid": "",
            "type": data.get("types", {}).get("resourceTypeGeneral", "")}


def venue_matches(a: str, b: str) -> bool:
    stop = {"of", "the", "and", "in", "on", "for"}
    left = [t for t in normalized(a).split() if t not in stop]
    right = [t for t in normalized(b).split() if t not in stop]
    return bool(left) and len(left) == len(right) and all(
        x.startswith(y) or y.startswith(x) for x, y in zip(left, right))


def given_names_match(a: str, b: str) -> bool:
    left, right = normalized(a).split(), normalized(b).split()
    if len(left) != len(right):
        return False
    return all(x == y or (min(len(x), len(y)) == 1 and x[0] == y[0]) for x, y in zip(left, right))


def compare(entry: dict, record: dict) -> tuple[list[dict], list[str]]:
    differences, compared = [], []

    def diff(field, local, remote, reason):
        differences.append({"field": field, "local": local, "remote": remote, "reason": reason})

    compared.append("doi")
    if clean_doi(entry.get("doi", "")) != clean_doi(record.get("doi", "")):
        diff("doi", entry.get("doi", ""), record.get("doi", ""), "IDENTIFIER_MISMATCH")
    local_title, remote_title = entry.get("title", ""), record.get("title", "")
    if local_title and remote_title:
        compared.append("title")
        if normalized(local_title) != normalized(remote_title):
            score = SequenceMatcher(None, normalized(local_title), normalized(remote_title)).ratio()
            diff("title", local_title, remote_title, f"TITLE_DIFFERENCE similarity={score:.3f}; inspect manually")
    else:
        diff("title", local_title, remote_title, "MISSING_TITLE")
    years = record.get("years", {})
    if entry.get("year") and years:
        compared.append("year")
        preferred = next(iter(years.values()))
        if entry["year"] != preferred:
            reason = "DATE_VARIANT" if entry["year"] in years.values() else "YEAR_DIFFERENCE"
            diff("year", entry["year"], years, reason)
    for field in ("volume", "number", "pages", "eid"):
        if entry.get(field) and record.get(field):
            compared.append(field)
            if normalized(entry[field]) != normalized(record[field]):
                diff(field, entry[field], record[field], "FIELD_DIFFERENCE")
    venue = entry.get("journal") or entry.get("booktitle")
    if venue and record.get("venue"):
        compared.append("venue")
        if not venue_matches(venue, record["venue"]):
            diff("venue", venue, record["venue"], "VENUE_DIFFERENCE_OR_ABBREVIATION")
    if entry.get("author") and record.get("authors"):
        compared.append("authors")
        try:
            local_authors, truncated = authors(entry["author"])
            remote_authors = record["authors"]
            if truncated or len(local_authors) != len(remote_authors):
                diff("authors", entry["author"], remote_authors, "AUTHOR_COUNT_OR_TRUNCATION")
            for index, (a, b) in enumerate(zip(local_authors, remote_authors), 1):
                if a.get("literal") or b.get("literal"):
                    diff(f"author_{index}", a, b, "CORPORATE_OR_UNSTRUCTURED_NAME_REVIEW")
                elif normalized(a.get("family", "")) != normalized(b.get("family", "")):
                    diff(f"author_{index}", a, b, "AUTHOR_FAMILY_OR_ORDER_DIFFERENCE")
                elif a.get("given") and b.get("given") and not given_names_match(a["given"], b["given"]):
                    diff(f"author_{index}", a, b, "AUTHOR_GIVEN_NAME_DIFFERENCE")
        except Exception as error:
            diff("authors", entry["author"], record["authors"], f"AUTHOR_PARSE: {error}")
    return differences, compared


def verify_entry(entry: dict, client: MetadataClient, search_titles=False) -> dict:
    result = {"key": entry["ID"], "status": "NOT_CHECKED", "attempts": [], "differences": []}
    doi = clean_doi(entry.get("doi", ""))
    evidence_start = len(client.evidence)
    if not doi:
        result["status"] = "NO_DOI"
        if search_titles and entry.get("title"):
            url = "https://api.crossref.org/works?" + urllib.parse.urlencode({"query.title": plain(entry["title"]), "rows": 5})
            try:
                response = client.get_json(url)
                items = response.get("message", {}).get("items") if isinstance(response, dict) else None
                if not isinstance(items, list):
                    raise LookupUnavailable("Invalid title-search response")
                result["candidates"] = [{"doi": r.get("DOI"), "title": r.get("title"),
                                         "year": r.get("issued"), "authors": r.get("author")} for r in items]
                result["status"] = "TITLE_CANDIDATES" if items else "NO_CANDIDATES"
            except (LookupUnavailable, TypeError, KeyError, AttributeError) as error:
                result.update(status="UNAVAILABLE", error=str(error))
    elif not valid_doi(doi):
        result.update(status="INVALID_DOI", error="Run offline audit and check DOI syntax.")
    else:
        for provider, endpoint, transform in (
            ("crossref", "https://api.crossref.org/works/", crossref_record),
            ("datacite", "https://api.datacite.org/dois/", datacite_record),
        ):
            url = endpoint + urllib.parse.quote(doi, safe="")
            try:
                response = client.get_json(url)
                if response is None:
                    result["attempts"].append({"provider": provider, "status": "NOT_INDEXED"})
                    continue
                record = transform(response)
                differences, compared = compare(entry, record)
                result.update(status="REVIEW" if differences else "MATCHED_FIELDS", provider=provider,
                              record=record, differences=differences, compared_fields=compared,
                              unchecked_fields=[f for f in ("authors", "year", "venue", "volume", "number", "pages", "eid") if f not in compared])
                result["attempts"].append({"provider": provider, "status": "RECORD_RETURNED"})
                break
            except (LookupUnavailable, TypeError, KeyError, AttributeError, IndexError) as error:
                result["attempts"].append({"provider": provider, "status": "UNAVAILABLE", "error": str(error)})
        else:
            result["status"] = "UNAVAILABLE" if any(a["status"] == "UNAVAILABLE" for a in result["attempts"]) else "NOT_INDEXED"
    result["provider_complete"] = result["status"] != "UNAVAILABLE" and not any(
        attempt["status"] == "UNAVAILABLE" for attempt in result["attempts"])
    result["evidence"] = client.evidence[evidence_start:]
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bib", type=Path)
    parser.add_argument("--aux", type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--online", action="store_true", help="Allow DOI/title requests to public APIs.")
    mode.add_argument("--cache-only", action="store_true", help="Never send network requests.")
    parser.add_argument("--search-titles", action="store_true", help="For entries without DOI, return candidates only.")
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--cache-hours", type=float, default=24)
    parser.add_argument("--timeout", type=float, default=20)
    parser.add_argument("--email", help="Optional contact email sent in API User-Agent.")
    parser.add_argument("--limit", type=int, help="Positive limit for smoke tests; report is explicitly partial.")
    parser.add_argument("--strict", action="store_true", help="Nonzero unless every selected record has MATCHED_FIELDS.")
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.timeout <= 0 or args.cache_hours < 0 or (args.limit is not None and args.limit <= 0):
        parser.error("Timeout/limit must be positive; cache-hours must be nonnegative")
    try:
        _, selected, controls, missing = parse_inputs(args.bib, args.aux)
        if missing:
            raise ValueError("Undefined AUX citations: " + ", ".join(missing))
        if not selected or len({e['ID'] for e in selected}) != len(selected):
            raise ValueError("Empty selection or duplicate citation keys; run offline audit first.")
        if any((args.out_dir / f"metadata-check.{ext}").exists() for ext in ("json", "md")):
            raise FileExistsError("Report already exists; choose a new --out-dir.")
        report = report_base(args.bib, "online" if args.online else "cache-only")
        report.update(selected_entries=len(selected), checked_entries=len(selected[:args.limit]),
                      partial=args.limit is not None and len(selected) > args.limit)
        client = MetadataClient(args.cache_dir or args.out_dir / "evidence", online=args.online,
                                timeout=args.timeout, max_age=args.cache_hours * 3600, email=args.email)
        if args.online:
            print("Network: DOI identifiers sent to Crossref/DataCite; titles only with --search-titles. No manuscript upload.", file=sys.stderr)
        for entry in selected[:args.limit]:
            result = verify_entry(entry, client, args.search_titles)
            report["entries"].append(result)
            print(f"{entry['ID']}: {result['status']}", file=sys.stderr)
        report["provider_complete"] = all(r["provider_complete"] for r in report["entries"])
        write_report(report, args.out_dir, "metadata-check")
    except Exception as error:
        print(f"Metadata check could not complete: {error}", file=sys.stderr)
        return 2
    statuses = {r["status"] for r in report["entries"]}
    if "UNAVAILABLE" in statuses:
        return 2
    if statuses & {"REVIEW", "INVALID_DOI"} or (args.strict and (
            statuses != {"MATCHED_FIELDS"} or report["partial"] or not report["provider_complete"])):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
