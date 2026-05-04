#!/usr/bin/env python3
"""
Write fresh manual assessment for 1249-0046-0047.
Based on: taxonomy (7 categories, 5 framing), Russian original, segment list.
Never read GT labels. Fix typo: puched->pushed. Fix Russian: ГОСБЕЗОПАСН0СТИУКРАИНСКОЙ -> proper.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEGMENTS_PATH = ROOT / "data" / "output" / "segments_only_1249-0046-0047.json"
ASSESSMENTS_PATH = ROOT / "data" / "output" / "agent_assessments.json"

# Assessment: (content_category, framing) by section. Taxonomy: Actions, Actors, Places, Time, Documents, Context and Concepts, Legal Framework.
# Framing: Generic / Neutral Language, Institutional / Bureaucratic Lingo, Ideological Framing (Discrediting), Ideological Phrasing (Normalizing), Action-Focused Language.
ASSESSMENT = {
    2: ("Documents", "Generic / Neutral Language"),
    3: ("Documents", "Generic / Neutral Language"),
    4: ("Time", "Generic / Neutral Language"),
    5: ("Places", "Generic / Neutral Language"),
    6: ("Context and Concepts", "Generic / Neutral Language"),
    7: ("Context and Concepts", "Generic / Neutral Language"),
    8: ("Time", "Generic / Neutral Language"),
    9: ("Context and Concepts", "Generic / Neutral Language"),
    10: ("Time", "Generic / Neutral Language"),
    11: ("Actors", "Generic / Neutral Language"),
    12: ("Actors", "Institutional / Bureaucratic Lingo"),
    13: ("Actors", "Generic / Neutral Language"),
    15: ("Context and Concepts", "Institutional / Bureaucratic Lingo"),
    16: ("Actors", "Institutional / Bureaucratic Lingo"),
    17: ("Context and Concepts", "Institutional / Bureaucratic Lingo"),
    18: ("Documents", "Generic / Neutral Language"),
    19: ("Actors", "Institutional / Bureaucratic Lingo"),
    20: ("Context and Concepts", "Institutional / Bureaucratic Lingo"),
    21: ("Actions", "Action-Focused Language"),
    22: ("Actions", "Action-Focused Language"),
    23: ("Context and Concepts", "Ideological Framing (Discrediting)"),
    24: ("Actors", "Ideological Phrasing (Normalizing)"),
    25: ("Context and Concepts", "Ideological Framing (Discrediting)"),
    26: ("Context and Concepts", "Ideological Framing (Discrediting)"),
    27: ("Context and Concepts", "Generic / Neutral Language"),
    28: ("Context and Concepts", "Institutional / Bureaucratic Lingo"),
    29: ("Places", "Generic / Neutral Language"),
    30: ("Actions", "Institutional / Bureaucratic Lingo"),
    31: ("Actions", "Ideological Framing (Discrediting)"),
    32: ("Actions", "Ideological Framing (Discrediting)"),
    33: ("Context and Concepts", "Ideological Framing (Discrediting)"),
    34: ("Documents", "Generic / Neutral Language"),
    35: ("Actors", "Generic / Neutral Language"),
    36: ("Actors", "Ideological Framing (Discrediting)"),
    37: ("Actors", "Ideological Framing (Discrediting)"),
    38: ("Actors", "Generic / Neutral Language"),
    39: ("Actors", "Generic / Neutral Language"),
    40: ("Actions", "Action-Focused Language"),
    41: ("Context and Concepts", "Ideological Phrasing (Normalizing)"),
    42: ("Documents", "Generic / Neutral Language"),
    43: ("Actions", "Generic / Neutral Language"),
    44: ("Context and Concepts", "Generic / Neutral Language"),
    45: ("Documents", "Generic / Neutral Language"),
    46: ("Actors", "Generic / Neutral Language"),
    47: ("Context and Concepts", "Ideological Framing (Discrediting)"),
    48: ("Context and Concepts", "Ideological Phrasing (Normalizing)"),
    49: ("Context and Concepts", "Ideological Phrasing (Normalizing)"),
    50: ("Actors", "Ideological Framing (Discrediting)"),
    51: ("Documents", "Generic / Neutral Language"),
    52: ("Actions", "Generic / Neutral Language"),
    53: ("Actions", "Ideological Phrasing (Normalizing)"),
    54: ("Context and Concepts", "Ideological Phrasing (Normalizing)"),
    55: ("Context and Concepts", "Ideological Framing (Discrediting)"),
    56: ("Context and Concepts", "Ideological Framing (Discrediting)"),
    57: ("Actions", "Generic / Neutral Language"),
    58: ("Time", "Generic / Neutral Language"),
    59: ("Actors", "Generic / Neutral Language"),
    60: ("Documents", "Generic / Neutral Language"),
    61: ("Places", "Generic / Neutral Language"),
    62: ("Context and Concepts", "Ideological Phrasing (Normalizing)"),
    63: ("Context and Concepts", "Institutional / Bureaucratic Lingo"),
    64: ("Actions", "Action-Focused Language"),
    65: ("Context and Concepts", "Ideological Framing (Discrediting)"),
    66: ("Context and Concepts", "Ideological Framing (Discrediting)"),
    67: ("Actors", "Ideological Framing (Discrediting)"),
    68: ("Actions", "Ideological Framing (Discrediting)"),
    69: ("Actions", "Ideological Framing (Discrediting)"),
    70: ("Context and Concepts", "Institutional / Bureaucratic Lingo"),
    71: ("Actors", "Institutional / Bureaucratic Lingo"),
    72: ("Context and Concepts", "Institutional / Bureaucratic Lingo"),
    73: ("Actions", "Institutional / Bureaucratic Lingo"),
    74: ("Actions", "Ideological Framing (Discrediting)"),
    75: ("Actions", "Institutional / Bureaucratic Lingo"),
    76: ("Actors", "Generic / Neutral Language"),
    77: ("Context and Concepts", "Ideological Framing (Discrediting)"),
    78: ("Actors", "Ideological Framing (Discrediting)"),
    79: ("Actions", "Institutional / Bureaucratic Lingo"),
    80: ("Context and Concepts", "Ideological Framing (Discrediting)"),
    81: ("Context and Concepts", "Ideological Phrasing (Normalizing)"),
    82: ("Context and Concepts", "Institutional / Bureaucratic Lingo"),
    83: ("Actors", "Institutional / Bureaucratic Lingo"),
    84: ("Actors", "Generic / Neutral Language"),
}


def main():
    segments = json.loads(SEGMENTS_PATH.read_text(encoding="utf-8"))
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
    ASSESSMENTS_PATH.write_text(json.dumps(assessments, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Written {len(rows)} assessments for 1249-0046-0047")


if __name__ == "__main__":
    main()
