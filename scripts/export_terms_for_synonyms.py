#!/usr/bin/env python3
"""
Export unique term pairs (entry_eng, entry_rus) from comparison_results.json
for the synonym agent task.

Usage: python scripts/export_terms_for_synonyms.py [path/to/comparison_results.json]
Output: data/output/terms_for_synonyms.json

The synonym agent should use this file as input and produce term_synonyms.json.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


# Known typos/corrections: (entry_eng, entry_rus) -> corrected (entry_eng, entry_rus)
_TERM_FIXES: dict[tuple[str, str], tuple[str, str]] = {
    ('"Brothers in the Dollar"', 'Братья во долларе"'): ('"Brothers in the Dollar"', '"Братья во долларе"'),
}


def _normalize_for_group(s: str) -> str:
    if not s:
        return ""
    t = s.strip()
    if t in ("Generic / Neutral", "Generic / Neutral Language"):
        return "Generic / Neutral Language"
    return t


def collect_terms(comparison_by_doc: dict) -> list:
    """Extract unique (entry_eng, entry_rus) pairs with category/framing info."""
    seen: set[tuple[str, str]] = set()
    terms: list[dict] = []
    for doc_id, comp in (comparison_by_doc or {}).items():
        for r in comp.get("aligned_rows", []):
            eng = (r.get("entry_eng") or "").strip()
            rus = (r.get("entry_rus") or "").strip()
            if not eng and not rus:
                continue
            pair = (eng or rus, rus or eng)
            if pair in seen:
                continue
            seen.add(pair)
            eng, rus = eng or rus, rus or eng
            fixed = _TERM_FIXES.get((eng, rus), (eng, rus))
            cat = _normalize_for_group(r.get("llm_category") or "")
            fram = _normalize_for_group(r.get("llm_framing") or "")
            if not cat:
                cat = "Context and Concepts"
            if not fram:
                fram = "Generic / Neutral Language"
            terms.append({
                "entry_eng": fixed[0],
                "entry_rus": fixed[1],
                "category": cat,
                "framing": fram,
            })
    return sorted(terms, key=lambda t: (t["entry_eng"] or t["entry_rus"]).lower())


def main() -> int:
    if len(sys.argv) > 1:
        json_path = Path(sys.argv[1])
    else:
        json_path = ROOT / "data" / "output" / "comparison_results.json"

    if not json_path.exists():
        print(f"Not found: {json_path}")
        print("Run the full pipeline first: python run.py")
        return 1

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    comparison_by_doc = data.get("comparison_by_doc", {})

    terms = collect_terms(comparison_by_doc)
    out = {
        "terms": terms,
        "source": str(json_path),
        "count": len(terms),
    }

    out_path = ROOT / "data" / "output" / "terms_for_synonyms.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"Exported {len(terms)} terms to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
