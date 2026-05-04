"""
Test ground_truth module: fixture shape when no CSV dir; row shape matches LLM contract.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ground_truth import run as gt_run


def test_ground_truth_returns_fixture_when_no_dir():
    config = {"ground_truth": {"path": "data/ground_truth_nonexistent", "pattern": "*.csv"}}
    result = gt_run(config, ["doc1", "doc2"])
    assert "doc1" in result
    assert "doc2" in result
    for doc_id, rows in result.items():
        assert isinstance(rows, list)
        assert len(rows) >= 1
        for r in rows:
            assert "section" in r
            assert "entry_eng" in r
            assert "entry_rus" in r
            assert "content_category" in r
            assert "framing" in r
            assert "context" in r


def test_ground_truth_row_shape_matches_llm_contract():
    """Same keys as LLM extraction output for compare module."""
    config = {}
    result = gt_run(config, ["doc1"])
    rows = result["doc1"]
    assert len(rows) >= 1
    row = rows[0]
    required = {"section", "entry_eng", "entry_rus", "content_category", "framing", "context"}
    assert required.issubset(row.keys()), f"Missing keys: {required - row.keys()}"
