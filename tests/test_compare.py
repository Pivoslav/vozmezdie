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
        {"section": 1, "entry_eng": "A", "entry_rus": "", "content_category": "Actors", "framing": "Generic / Neutral", "context": "A"},
        {"section": 2, "entry_eng": "B", "entry_rus": "", "content_category": "Actions", "framing": "Institutional", "context": "B"},
    ]
    gt_rows = [
        {"section": 1, "entry_eng": "A", "entry_rus": "", "content_category": "Actors", "framing": "Generic / Neutral", "context": "A"},
        {"section": 2, "entry_eng": "B", "entry_rus": "", "content_category": "Actions", "framing": "Institutional", "context": "B"},
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
        {"section": 1, "entry_eng": "A", "entry_rus": "", "content_category": "Actors", "framing": "Generic", "context": "A"},
        {"section": 2, "entry_eng": "B", "entry_rus": "", "content_category": "Places", "framing": "Institutional", "context": "B"},
    ]
    gt_rows = [
        {"section": 1, "entry_eng": "A", "entry_rus": "", "content_category": "Actors", "framing": "Generic", "context": "A"},
        {"section": 2, "entry_eng": "B", "entry_rus": "", "content_category": "Actions", "framing": "Generic", "context": "B"},
    ]
    result = compare_run({"doc1": llm_rows}, {"doc1": gt_rows})
    r = result["doc1"]
    assert r["category_accuracy_pct"] == 50.0  # first match, second mismatch
    assert r["framing_accuracy_pct"] == 50.0
    assert r["both_match_pct"] == 50.0
    assert r["aligned_rows"][0]["category_match"] is True
    assert r["aligned_rows"][1]["category_match"] is False


def test_compare_length_mismatch():
    llm_rows = [{"section": 1, "entry_eng": "A", "entry_rus": "", "content_category": "Actors", "framing": "G", "context": "A"}]
    gt_rows = [
        {"section": 1, "entry_eng": "A", "entry_rus": "", "content_category": "Actors", "framing": "G", "context": "A"},
        {"section": 2, "entry_eng": "B", "entry_rus": "", "content_category": "Actions", "framing": "G", "context": "B"},
    ]
    result = compare_run({"doc1": llm_rows}, {"doc1": gt_rows})
    r = result["doc1"]
    assert r["n_human"] == 2 and r["n_llm"] == 1 and r["n_matched"] == 1
    assert len(r["aligned_rows"]) == 1
    assert r["aligned_rows"][0]["both_match"] is True
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
