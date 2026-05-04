"""
Smoke test: run full pipeline and check output files exist and have expected content.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def test_full_pipeline_produces_output():
    """Run pipeline (fixture data); assert HTML and JSON exist and are valid."""
    from run import load_config, load_taxonomy, main

    config = load_config()
    taxonomy = load_taxonomy(config)
    out_dir = Path(config.get("output", {}).get("dir", "data/output"))
    html_name = config.get("output", {}).get("report_html", "manual_analysis_report.html")
    json_name = config.get("output", {}).get("intermediate_json", "comparison_results.json")
    root = Path(__file__).resolve().parent.parent

    exit_code = main()
    assert exit_code == 0

    html_path = root / out_dir / html_name
    json_path = root / out_dir / json_name
    assert html_path.exists(), f"Report not found: {html_path}"
    assert json_path.exists(), f"Results JSON not found: {json_path}"

    html_content = html_path.read_text(encoding="utf-8")
    assert "tab-contents" in html_content
    assert "comparison-table" in html_content
    assert "document-text-view" in html_content or "document-text-content" in html_content
    assert "showTab(" in html_content

    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert "documents" in data
    assert "comparison_by_doc" in data
    assert len(data["documents"]) >= 1
    assert len(data["comparison_by_doc"]) >= 1


def test_report_only_from_json():
    """Regenerate report from existing JSON; assert HTML updated."""
    from run_report_only import load_config, main as report_main

    config = load_config()
    out_dir = Path(config.get("output", {}).get("dir", "data/output"))
    json_name = config.get("output", {}).get("intermediate_json", "comparison_results.json")
    root = Path(__file__).resolve().parent.parent
    json_path = root / out_dir / json_name

    if not json_path.exists():
        # Run full pipeline first so we have JSON
        from run import main as full_main
        full_main()
    assert json_path.exists(), "Need comparison_results.json (run full pipeline first)"

    # run_report_only reads sys.argv[1] for JSON path
    old_argv = sys.argv
    sys.argv = ["run_report_only.py", str(json_path)]
    try:
        exit_code = report_main()
    finally:
        sys.argv = old_argv

    assert exit_code == 0
    html_path = root / out_dir / config.get("output", {}).get("report_html", "manual_analysis_report.html")
    assert html_path.exists()
    assert "tab-contents" in html_path.read_text(encoding="utf-8")
