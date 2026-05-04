"""
Test compare module: aligned rows and accuracy percentages.
"""
import sys
from pathlib import Path

# Allow importing framework modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from compare import run as compare_run


def test_compare_full_match():
    llm_rows = [
        {"section": 1, "entry_eng": "A", "entry_rus": "", "content_category": "Actors", "framing": "Institutional / Bureaucratic Lingo", "context": "A"},
        {"section": 2, "entry_eng": "B", "entry_rus": "", "content_category": "Actions", "framing": "Institutional / Bureaucratic Lingo", "context": "B"},
    ]
    gt_rows = [
        {"section": 1, "entry_eng": "A", "entry_rus": "", "content_category": "Actors", "framing": "Institutional / Bureaucratic Lingo", "context": "A"},
        {"section": 2, "entry_eng": "B", "entry_rus": "", "content_category": "Actions", "framing": "Institutional / Bureaucratic Lingo", "context": "B"},
    ]
    result = compare_run({"doc1": llm_rows}, {"doc1": gt_rows})
    assert "doc1" in result
    r = result["doc1"]
    assert r["category_accuracy_pct"] == 100.0
    assert r["framing_accuracy_pct"] == 100.0
    assert r["both_match_pct"] == 100.0
    assert len(r["aligned_rows"]) == 2
    assert all(row["category_match"] and row["framing_match"] for row in r["aligned_rows"])


def test_compare_mismatch():
    llm_rows = [
        {"section": 1, "entry_eng": "A", "entry_rus": "", "content_category": "Actors", "framing": "Institutional / Bureaucratic Lingo", "context": "A"},
        {"section": 2, "entry_eng": "B", "entry_rus": "", "content_category": "Places", "framing": "Institutional / Bureaucratic Lingo", "context": "B"},
    ]
    gt_rows = [
        {"section": 1, "entry_eng": "A", "entry_rus": "", "content_category": "Actors", "framing": "Institutional / Bureaucratic Lingo", "context": "A"},
        {"section": 2, "entry_eng": "B", "entry_rus": "", "content_category": "Actions", "framing": "Institutional / Bureaucratic Lingo", "context": "B"},
    ]
    result = compare_run({"doc1": llm_rows}, {"doc1": gt_rows})
    r = result["doc1"]
    assert r["category_accuracy_pct"] == 50.0  # first match, second mismatch
    assert r["framing_accuracy_pct"] == 100.0
    assert r["both_match_pct"] == 50.0
    assert r["aligned_rows"][0]["category_match"] is True
    assert r["aligned_rows"][1]["category_match"] is False


def test_compare_normalizes_retired_category_labels():
    """Aligned rows store canonical category names, not retired sheet labels."""
    llm_rows = [
        {"section": 1, "entry_eng": "A", "content_category": "Information", "framing": "Institutional / Bureaucratic Lingo", "context": ""},
    ]
    gt_rows = [
        {"section": 1, "entry_eng": "A", "content_category": "Documents", "framing": "Institutional / Bureaucratic Lingo", "context": ""},
    ]
    result = compare_run({"doc1": llm_rows}, {"doc1": gt_rows})
    row = result["doc1"]["aligned_rows"][0]
    assert row["llm_category"] == "Documents"
    assert row["human_category"] == "Documents"
    assert row["llm_framing"] == "Institutional / Bureaucratic Lingo"
    assert row["category_match"] is True
    assert row["framing_match"] is True


def test_compare_lists_every_gt_row_content_mode():
    """Content alignment emits one row per human segment; unmatched GT keeps empty LLM fields."""
    llm_rows = [
        {"section": 1, "entry_eng": "A", "content_category": "Actors", "framing": "Generic / Neutral Language", "context": ""},
        {"section": 2, "entry_eng": "B", "content_category": "Actions", "framing": "Action-Focused Language", "context": ""},
    ]
    gt_rows = [
        {"section": 1, "entry_eng": "A", "content_category": "Actors", "framing": "Ideological Framing (Discrediting)", "context": ""},
        {"section": 2, "entry_eng": "B", "content_category": "Actions", "framing": "Action-Focused Language", "context": ""},
        {"section": 3, "entry_eng": "C", "content_category": "Places", "framing": "Generic / Neutral Language", "context": ""},
    ]
    result = compare_run({"doc1": llm_rows}, {"doc1": gt_rows})
    r = result["doc1"]
    assert len(r["aligned_rows"]) == 3
    assert r["n_matched"] == 2
    assert r["aligned_rows"][2]["entry_eng"] == "C"
    assert r["aligned_rows"][2]["paired_with_llm"] is False
    assert r["aligned_rows"][2]["llm_category"] == ""


def test_scrub_retired_multiword_category_labels():
    from config.taxonomy_categories import scrub_retired_multiword_category_labels

    text = "Cross-reference Context and Concepts when labeling narrative framing."
    out = scrub_retired_multiword_category_labels(text)
    assert "Context and Concepts" not in out
    assert "Documents" in out


def test_compare_length_mismatch():
    llm_rows = [{"section": 1, "entry_eng": "A", "entry_rus": "", "content_category": "Actors", "framing": "G", "context": "A"}]
    gt_rows = [
        {"section": 1, "entry_eng": "A", "entry_rus": "", "content_category": "Actors", "framing": "G", "context": "A"},
        {"section": 2, "entry_eng": "B", "entry_rus": "", "content_category": "Actions", "framing": "G", "context": "B"},
    ]
    result = compare_run({"doc1": llm_rows}, {"doc1": gt_rows})
    r = result["doc1"]
    assert r["n_human"] == 2 and r["n_llm"] == 1 and r["n_matched"] == 1
    assert len(r["aligned_rows"]) == 2
    assert r["aligned_rows"][0]["both_match"] is True
    assert r["aligned_rows"][1]["paired_with_llm"] is False
    assert r["category_accuracy_pct"] == 100.0


def test_compare_index_mode():
    """With match_by=index, alignment is by row index (legacy)."""
    llm_rows = [{"section": 1, "entry_eng": "A", "entry_rus": "", "content_category": "Actors", "framing": "G", "context": "A"}]
    gt_rows = [
        {"section": 1, "entry_eng": "A", "entry_rus": "", "content_category": "Actors", "framing": "G", "context": "A"},
        {"section": 2, "entry_eng": "B", "entry_rus": "", "content_category": "Actions", "framing": "G", "context": "B"},
    ]
    result = compare_run({"doc1": llm_rows}, {"doc1": gt_rows}, config={"compare": {"match_by": "index"}})
    r = result["doc1"]
    assert len(r["aligned_rows"]) == 2
    assert r["aligned_rows"][0]["both_match"] is True
    assert r["aligned_rows"][1]["category_match"] is False


if __name__ == "__main__":
    test_compare_full_match()
    test_compare_mismatch()
    test_compare_length_mismatch()
    print("All compare tests passed.")
