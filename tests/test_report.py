"""
Test report module: given comparison input, produces valid HTML with expected structure.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from report import run as report_run
from report import _normalize_segment_for_search, _get_accepted_segments


def test_report_produces_html():
    """Report run writes HTML file containing tabs, table, document text view, glossary."""
    config = {"output": {"dir": "data/output", "report_html": "test_report_output.html", "intermediate_json": "comparison_results.json"}}
    taxonomy = {
        "content_categories": [{"id": "Actors", "label_en": "Actors", "colour": "#3b82f6"}],
        "framing_strategies": [{"id": "Generic", "label_en": "Generic", "colour": "#666"}],
    }
    documents = [
        {"document_id": "d1", "display_name": "doc1.txt"},
        {"document_id": "d2", "display_name": "doc2.txt"},
    ]
    comparison_by_doc = {
        "d1": {
            "aligned_rows": [
                {"section": 1, "entry_eng": "Test", "entry_rus": "", "llm_category": "Actors", "llm_framing": "Generic", "human_category": "Actors", "human_framing": "Generic", "context": "Test", "category_match": True, "framing_match": True, "both_match": True},
            ],
            "category_accuracy_pct": 100.0,
            "framing_accuracy_pct": 100.0,
            "both_match_pct": 100.0,
        },
        "d2": {
            "aligned_rows": [],
            "category_accuracy_pct": 0.0,
            "framing_accuracy_pct": 0.0,
            "both_match_pct": 0.0,
        },
    }

    out_path = report_run(comparison_by_doc, documents, taxonomy, config)

    assert out_path.exists()
    html = out_path.read_text(encoding="utf-8")
    assert "tab-contents" in html
    assert "tab-d1" in html
    assert "tab-d2" in html
    assert "tab-glossary" in html
    assert "comparison-table" in html
    assert "document-text-view" in html or "document-text-content" in html
    assert "buildDocumentTextView" in html or "doc-text-" in html
    assert "100.0%" in html
    assert "Actors" in html
    assert "Glossary" in html
    assert "collapsible-section" in html
    assert "document-text-controls-sticky" in html
    assert "Accuracy stats" in html and "Document text view" in html and "Comparison table" in html
    assert "sidebar" in html and "tab-home" in html and "homepage-placeholder" in html

    # Clean up test output
    try:
        out_path.unlink()
    except Exception:
        pass


def test_normalize_segment_for_search():
    """Segment normalization collapses whitespace for tolerant search."""
    assert _normalize_segment_for_search("word1  word2") == "word1 word2"
    assert _normalize_segment_for_search("word1\nword2") == "word1 word2"
    assert _normalize_segment_for_search("  word  ") == "word"
    assert _normalize_segment_for_search("") == ""
    assert _normalize_segment_for_search("single") == "single"


def test_get_accepted_segments_whitespace_tolerant():
    """Segment search tolerates different whitespace (normalization)."""
    aligned = [{"entry_eng": "word1 word2", "llm_category": "A", "llm_framing": "X"}]
    full_text = "Before word1\nword2 after"
    accepted = _get_accepted_segments(full_text, aligned, "entry_eng")
    assert len(accepted) == 1
    assert accepted[0][2] == "word1\nword2"


def test_get_accepted_segments_shorter_wins():
    """Shorter overlapping segments win (substring overlap fix)."""
    aligned = [
        {"entry_eng": "delegation arrived", "llm_category": "A", "llm_framing": "Generic"},
        {"entry_eng": "arrived", "llm_category": "A", "llm_framing": "Action-Focused"},
    ]
    full_text = "The delegation arrived at the hall."
    accepted = _get_accepted_segments(full_text, aligned, "entry_eng")
    texts = [a[2] for a in accepted]
    assert "arrived" in texts
    assert "delegation arrived" not in texts
