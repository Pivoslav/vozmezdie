#!/usr/bin/env python3
"""
Vozmezdie framework: thin orchestrator.
Runs pipeline: config -> ingest -> llm -> ground_truth -> compare -> report.
Uses config from config/pipeline_config.example.json (or PIPELINE_CONFIG env) and
taxonomy from config/taxonomy.json (or path in config).
"""
import json
import sys
from pathlib import Path
from typing import Optional

# Project root
ROOT = Path(__file__).resolve().parent


def load_config() -> dict:
    import os

    rel = os.environ.get("PIPELINE_CONFIG", "config/pipeline_config.example.json")
    config_path = Path(rel)
    if not config_path.is_absolute():
        config_path = ROOT / config_path
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_taxonomy(config: dict) -> dict:
    tax_cfg = config.get("taxonomy")
    if isinstance(tax_cfg, dict) and tax_cfg.get("source_html"):
        from config.taxonomy_from_html import load_taxonomy_from_html
        html_path = ROOT / tax_cfg["source_html"]
        merge_path = ROOT / tax_cfg.get("path", "config/taxonomy.json")
        return load_taxonomy_from_html(html_path, merge_path if merge_path.exists() else None)
    tax_path = ROOT / (tax_cfg if isinstance(tax_cfg, str) else "config/taxonomy.json")
    if not tax_path.exists():
        return {"content_categories": [], "framing_strategies": []}
    with open(tax_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main(
    use_ollama: bool = False,
    use_agent_assessments: bool = False,
    agent_assessments_file: Optional[str] = None,
    output_report: Optional[str] = None,
) -> int:
    config = load_config()
    if use_ollama:
        config.setdefault("llm", {})["use_fixture"] = False
    if output_report:
        out_report = Path(output_report)
        if not out_report.is_absolute():
            out_report = ROOT / out_report
        config.setdefault("output", {})["report_html"] = out_report.name
        config.setdefault("output", {})["dir"] = str(out_report.parent)
    taxonomy = load_taxonomy(config)

    # 1. Ingest (syncs Russian originals from dev into data/russian_originals when document_map_path set)
    from ingest import run as ingest_run
    documents = ingest_run(config, ROOT)
    if not documents:
        print("No documents; exiting.")
        return 1
    print(f"Ingest: {len(documents)} documents")

    # 2. Comparison primary side: pipeline LLM / fixture, or agent assessments (CLI or config.output.comparison_source)
    out_cfg = config.get("output") or {}
    comparison_source = str(out_cfg.get("comparison_source") or "llm").strip().lower()
    use_agent_from_config = comparison_source in ("agent_assessments", "experiment_a")
    effective_use_agent = use_agent_assessments or use_agent_from_config

    if effective_use_agent:
        out_dir = Path(out_cfg.get("dir", "data/output"))
        path_arg = agent_assessments_file or out_cfg.get("agent_assessments_file")
        agent_path = Path(path_arg) if path_arg else out_dir / "agent_assessments.json"
        if not agent_path.is_absolute():
            agent_path = ROOT / agent_path
        if not agent_path.exists():
            print("Agent assessments not found:", agent_path)
            return 1
        with open(agent_path, "r", encoding="utf-8") as f:
            agent_data = json.load(f)
        document_ids = [d.get("document_id") for d in documents]
        llm_by_doc = {doc_id: agent_data.get(doc_id, []) for doc_id in document_ids}
        print(
            f"Agent assessments ({comparison_source if use_agent_from_config else 'CLI'}): {agent_path.name} — "
            f"{len(llm_by_doc)} documents ({sum(len(v) for v in llm_by_doc.values())} rows)"
        )
    else:
        from llm import run as llm_run
        llm_by_doc = llm_run(documents, taxonomy, config)
        print(f"LLM: {len(llm_by_doc)} documents")

    # 3. Ground truth
    from ground_truth import run as gt_run
    document_ids = [d.get("document_id") for d in documents]
    gt_by_doc = gt_run(config, document_ids)
    print(f"Ground truth: {len(gt_by_doc)} documents")

    # 4. Compare
    from compare import run as compare_run
    comparison_by_doc = compare_run(llm_by_doc, gt_by_doc, config)
    print(f"Compare: {len(comparison_by_doc)} documents")

    # 4b. Save intermediate results (so report can be regenerated without re-running LLM/GT)
    out_config = config.get("output", {})
    out_dir = Path(out_config.get("dir", "data/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    json_name = out_config.get("intermediate_json", "comparison_results.json")
    json_path = out_dir / json_name
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"documents": documents, "comparison_by_doc": comparison_by_doc}, f, indent=2, ensure_ascii=False)
    print(f"Saved: {json_path}")

    # Optional secondary comparison (Experiment B) for merged Research Lab viz
    from report import _load_secondary_comparison_by_doc

    sec_rel = (config.get("report") or {}).get("secondary_comparison_json") or ""
    if sec_rel.strip():
        sec_cbd = _load_secondary_comparison_by_doc(config)
        if sec_cbd is None:
            print("Note: secondary_comparison_json set but file missing or empty; Lab charts use primary run only.")
        else:
            print(f"Research Lab: secondary comparison loaded ({len(sec_cbd)} documents) for viz toggle.")

    # 5. Report
    from report import run as report_run
    out_path = report_run(comparison_by_doc, documents, taxonomy, config)
    print(f"Report: {out_path}")

    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--report-only":
        json_path = args[1] if len(args) > 1 else None
        sys.argv = [sys.argv[0]] + ([json_path] if json_path else [])
        from run_report_only import main as report_main
        sys.exit(report_main())
    use_ollama = args and args[0] == "--use-ollama"
    use_agent_assessments = args and args[0] == "--agent-assessments"
    agent_file = None
    output_report = None
    for a in args:
        if a.startswith("--agent-assessments-file="):
            agent_file = a.split("=", 1)[1]
        elif a.startswith("--output-report="):
            output_report = a.split("=", 1)[1]
    sys.exit(main(
        use_ollama=use_ollama,
        use_agent_assessments=use_agent_assessments,
        agent_assessments_file=agent_file,
        output_report=output_report,
    ))
