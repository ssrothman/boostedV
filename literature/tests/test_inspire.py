import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import inspire  # noqa: E402

HEAD = (
    "# Candidate corpus\n\n"
    "| recid | arXiv | short title | found-via | tags | verdict | reason | status |\n"
    "|---|---|---|---|---|---|---|---|\n"
)


def test_record_row_cleans_pipes_and_takes_first_title():
    meta = {"control_number": 7, "arxiv_eprints": [{"value": "2401.00001"}],
            "titles": [{"title": "A | B\n  title"}, {"title": "other"}]}
    assert inspire.record_row(meta, "ref:x") == {
        "recid": "7", "arxiv": "2401.00001", "title": "A / B title", "via": "ref:x"}


def test_record_row_without_arxiv():
    assert inspire.record_row({"control_number": 8, "titles": [{"title": "T"}]}, "v")["arxiv"] == ""


def test_unlinked_row_uses_misc_text():
    ref = {"reference": {"misc": ["Advances in Jet", "Substructure"]}}
    assert inspire.unlinked_row(ref, "ref:y") == {
        "recid": "", "arxiv": "", "title": "Advances in Jet Substructure", "via": "ref:y"}


def test_key_priority():
    assert inspire.key({"recid": "5", "arxiv": "a", "title": "t"}) == "5"
    assert inspire.key({"recid": "", "arxiv": "a", "title": "t"}) == "arXiv:a"
    assert inspire.key({"recid": "", "arxiv": "", "title": "T"}) == "title:t"


def test_merge_dedups_and_records_every_source():
    rows1 = [{"recid": "1", "arxiv": "a1", "title": "One", "via": "ref:A"},
             {"recid": "2", "arxiv": "", "title": "Two", "via": "ref:A"},
             {"recid": "", "arxiv": "", "title": "Book", "via": "ref:A"}]
    text, n = inspire.merge(HEAD, rows1)
    assert n == 3
    rows2 = [{"recid": "1", "arxiv": "a1", "title": "One", "via": "ref:B"},
             {"recid": "1", "arxiv": "a1", "title": "One", "via": "ref:B"},
             {"recid": "", "arxiv": "", "title": "Book", "via": "ref:B"},
             {"recid": "3", "arxiv": "a3", "title": "Three", "via": "cites:A"}]
    text, n = inspire.merge(text, rows2)
    assert n == 1
    assert text == HEAD + (
        "| 1 | a1 | One | ref:A; ref:B |  |  |  | new |\n"
        "| 2 |  | Two | ref:A |  |  |  | new |\n"
        "|  |  | Book | ref:A; ref:B |  |  |  | new |\n"
        "| 3 | a3 | Three | cites:A |  |  |  | new |\n")


def test_merge_preserves_triaged_cells():
    text = HEAD + "| 1 | a1 | One | ref:A | Q1 | deep | has limit | triaged |\n"
    out, n = inspire.merge(text, [{"recid": "1", "arxiv": "a1", "title": "One", "via": "cites:B"}])
    assert n == 0
    assert out.endswith("| 1 | a1 | One | ref:A; cites:B | Q1 | deep | has limit | triaged |\n")
