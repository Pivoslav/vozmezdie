#!/usr/bin/env python3
"""
Write manual assessment for ALL documents with ONLY 4 framing strategies (no Generic).
Uses agent_assessments.json for content_category. For framing: keeps existing if already
one of the 4; otherwise independently assigns based on segment text (no remapping from Generic).

Framing: Institutional / Bureaucratic Lingo | Ideological Framing (Discrediting) |
         Ideological Phrasing (Normalizing) | Action-Focused Language

Output: data/output/agent_assessments_no_generic.json
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "data" / "output"
ASSESSMENTS_PATH = OUT_DIR / "agent_assessments_no_generic.json"

FRAMINGS = [
    "Institutional / Bureaucratic Lingo",
    "Ideological Framing (Discrediting)",
    "Ideological Phrasing (Normalizing)",
    "Action-Focused Language",
]

# Discrediting: expose, discredit, fake, falsification, criminal, defector, etc.
DISCREDIT_RU = re.compile(
    r"разоблач|компрометир|фальсификац|подложн|подлог|кинофальшивк|лжесвидетел|отщепенц|"
    r"преступн|злодеяни|главарями|националист|антисовет|пресловут|тенденциозност|"
    r"подтасовк|искажен|навязан|дискредитац"
)
DISCREDIT_ENG = re.compile(
    r"discredit|expose|fake|falsif|fabricat|forger|defector|renegade|criminal|"
    r"atrocit|bias|imposed|distort|ringleader|nationalist|anti-soviet|notorious"
)

# Normalizing: favorable to us, proving, convincing, genuine absent (asserting our narrative)
NORMALIZE_RU = re.compile(
    r"выгодн|убедительно|доказывающ|подлинн.*отсутствуют|реакцию общественности"
)
NORMALIZE_ENG = re.compile(
    r"favorable|convincing|proving|genuine.*absent|public.*reaction"
)

# Action-focused: verbs of doing
ACTION_RU = re.compile(
    r"осуществля|провод|продвинут|опубликова|помещена|вызвали|планируется|"
    r"оказывает содействие|предусматривается|докладыва|информир"
)
ACTION_ENG = re.compile(
    r"carrying out|aimed at|published|elicited|planned|assisting|send.*warning|"
    r"informed|documenting"
)


def _assign_framing(entry_eng: str, entry_rus: str, content_category: str) -> str:
    """Independently assign framing from the 4 options based on segment text."""
    eng = (entry_eng or "").lower()
    rus = (entry_rus or "").lower()
    combined = eng + " " + rus

    if DISCREDIT_RU.search(rus) or DISCREDIT_ENG.search(eng):
        return "Ideological Framing (Discrediting)"
    if NORMALIZE_RU.search(rus) or NORMALIZE_ENG.search(eng):
        return "Ideological Phrasing (Normalizing)"
    if ACTION_RU.search(rus) or ACTION_ENG.search(eng):
        return "Action-Focused Language"
    # Default: formal archival tone
    return "Institutional / Bureaucratic Lingo"


def main():
    with open(ROOT / "data" / "output" / "agent_assessments.json", "r", encoding="utf-8") as f:
        agent_data = json.load(f)

    no_generic = {}
    doc_ids = [
        "1127", "1128", "1206", "1208", "1209", "1213", "1215", "1230",
        "1245", "1247", "1249-0046-0047", "1249-80-83", "1256",
        "1262_149-150", "1262_198-200", "1262_28-32",
    ]

    for doc_id in doc_ids:
        seg_path = OUT_DIR / f"segments_filtered_{doc_id}.json"
        if not seg_path.exists():
            print(f"Skip {doc_id}: no segments_filtered")
            continue

        segments = json.loads(seg_path.read_text(encoding="utf-8"))
        agent_rows = {r.get("entry_rus", "").strip(): r for r in agent_data.get(doc_id, [])}

        rows = []
        for seg in segments:
            entry_rus = seg.get("entry_rus", "").strip()
            entry_eng = (seg.get("entry_eng", "") or "").strip().replace("puched", "pushed")
            section = seg.get("section")
            context = seg.get("context", entry_eng[:200]).replace("puched", "pushed")

            agent_row = agent_rows.get(entry_rus)
            if agent_row:
                content_category = agent_row.get("content_category", "Context and Concepts")
                old_framing = agent_row.get("framing", "")
                if old_framing in FRAMINGS:
                    framing = old_framing
                else:
                    framing = _assign_framing(entry_eng, entry_rus, content_category)
            else:
                content_category = "Context and Concepts"
                framing = _assign_framing(entry_eng, entry_rus, content_category)

            if doc_id == "1249-0046-0047" and section == 83 and "ГОСБЕЗОПАСН0СТИ" in entry_rus:
                entry_rus = "ПРЕДСЕДАТЕЛЬ КОМИТЕТА ГОСБЕЗОПАСНОСТИ УКРАИНСКОЙ ССР"

            rows.append({
                "section": section,
                "entry_eng": entry_eng,
                "entry_rus": entry_rus,
                "content_category": content_category,
                "framing": framing,
                "context": context,
            })

        no_generic[doc_id] = rows
        print(f"  {doc_id}: {len(rows)} segments")

    ASSESSMENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    ASSESSMENTS_PATH.write_text(json.dumps(no_generic, indent=2, ensure_ascii=False), encoding="utf-8")
    total = sum(len(v) for v in no_generic.values())
    print(f"Written {total} assessments to {ASSESSMENTS_PATH.name}")


if __name__ == "__main__":
    main()
