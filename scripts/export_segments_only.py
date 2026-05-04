#!/usr/bin/env python3
"""
Export segment identifiers only from ground truth HTML.
Output: section, entry_eng, entry_rus, context (NO content_category, NO framing).
Use this so the assessor can work without seeing the human's labels.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from ground_truth.html_loader import load_ground_truth_from_html


def main():
    if len(sys.argv) < 2:
        print("Usage: python export_segments_only.py <doc_id>")
        return 1
    doc_id = sys.argv[1]
    html_path = ROOT / "data" / "ground_truth" / "html" / f"{doc_id}.html"
    if not html_path.exists():
        html_path = ROOT / "data" / "ground_truth" / "html" / f"{doc_id.replace('_', ' ')}.html"
    if not html_path.exists():
        print(f"GT not found for {doc_id}")
        return 1
    rows = load_ground_truth_from_html(html_path)
    segments = [
        {"section": r.get("section"), "entry_eng": r.get("entry_eng", ""), "entry_rus": r.get("entry_rus", ""), "context": r.get("context", r.get("entry_eng", "")[:200])}
        for r in rows
    ]
    out_path = ROOT / "data" / "output" / f"segments_only_{doc_id}.json"
    out_path.write_text(json.dumps(segments, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(segments)} segments (no labels) to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
