#!/usr/bin/env python3
"""
Regenerate the HTML report from saved comparison results (no LLM, no ingest).
Usage: python run_report_only.py [path/to/comparison_results.json] [--no-generic]
  --no-generic: produce manual_analysis_report_no_generic.html with Generic/Neutral rows removed
Default: config/output.dir + config/output.intermediate_json
"""
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

ROOT = Path(__file__).resolve().parent

GENERIC_FRAMINGS = {"Generic / Neutral Language", "Generic / Neutral"}


def _filter_no_generic(comparison_by_doc: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Remove rows where human_framing or llm_framing is Generic/Neutral; recompute stats."""
    filtered = {}
    for doc_id, comp in comparison_by_doc.items():
        aligned = comp.get("aligned_rows", [])
        kept = [
            r for r in aligned
            if (r.get("human_framing") or "").strip() not in GENERIC_FRAMINGS
            and (r.get("llm_framing") or "").strip() not in GENERIC_FRAMINGS
        ]
        total = len(kept)
        if total == 0:
            cat_pct = fram_pct = both_pct = 0.0
        else:
            cat_pct = 100.0 * sum(1 for r in kept if r.get("category_match")) / total
            fram_pct = 100.0 * sum(1 for r in kept if r.get("framing_match")) / total
            both_pct = 100.0 * sum(1 for r in kept if r.get("both_match")) / total
        filtered[doc_id] = {
            "aligned_rows": kept,
            "n_human": comp.get("n_human", 0),
            "n_llm": comp.get("n_llm", 0),
            "n_matched": total,
            "category_accuracy_pct": round(cat_pct, 1),
            "framing_accuracy_pct": round(fram_pct, 1),
            "both_match_pct": round(both_pct, 1),
        }
    return filtered


def load_config() -> dict:
    config_path = ROOT / "config" / "pipeline_config.example.json"
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


def main() -> int:
    config = load_config()
    taxonomy = load_taxonomy(config)

    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    no_generic = "--no-generic" in sys.argv[1:]

    # JSON path: CLI arg or config default
    if args:
        json_path = Path(args[0])
    else:
        out_dir = Path(config.get("output", {}).get("dir", "data/output"))
        json_name = config.get("output", {}).get("intermediate_json", "comparison_results.json")
        json_path = ROOT / out_dir / json_name

    if not json_path.exists():
        print(f"Not found: {json_path}")
        print("Run the full pipeline first: python run.py")
        return 1

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    comparison_by_doc = data.get("comparison_by_doc", {})

    if no_generic:
        comparison_by_doc = _filter_no_generic(comparison_by_doc)
        out_dir = Path(config.get("output", {}).get("dir", "data/output"))
        config = dict(config)
        config.setdefault("output", {})
        config["output"] = dict(config["output"])
        config["output"]["report_html"] = "manual_analysis_report_no_generic.html"
        config["output"]["dir"] = str(out_dir)

    # Load documents fresh from ingest so raw_text/raw_text_en always match current files.
    # JSON may have stale cached documents; comparison_by_doc is the expensive part we keep.
    from ingest import run as ingest_run
    documents = ingest_run(config, ROOT)
    if not documents:
        print("No documents from ingest.")
        return 1

    from report import run as report_run
    out_path = report_run(comparison_by_doc, documents, taxonomy, config)
    print(f"Report: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
