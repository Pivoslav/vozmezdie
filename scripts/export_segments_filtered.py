#!/usr/bin/env python3
"""
Export segment identifiers from ground truth, using the SAME filter as the pipeline.
Only body rows (content_category in taxonomy) are exported. Section numbers align
with what compare uses. Use this for fresh assessment so segments match GT exactly.

Usage: python scripts/export_segments_filtered.py <doc_id> [doc_id ...]
Output: data/output/segments_filtered_<doc_id>.json
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main():
    if len(sys.argv) < 2:
        print("Usage: python export_segments_filtered.py <doc_id> [doc_id ...]")
        return 1

    config_path = ROOT / "config" / "pipeline_config.example.json"
    if not config_path.exists():
        print(f"Config not found: {config_path}")
        return 1
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    from ground_truth import run as gt_run

    doc_ids = sys.argv[1:]
    gt_by_doc = gt_run(config, doc_ids)

    for doc_id in doc_ids:
        rows = gt_by_doc.get(doc_id, [])
        segments = [
            {
                "section": r.get("section"),
                "entry_eng": r.get("entry_eng", ""),
                "entry_rus": r.get("entry_rus", ""),
                "context": r.get("context", (r.get("entry_eng") or "")[:200]),
            }
            for r in rows
        ]
        out_path = ROOT / "data" / "output" / f"segments_filtered_{doc_id}.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(segments, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {len(segments)} filtered segments to {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
