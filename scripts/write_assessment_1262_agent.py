#!/usr/bin/env python3
"""
Agent (AI) assessment for 1262 documents. Uses filtered segments.
Assessment by AI based on taxonomy; no GT labels read.
Run: python scripts/write_assessment_1262_agent.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "output"
SCRIPTS = ROOT / "scripts"

# Taxonomy: content_category, framing. Use exact labels from taxonomy.
# 1262_149-150 (54 segments)
ASSESSMENT_149_150 = {
    17: ("Places", "Generic / Neutral Language"),
    18: ("Time", "Generic / Neutral Language"),
    19: ("Information", "Institutional / Bureaucratic Lingo"),
    20: ("Places", "Generic / Neutral Language"),
    21: ("Information", "Institutional / Bureaucratic Lingo"),
    22: ("Status and Condition", "Institutional / Bureaucratic Lingo"),
    23: ("Actors", "Ideological Framing (Discrediting)"),
    24: ("Actors", "Institutional / Bureaucratic Lingo"),
    25: ("Actions", "Institutional / Bureaucratic Lingo"),
    26: ("Context and Concepts", "Generic / Neutral Language"),
    27: ("Places", "Generic / Neutral Language"),
    28: ("Actors", "Generic / Neutral Language"),
    29: ("Actors", "Generic / Neutral Language"),
    30: ("Actions", "Institutional / Bureaucratic Lingo"),
    32: ("Events", "Ideological Framing (Discrediting)"),
    33: ("Actors", "Ideological Framing (Discrediting)"),
    34: ("Actions", "Action-Focused Language"),
    35: ("Methods", "Institutional / Bureaucratic Lingo"),
    36: ("Time", "Generic / Neutral Language"),
    37: ("Context and Concepts", "Ideological Phrasing (Normalizing)"),
    38: ("Information", "Ideological Framing (Discrediting)"),
    39: ("Context and Concepts", "Ideological Framing (Discrediting)"),
    40: ("Context and Concepts", "Ideological Phrasing (Normalizing)"),
    41: ("Places", "Generic / Neutral Language"),
    42: ("Time", "Generic / Neutral Language"),
    43: ("Documents", "Institutional / Bureaucratic Lingo"),
    44: ("Actions", "Ideological Phrasing (Normalizing)"),
    45: ("Actors", "Institutional / Bureaucratic Lingo"),
    46: ("Actions", "Institutional / Bureaucratic Lingo"),
    47: ("Actors", "Institutional / Bureaucratic Lingo"),
    48: ("Actions", "Institutional / Bureaucratic Lingo"),
    49: ("Actors", "Generic / Neutral Language"),
    50: ("Events", "Institutional / Bureaucratic Lingo"),
    51: ("Context and Concepts", "Institutional / Bureaucratic Lingo"),
    52: ("Context and Concepts", "Institutional / Bureaucratic Lingo"),
    53: ("Actors", "Institutional / Bureaucratic Lingo"),
    54: ("Actions", "Institutional / Bureaucratic Lingo"),
    55: ("Legal Framework", "Institutional / Bureaucratic Lingo"),
    56: ("Status and Condition", "Ideological Framing (Discrediting)"),
    57: ("Actors", "Generic / Neutral Language"),
    58: ("Legal Framework", "Institutional / Bureaucratic Lingo"),
    59: ("Time", "Generic / Neutral Language"),
    60: ("Actors", "Ideological Framing (Discrediting)"),
    61: ("Places", "Generic / Neutral Language"),
    62: ("Actions", "Ideological Framing (Discrediting)"),
    63: ("Actions", "Institutional / Bureaucratic Lingo"),
    64: ("Actions", "Ideological Framing (Discrediting)"),
    65: ("Information", "Ideological Phrasing (Normalizing)"),
    67: ("Actors", "Institutional / Bureaucratic Lingo"),
    68: ("Actions", "Action-Focused Language"),
    69: ("Status and Condition", "Ideological Framing (Discrediting)"),
    70: ("Actors", "Ideological Framing (Discrediting)"),
    71: ("Actors", "Institutional / Bureaucratic Lingo"),
    72: ("Actors", "Institutional / Bureaucratic Lingo"),
}


def _load_assessment_json(name: str) -> dict:
    """Load assessment from scripts/assessment_<name>.json; keys become int."""
    path = SCRIPTS / f"assessment_{name}.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {int(k): tuple(v) for k, v in data.items()}


ASSESSMENT_28_32 = _load_assessment_json("1262_28_32")
ASSESSMENT_198_200 = _load_assessment_json("1262_198_200")


def _build_rows(doc_id: str, assessment: dict) -> list:
    seg_path = OUT / f"segments_filtered_{doc_id}.json"
    if not seg_path.exists():
        print(f"Run first: python scripts/export_segments_filtered.py {doc_id}")
        return []
    segments = json.loads(seg_path.read_text(encoding="utf-8"))
    rows = []
    for s in segments:
        sec = s.get("section")
        if sec not in assessment:
            continue
        cat, fram = assessment[sec]
        rows.append({
            "section": sec,
            "entry_eng": s.get("entry_eng", ""),
            "entry_rus": s.get("entry_rus", ""),
            "content_category": cat,
            "framing": fram,
            "context": s.get("context", (s.get("entry_eng") or "")[:200]),
        })
    return rows


def main():
    assessments_path = OUT / "agent_assessments.json"
    assessments = {}
    if assessments_path.exists():
        assessments = json.loads(assessments_path.read_text(encoding="utf-8"))

    for doc_id, assessment in [
        ("1262_149-150", ASSESSMENT_149_150),
        ("1262_28-32", ASSESSMENT_28_32),
        ("1262_198-200", ASSESSMENT_198_200),
    ]:
        rows = _build_rows(doc_id, assessment)
        if rows:
            assessments[doc_id] = rows
            print(f"Written {len(rows)} assessments for {doc_id}")

    assessments_path.write_text(json.dumps(assessments, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved to {assessments_path}")


if __name__ == "__main__":
    main()
