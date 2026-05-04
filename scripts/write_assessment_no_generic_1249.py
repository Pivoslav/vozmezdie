#!/usr/bin/env python3
"""
Write manual assessment for 1249-0046-0047 with ONLY 4 framing strategies (no Generic).
Independent assessment of each segment; Generic was never an option.

Framing: Institutional / Bureaucratic Lingo | Ideological Framing (Discrediting) |
         Ideological Phrasing (Normalizing) | Action-Focused Language

Output: data/output/agent_assessments_no_generic.json
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEGMENTS_PATH = ROOT / "data" / "output" / "segments_filtered_1249-0046-0047.json"
ASSESSMENTS_PATH = ROOT / "data" / "output" / "agent_assessments_no_generic.json"

# Independent assessment: (content_category, framing) by section.
# Framing: 4 only — no Generic.
ASSESSMENT = {
    16: ("Actors", "Institutional / Bureaucratic Lingo"),
    17: ("Actors", "Institutional / Bureaucratic Lingo"),
    18: ("Documents", "Institutional / Bureaucratic Lingo"),
    19: ("Actors", "Institutional / Bureaucratic Lingo"),
    20: ("Context and Concepts", "Institutional / Bureaucratic Lingo"),
    21: ("Actions", "Action-Focused Language"),
    22: ("Actions", "Action-Focused Language"),
    23: ("Context and Concepts", "Ideological Framing (Discrediting)"),
    24: ("Actors", "Ideological Framing (Discrediting)"),
    25: ("Context and Concepts", "Ideological Framing (Discrediting)"),
    26: ("Context and Concepts", "Ideological Framing (Discrediting)"),
    27: ("Context and Concepts", "Institutional / Bureaucratic Lingo"),
    28: ("Context and Concepts", "Institutional / Bureaucratic Lingo"),
    29: ("Places", "Institutional / Bureaucratic Lingo"),
    30: ("Actions", "Action-Focused Language"),
    31: ("Actions", "Ideological Framing (Discrediting)"),
    32: ("Actions", "Ideological Framing (Discrediting)"),
    33: ("Context and Concepts", "Ideological Framing (Discrediting)"),
    34: ("Documents", "Ideological Framing (Discrediting)"),
    35: ("Actors", "Institutional / Bureaucratic Lingo"),
    36: ("Actors", "Ideological Framing (Discrediting)"),
    37: ("Actors", "Ideological Framing (Discrediting)"),
    38: ("Actors", "Institutional / Bureaucratic Lingo"),
    39: ("Actors", "Institutional / Bureaucratic Lingo"),
    40: ("Actions", "Action-Focused Language"),
    41: ("Context and Concepts", "Ideological Phrasing (Normalizing)"),
    42: ("Documents", "Institutional / Bureaucratic Lingo"),
    43: ("Actions", "Action-Focused Language"),
    44: ("Context and Concepts", "Institutional / Bureaucratic Lingo"),
    45: ("Documents", "Institutional / Bureaucratic Lingo"),
    46: ("Actors", "Institutional / Bureaucratic Lingo"),
    47: ("Context and Concepts", "Ideological Framing (Discrediting)"),
    48: ("Context and Concepts", "Ideological Phrasing (Normalizing)"),
    49: ("Context and Concepts", "Ideological Phrasing (Normalizing)"),
    50: ("Actors", "Ideological Framing (Discrediting)"),
    51: ("Documents", "Institutional / Bureaucratic Lingo"),
    52: ("Actions", "Action-Focused Language"),
    53: ("Actions", "Ideological Phrasing (Normalizing)"),
    54: ("Context and Concepts", "Ideological Phrasing (Normalizing)"),
    55: ("Context and Concepts", "Ideological Framing (Discrediting)"),
    56: ("Context and Concepts", "Ideological Framing (Discrediting)"),
    57: ("Actions", "Action-Focused Language"),
    58: ("Time", "Institutional / Bureaucratic Lingo"),
    59: ("Actors", "Institutional / Bureaucratic Lingo"),
    60: ("Documents", "Institutional / Bureaucratic Lingo"),
    61: ("Places", "Institutional / Bureaucratic Lingo"),
    62: ("Context and Concepts", "Ideological Phrasing (Normalizing)"),
    63: ("Context and Concepts", "Institutional / Bureaucratic Lingo"),
    64: ("Actions", "Ideological Framing (Discrediting)"),
    65: ("Context and Concepts", "Ideological Framing (Discrediting)"),
    66: ("Context and Concepts", "Ideological Framing (Discrediting)"),
    67: ("Context and Concepts", "Ideological Framing (Discrediting)"),
    68: ("Actions", "Ideological Framing (Discrediting)"),
    69: ("Actions", "Ideological Framing (Discrediting)"),
    70: ("Context and Concepts", "Institutional / Bureaucratic Lingo"),
    71: ("Actors", "Institutional / Bureaucratic Lingo"),
    72: ("Context and Concepts", "Institutional / Bureaucratic Lingo"),
    73: ("Actions", "Institutional / Bureaucratic Lingo"),
    74: ("Actions", "Ideological Framing (Discrediting)"),
    75: ("Actions", "Institutional / Bureaucratic Lingo"),
    76: ("Context and Concepts", "Institutional / Bureaucratic Lingo"),
    77: ("Context and Concepts", "Ideological Framing (Discrediting)"),
    78: ("Actors", "Ideological Framing (Discrediting)"),
    79: ("Actions", "Institutional / Bureaucratic Lingo"),
    80: ("Context and Concepts", "Ideological Framing (Discrediting)"),
    81: ("Context and Concepts", "Ideological Phrasing (Normalizing)"),
    82: ("Context and Concepts", "Institutional / Bureaucratic Lingo"),
    83: ("Actors", "Institutional / Bureaucratic Lingo"),
    84: ("Actors", "Institutional / Bureaucratic Lingo"),
}


def main():
    segments = json.loads(SEGMENTS_PATH.read_text(encoding="utf-8"))
    assessments = {}
    if ASSESSMENTS_PATH.exists():
        assessments = json.loads(ASSESSMENTS_PATH.read_text(encoding="utf-8"))

    rows = []
    for s in segments:
        sec = s["section"]
        if sec not in ASSESSMENT:
            continue
        cat, framing = ASSESSMENT[sec]
        entry_eng = s["entry_eng"].replace("puched", "pushed")
        entry_rus = s["entry_rus"]
        if sec == 83 and "ГОСБЕЗОПАСН0СТИУКРАИНСКОЙ" in entry_rus:
            entry_rus = "ПРЕДСЕДАТЕЛЬ КОМИТЕТА ГОСБЕЗОПАСНОСТИ УКРАИНСКОЙ ССР"
        rows.append({
            "section": sec,
            "entry_eng": entry_eng,
            "entry_rus": entry_rus,
            "content_category": cat,
            "framing": framing,
            "context": s.get("context", entry_eng[:200]).replace("puched", "pushed"),
        })

    assessments["1249-0046-0047"] = rows
    ASSESSMENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    ASSESSMENTS_PATH.write_text(json.dumps(assessments, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Written {len(rows)} assessments for 1249-0046-0047 to {ASSESSMENTS_PATH.name}")


if __name__ == "__main__":
    main()
