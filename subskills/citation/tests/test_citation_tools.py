"""Deterministic tests; no network or external API credentials required."""

import io
import json
import sys
import tempfile
import unittest
import urllib.error
import urllib.parse
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_bibtex import audit, main as audit_main
from check_updates import check_entry, main as updates_main
from citation_common import authors, aux_keys, clean_doi, read_bib, report_base, write_report
from verify_metadata import (LookupUnavailable, MetadataClient, compare, crossref_record,
                             datacite_record, main as verify_main, verify_entry)


BIB = r'''
@string{venue = "IEEE Trans. Signal Process."}
@IEEEtranBSTCTL{control, CTLuse_url={no}}
@article{one,
  title = {A {General} Method}, author = {Doe, Jane and Roe, John},
  journal = venue, year = {2024}, month = jan,
  volume = {72}, number = {1}, pages = {12--20}, doi = {10.1234/example}
}
@misc{two, title = "A Study" # " of Signals", author = {{Research and Development Group}}, year = {2023}}
'''


def crossref(title="A General Method"):
    return {"status": "ok", "message": {"DOI": "10.1234/example", "title": [title],
            "author": [{"given": "Jane", "family": "Doe"}, {"given": "John", "family": "Roe"}],
            "container-title": ["IEEE Transactions on Signal Processing"],
            "published-print": {"date-parts": [[2024, 1]]},
            "published-online": {"date-parts": [[2023, 12]]},
            "volume": "72", "issue": "1", "page": "12-20", "type": "journal-article"}}


class FakeClient:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.evidence = []
        self.urls = []

    def get_json(self, url):
        self.urls.append(url)
        response = next(self.responses)
        if isinstance(response, Exception):
            raise response
        return response


class CitationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.bib = self.root / "references.bib"
        self.bib.write_text(BIB, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_macros_nested_braces_and_concatenation(self):
        entries, controls = read_bib(self.bib)
        self.assertEqual(len(entries), 2)
        self.assertEqual(len(controls), 1)
        self.assertEqual(entries[0]["month"], "January")
        self.assertEqual(entries[1]["title"], "A Study of Signals")

    def test_doi_url_normalization(self):
        self.assertEqual(clean_doi("https://doi.org/10.1234/ABC"), "10.1234/abc")

    def test_doi_url_percent_encoding(self):
        cases = {
            "https://doi.org/10.1234/abc%2Fdef": "10.1234/abc/def",
            "https://doi.org/10.1234%2Fabc": "10.1234/abc",
            "https://doi.org/10.1234/abc%25def": "10.1234/abc%def",
            "https://doi.org/10.1234/abc%23def": "10.1234/abc#def",
            "https://doi.org/10.1234/abc%252Fdef": "10.1234/abc%2fdef",
            " DOI: HTTPS://DX.DOI.ORG/10.1234/ABC%2fDEF ": "10.1234/abc/def",
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(clean_doi(raw), expected)
                self.assertEqual(clean_doi(expected), expected)

    def test_bare_doi_preserves_literal_percent(self):
        for raw in ("10.1234/abc%def", "10.1234/abc%2Fdef"):
            with self.subTest(raw=raw):
                self.assertEqual(clean_doi(raw), raw.lower())

    def test_doi_tex_escaped_characters(self):
        self.assertEqual(clean_doi(r"doi:10.1234/a\_b\%25c"), "10.1234/a_b%25c")
        self.assertEqual(clean_doi(r"https://doi.org/10.1234/a\%2Fb"), "10.1234/a/b")

    def test_encoded_doi_queries_complete_identifier(self):
        entries, _ = read_bib(self.bib)
        for suffix, expected in (("abc%2Fdef", "abc/def"), ("abc%25def", "abc%def"),
                                 ("abc%252Fdef", "abc%2fdef")):
            with self.subTest(suffix=suffix):
                entry = dict(entries[0], doi="https://doi.org/10.1234/" + suffix)
                response = crossref()
                response["message"]["DOI"] = "10.1234/" + expected
                client = FakeClient([response])
                result = verify_entry(entry, client)
                self.assertEqual(client.urls, ["https://api.crossref.org/works/" +
                                              urllib.parse.quote("10.1234/" + expected, safe="")])
                self.assertEqual(result["status"], "MATCHED_FIELDS")

    def test_percent_doi_mismatch_not_hidden(self):
        entry = {"doi": "https://doi.org/10.1234/abc%25def", "title": "Same"}
        record = {"doi": "10.1234/abc%xyz", "title": "Same"}
        differences, _ = compare(entry, record)
        self.assertIn("IDENTIFIER_MISMATCH", [d["reason"] for d in differences])

    def test_encoded_doi_does_not_create_false_duplicate(self):
        extra = '\n@misc{three, title={Different}, year={2024}, doi={10.1234/abc}}'
        self.bib.write_text(BIB.replace("10.1234/example", "https://doi.org/10.1234/abc%2Fdef")
                            + extra, encoding="utf-8")
        self.assertNotIn("DUPLICATE_DOI", [p["code"] for p in audit(self.bib)["issues"]])

    def test_corporate_author(self):
        people, truncated = authors("{Research and Development Group} and Doe, Jane")
        self.assertEqual(len(people), 2)
        self.assertIn("literal", people[0])
        self.assertFalse(truncated)

    def test_truncated_authors(self):
        self.assertTrue(authors("Doe, Jane and others")[1])

    def test_invalid_bib_fails_closed(self):
        self.bib.write_text(BIB + "\n@article{broken, title={oops}", encoding="utf-8")
        with self.assertRaises(Exception):
            read_bib(self.bib)

    def test_unknown_macro_fails(self):
        self.bib.write_text("@article{x, title=undefinedmacro}", encoding="utf-8")
        with self.assertRaises(Exception):
            read_bib(self.bib)

    def test_duplicate_keys_are_errors(self):
        self.bib.write_text(BIB + "\n@misc{one, title={Duplicate}, year={2024}}", encoding="utf-8")
        self.assertIn("DUPLICATE_KEY", [p["code"] for p in audit(self.bib)["issues"]])

    def test_duplicate_doi(self):
        self.bib.write_text(BIB + "\n@misc{three, title={Different}, year={2024}, doi={https://doi.org/10.1234/EXAMPLE}}", encoding="utf-8")
        self.assertIn("DUPLICATE_DOI", [p["code"] for p in audit(self.bib)["issues"]])

    def test_aux_selects_actual_keys_and_reports_missing(self):
        aux = self.root / "main.aux"
        aux.write_text("\\citation{one,missing,control}\n%\\citation{two}", encoding="utf-8")
        report = audit(self.bib, aux)
        self.assertEqual(report["selected_entries"], 1)
        self.assertIn("UNDEFINED_CITATION", [p["code"] for p in report["issues"]])

    def test_aux_children_and_biblatex(self):
        aux = self.root / "main.aux"
        aux.write_text("\\@input{child.aux}", encoding="utf-8")
        (self.root / "child.aux").write_text("\\abx@aux@cite{0}{two}\n\\@input{main.aux}", encoding="utf-8")
        self.assertEqual(aux_keys(aux), {"two"})

    def test_aux_wildcard(self):
        aux = self.root / "main.aux"
        aux.write_text("\\citation{*}", encoding="utf-8")
        self.assertEqual(audit(self.bib, aux)["selected_entries"], 2)

    def test_aux_outside_root_rejected(self):
        aux = self.root / "main.aux"
        aux.write_text("\\@input{../other.aux}", encoding="utf-8")
        with self.assertRaises(ValueError):
            aux_keys(aux)

    def test_no_default_count_quota(self):
        self.assertNotIn("COUNT_BELOW_REQUEST", [p["code"] for p in audit(self.bib)["issues"]])
        self.assertIn("COUNT_BELOW_REQUEST", [p["code"] for p in audit(self.bib, min_count=3)["issues"]])

    def test_input_not_modified(self):
        before = self.bib.read_bytes()
        self.assertEqual(audit_main([str(self.bib), "--out-dir", str(self.root / "report")]), 0)
        self.assertEqual(before, self.bib.read_bytes())

    def test_report_cannot_overwrite_existing(self):
        report = report_base(self.bib, "offline")
        write_report(report, self.root / "report", "test")
        with self.assertRaises(FileExistsError):
            write_report(report, self.root / "report", "test")

    def test_matched_fields_not_blanket_verified(self):
        entry = read_bib(self.bib)[0][0]
        result = verify_entry(entry, FakeClient([crossref()]))
        self.assertEqual(result["status"], "MATCHED_FIELDS")
        self.assertIn("eid", result["unchecked_fields"])

    def test_wrong_doi_title_requires_review(self):
        entry = read_bib(self.bib)[0][0]
        result = verify_entry(entry, FakeClient([crossref("An unrelated paper")]))
        self.assertEqual(result["status"], "REVIEW")
        self.assertEqual(result["differences"][0]["field"], "title")

    def test_same_initial_different_full_given_name(self):
        entry = read_bib(self.bib)[0][0]
        entry["author"] = "Doe, Janet and Roe, John"
        differences, _ = compare(entry, crossref_record(crossref()))
        self.assertTrue(any(d["reason"] == "AUTHOR_GIVEN_NAME_DIFFERENCE" for d in differences))

    def test_initials_accepted(self):
        entry = read_bib(self.bib)[0][0]
        entry["author"] = "Doe, J. and Roe, J."
        self.assertEqual(compare(entry, crossref_record(crossref()))[0], [])

    def test_print_online_year_distinguished(self):
        entry = read_bib(self.bib)[0][0]
        entry["year"] = "2023"
        self.assertIn("DATE_VARIANT", [d["reason"] for d in compare(entry, crossref_record(crossref()))[0]])

    def test_authors_order_is_checked(self):
        entry = read_bib(self.bib)[0][0]
        entry["author"] = "Roe, John and Doe, Jane"
        self.assertTrue(compare(entry, crossref_record(crossref()))[0])

    def test_pages_compared(self):
        entry = read_bib(self.bib)[0][0]
        entry["pages"] = "12--21"
        self.assertIn("pages", [d["field"] for d in compare(entry, crossref_record(crossref()))[0]])

    def test_datacite_fallback(self):
        entry = read_bib(self.bib)[0][0]
        payload = {"data": {"attributes": {"doi": "10.1234/example", "titles": [{"title": "A General Method"}], "publicationYear": 2024}}}
        result = verify_entry(entry, FakeClient([None, payload]))
        self.assertEqual(result["provider"], "datacite")
        self.assertIn("authors", result["unchecked_fields"])

    def test_missing_in_both_not_fabricated(self):
        entry = read_bib(self.bib)[0][0]
        self.assertEqual(verify_entry(entry, FakeClient([None, None]))["status"], "NOT_INDEXED")

    def test_network_failure_not_not_found(self):
        entry = read_bib(self.bib)[0][0]
        result = verify_entry(entry, FakeClient([LookupUnavailable("timeout"), None]))
        self.assertEqual(result["status"], "UNAVAILABLE")

    def test_wrong_response_schema_unavailable(self):
        entry = read_bib(self.bib)[0][0]
        self.assertEqual(verify_entry(entry, FakeClient([{}, {}]))["status"], "UNAVAILABLE")

    def test_no_doi_does_not_query_by_default(self):
        client = FakeClient([])
        self.assertEqual(verify_entry(read_bib(self.bib)[0][1], client)["status"], "NO_DOI")
        self.assertEqual(client.urls, [])

    def test_title_search_is_candidate_only(self):
        entry = read_bib(self.bib)[0][1]
        client = FakeClient([{"message": {"items": [{"DOI": "10.1234/guess", "title": [entry["title"]]}]}}])
        self.assertEqual(verify_entry(entry, client, True)["status"], "TITLE_CANDIDATES")

    def test_offline_cache_miss_never_networks(self):
        client = MetadataClient(self.root / "cache")
        with patch("urllib.request.urlopen") as request:
            with self.assertRaises(LookupUnavailable):
                client.get_json("https://api.crossref.org/works/10.1234%2Fexample")
            request.assert_not_called()

    def test_429_retries_then_unavailable(self):
        client = MetadataClient(self.root / "cache", online=True, retries=1, interval=0)
        error = urllib.error.HTTPError("https://api.crossref.org", 429, "rate limit", {}, None)
        with patch("urllib.request.urlopen", side_effect=error) as request, patch("time.sleep"):
            with self.assertRaises(LookupUnavailable):
                client.get_json("https://api.crossref.org/works/10.1234%2Fexample")
            self.assertEqual(request.call_count, 2)

    def test_404_cached_and_reused(self):
        url = "https://api.crossref.org/works/10.1234%2Fexample"
        online = MetadataClient(self.root / "cache", online=True, interval=0)
        error = urllib.error.HTTPError(url, 404, "missing", {}, None)
        with patch("urllib.request.urlopen", side_effect=error):
            self.assertIsNone(online.get_json(url))
        with patch("urllib.request.urlopen") as request:
            self.assertIsNone(MetadataClient(self.root / "cache").get_json(url))
            request.assert_not_called()

    def test_stale_cache_not_accepted(self):
        url = "https://api.crossref.org/works/10.1234%2Fexample"
        client = MetadataClient(self.root / "cache", online=True, interval=0)
        error = urllib.error.HTTPError(url, 404, "missing", {}, None)
        with patch("urllib.request.urlopen", side_effect=error):
            client.get_json(url)
        with self.assertRaises(LookupUnavailable):
            MetadataClient(self.root / "cache", max_age=0).get_json(url)

    def test_no_arbitrary_endpoint(self):
        with self.assertRaises(LookupUnavailable):
            MetadataClient(self.root / "cache", online=True).get_json("https://example.org/anything")

    def test_cache_only_cli_incomplete_exit(self):
        with patch("urllib.request.urlopen") as request:
            code = verify_main([str(self.bib), "--cache-only", "--out-dir", str(self.root / "out")])
            self.assertEqual(code, 2)
            request.assert_not_called()
        report = json.loads((self.root / "out/metadata-check.json").read_text(encoding="utf-8"))
        self.assertEqual(report["entries"][0]["status"], "UNAVAILABLE")

    def test_cli_requires_explicit_network_mode(self):
        with self.assertRaises(SystemExit), patch("sys.stderr", new=io.StringIO()):
            verify_main([str(self.bib), "--out-dir", str(self.root / "out")])

    def test_limit_cli_reports_scope_in_markdown(self):
        self.bib.write_text("\n".join(
            "@misc{item%d, title={Example %d}, year={2024}, doi={10.1234/item%d}}" % (i, i, i)
            for i in range(50)), encoding="utf-8")
        for main, stem in ((verify_main, "metadata-check"), (updates_main, "publication-updates")):
            with self.subTest(stem=stem):
                out = self.root / stem
                with patch("urllib.request.urlopen") as request, patch("sys.stderr", new=io.StringIO()):
                    self.assertEqual(main([str(self.bib), "--cache-only", "--limit", "2",
                                           "--out-dir", str(out)]), 2)
                    request.assert_not_called()
                data = json.loads((out / f"{stem}.json").read_text(encoding="utf-8"))
                text = (out / f"{stem}.md").read_text(encoding="utf-8")
                self.assertEqual((data["checked_entries"], data["selected_entries"], data["partial"]), (2, 50, True))
                header = text.split("## Findings")[0]
                for expected in ("**2 / 50**", "**PARTIAL**", "INCOMPLETE", "UNAVAILABLE: 2", "Selection: all"):
                    self.assertIn(expected, header)

    def test_report_full_coverage_with_source_failure(self):
        for record in ({"status": "UNAVAILABLE"}, {"status": "PARTIAL", "complete": False},
                       {"status": "MATCHED_FIELDS", "provider_complete": False}):
            with self.subTest(record=record):
                report = report_base(self.bib, "online")
                report.update(selected_entries=1, checked_entries=1, partial=False,
                              entries=[dict(record, key="one")])
                stem = record["status"]
                write_report(report, self.root / "reports", stem)
                text = (self.root / "reports" / f"{stem}.md").read_text(encoding="utf-8")
                self.assertIn("**FULL**", text)
                self.assertIn("INCOMPLETE", text)

    def test_report_complete_processing_and_unverified_statuses(self):
        report = report_base(self.bib, "online")
        report.update(selected_entries=2, checked_entries=2, partial=False,
                      entries=[{"key": "one", "status": "MATCHED_FIELDS"},
                               {"key": "two", "status": "NO_DOI"}])
        write_report(report, self.root, "complete")
        text = (self.root / "complete.md").read_text(encoding="utf-8")
        for expected in ("**2 / 2**", "**FULL**", "PROCESSING_FINISHED", "NO_DOI: 1"):
            self.assertIn(expected, text)

    def test_offline_report_aux_scope_and_empty_selection(self):
        aux = self.root / "main.aux"
        for citation, count in (("one", 1), ("missing", 0)):
            with self.subTest(citation=citation):
                aux.write_text("\\citation{" + citation + "}", encoding="utf-8")
                report = audit(self.bib, aux)
                write_report(report, self.root, citation)
                text = (self.root / f"{citation}.md").read_text(encoding="utf-8")
                for expected in ("Selection: aux", "Bibliography entries: 2", f"**{count} / {count}**", "LOCAL_ONLY"):
                    self.assertIn(expected, text)
                self.assertIn("**FULL**" if count else "**EMPTY**", text)

    def test_retraction_notice_direction(self):
        record = {"DOI": "10.1234/notice", "title": ["Retraction notice"],
                  "update-to": [{"DOI": "10.1234/example", "type": "retraction", "source": "publisher"}]}
        result = check_entry(read_bib(self.bib)[0][0], FakeClient([{"message": {"items": [record], "total-results": 1}}]))
        self.assertEqual(result["status"], "UPDATE_NOTICE")
        self.assertEqual(result["notices"][0]["notice_doi"], "10.1234/notice")

    def test_unrelated_update_is_not_accepted(self):
        record = {"DOI": "10.1234/notice", "update-to": [{"DOI": "10.1234/other", "type": "retraction"}]}
        result = check_entry(read_bib(self.bib)[0][0], FakeClient([{"message": {"items": [record], "total-results": 1}}]))
        self.assertEqual(result["status"], "UNAVAILABLE")

    def test_empty_updates_not_blanket_safe(self):
        result = check_entry(read_bib(self.bib)[0][0], FakeClient([{"message": {"items": [], "total-results": 0}}]))
        self.assertEqual(result["status"], "NO_UPDATE_FOUND")

    def test_update_pagination_is_explicit(self):
        result = check_entry(read_bib(self.bib)[0][0], FakeClient([{"message": {"items": [], "total-results": 101}}]))
        self.assertEqual(result["status"], "PARTIAL")
        self.assertFalse(result["complete"])

    def test_update_outage_is_not_no_update(self):
        result = check_entry(read_bib(self.bib)[0][0], FakeClient([LookupUnavailable("timeout")]))
        self.assertEqual(result["status"], "UNAVAILABLE")

    def test_metadata_identifier_conflict_is_preserved(self):
        payload = crossref()
        payload["message"]["DOI"] = "10.1234/different"
        result = verify_entry(read_bib(self.bib)[0][0], FakeClient([payload]))
        self.assertEqual(result["status"], "REVIEW")
        self.assertIn("IDENTIFIER_MISMATCH", [d["reason"] for d in result["differences"]])

    def test_provider_failure_survives_successful_fallback(self):
        payload = {"data": {"attributes": {"doi": "10.1234/example", "titles": [{"title": "A General Method"}], "publicationYear": 2024}}}
        result = verify_entry(read_bib(self.bib)[0][0], FakeClient([LookupUnavailable("rate limited"), payload]))
        self.assertEqual(result["status"], "MATCHED_FIELDS")
        self.assertFalse(result["provider_complete"])

    def test_empty_title_candidate_response_stays_unavailable(self):
        result = verify_entry(read_bib(self.bib)[0][1], FakeClient([{"message": {"items": [None]}}]), True)
        self.assertEqual(result["status"], "UNAVAILABLE")


if __name__ == "__main__":
    unittest.main()
