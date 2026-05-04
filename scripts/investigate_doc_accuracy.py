#!/usr/bin/env python3
"""
Investigate accuracy for a specific document (e.g. 1245).

Usage: python scripts/investigate_doc_accuracy.py [doc_id]
Default: 1245

Outputs: category distribution (human vs LLM), sample mismatches, schema analysis.
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    doc_id = sys.argv[1] if len(sys.argv) > 1 else "1245"
    json_path = ROOT / "data" / "output" / "comparison_results.json"
    if not json_path.exists():
        print(f"Not found: {json_path}")
        print("Run: python run.py")
        return 1

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    comp = data.get("comparison_by_doc", {})
    if doc_id not in comp:
        print(f"Document {doc_id} not in comparison results.")
        print("Available:", ", ".join(sorted(comp.keys())))
        return 1

    c = comp[doc_id]
    rows = c.get("aligned_rows", [])
    n_human = c.get("n_human", 0)
    n_llm = c.get("n_llm", 0)
    n_matched = c.get("n_matched", 0)

    human_cats = Counter((r.get("human_category") or "").strip() for r in rows)
    llm_cats = Counter((r.get("llm_category") or "").strip() for r in rows)

    print(f"=== Document {doc_id} ===")
    print(f"n_human={n_human} n_llm={n_llm} n_matched={n_matched}")
    print(f"category_accuracy={c.get('category_accuracy_pct')}% framing={c.get('framing_accuracy_pct')}% both={c.get('both_match_pct')}%")
    print()
    print("Human (GT) categories:")
    for cat, cnt in human_cats.most_common(20):
        print(f"  {repr(cat)}: {cnt}")
    print()
    print("LLM categories:")
    for cat, cnt in llm_cats.most_common(20):
        print(f"  {repr(cat)}: {cnt}")

    mismatches = [r for r in rows if not r.get("category_match")]
    print()
    print(f"Category mismatches: {len(mismatches)} of {len(rows)}")
    if mismatches:
        print()
        print("Sample mismatches (first 5):")
        for r in mismatches[:5]:
            eng = (r.get("entry_eng") or "")[:50]
            print(f"  Human: {repr(r.get('human_category'))} | LLM: {repr(r.get('llm_category'))}")
            print(f"    entry_eng: {repr(eng)}...")

    # Schema analysis
    n_human_cats = len(human_cats)
    n_llm_cats = len(llm_cats)
    if n_human_cats <= 3 and n_llm_cats > 5:
        print()
        print("SCHEMA MISMATCH DETECTED:")
        print("  Ground truth uses a coarse schema (few categories); LLM uses full taxonomy.")
        print("  Low category accuracy is likely due to different annotation schemas,")
        print("  not LLM failure. Consider re-annotating with the project taxonomy.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
