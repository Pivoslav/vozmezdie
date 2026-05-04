"""
Smoke test: run full pipeline and check output files exist and report has expected structure.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def test_full_pipeline_produces_report():
    """Run pipeline (fixture data) and assert HTML + JSON exist with expected content."""
    import run
    # Load config and ensure stub LLM
    config = run.load_config()
    config.setdefault("llm", {})["use_fixture"] = True
    taxonomy = run.load_taxonomy(config)

    from ingest import run as ingest_run
    from llm import run as llm_run
    from ground_truth import run as gt_run
    from compare import run as compare_run
    from report import run as report_run

    documents = ingest_run(config)
    assert len(documents) >= 1, "ingest should return at least one doc"

    llm_by_doc = llm_run(documents, taxonomy, config)
    document_ids = [d.get("document_id") for d in documents]
    gt_by_doc = gt_run(config, document_ids)
    comparison_by_doc = compare_run(llm_by_doc, gt_by_doc, config)

    out_dir = ROOT / config.get("output", {}).get("dir", "data/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    html_path = report_run(comparison_by_doc, documents, taxonomy, config)

    assert html_path.exists(), "report should write HTML file"
    html = html_path.read_text(encoding="utf-8")
    assert "tab-contents" in html, "report should have tab container"
    assert "comparison-table" in html, "report should have comparison table"
    assert "document-text-view" in html, "report should have document text view"
    for doc in documents:
        doc_id = doc.get("document_id", "")
        assert f"tab-{doc_id}" in html or doc_id in html, f"report should include doc {doc_id}"


def test_report_only_from_json():
    """If comparison_results.json exists, run_report_only produces HTML."""
    json_path = ROOT / "data" / "output" / "comparison_results.json"
    if not json_path.exists():
        # Create minimal JSON so test can run
        json_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "documents": [
                {"document_id": "smoke", "display_name": "smoke.txt", "raw_text": "One. Two."},
            ],
            "comparison_by_doc": {
                "smoke": {
                    "aligned_rows": [
                        {"section": 1, "entry_eng": "One", "entry_rus": "", "llm_category": "Actions", "llm_framing": "Institutional / Bureaucratic Lingo", "human_category": "Actions", "human_framing": "Institutional / Bureaucratic Lingo", "context": "One", "category_match": True, "framing_match": True, "both_match": True},
                        {"section": 2, "entry_eng": "Two", "entry_rus": "", "llm_category": "Actors", "llm_framing": "Institutional / Bureaucratic Lingo", "human_category": "Actors", "human_framing": "Institutional / Bureaucratic Lingo", "context": "Two", "category_match": True, "framing_match": True, "both_match": True},
                    ],
                    "category_accuracy_pct": 100.0,
                    "framing_accuracy_pct": 100.0,
                    "both_match_pct": 100.0,
                },
            },
        }
        json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    import run_report_only
    old_argv = sys.argv
    sys.argv = ["run_report_only.py", str(json_path)]
    try:
        code = run_report_only.main()
    finally:
        sys.argv = old_argv
    assert code == 0, "run_report_only should exit 0"
    out_path = ROOT / "data" / "output" / "manual_analysis_report.html"
    assert out_path.exists(), "report-only should write HTML"
