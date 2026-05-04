#!/usr/bin/env python3
"""
Merge agent assessment chunks into full English (and optionally Russian) text for documents
that lack a continuous translation. Reads chunk*_<doc_id>.json from data/output, merges
by section, concatenates entry_eng/entry_rus, writes to dev/english_translations and
dev/russian_originals. For 1249-0046-0047, also produces chunk-aligned Russian so Eng/Rus
panels match segment-for-segment.
Usage: python scripts/merge_chunks_to_english.py <doc_id>
Example: python scripts/merge_chunks_to_english.py 1249-0046-0047
"""
import json
import sys
from pathlib import Path
from typing import Dict, Optional

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "data" / "output"
DEV_EN = ROOT / "dev" / "english_translations"
DEV_RU = ROOT / "dev" / "russian_originals"


# Paragraph break points (section numbers) to match document structure.
# Insert \n\n after these sections.
PARAGRAPH_BREAKS: Dict[str, tuple] = {
    "1249-0046-0047": (18, 39, 62, 69, 81, 82),  # header, p1, p2, p3, p4, "Submitted", signature
}


def _load_and_sort_rows(doc_id: str):
    """Load all chunk files and return rows sorted by section."""
    chunks = sorted(OUT_DIR.glob(f"chunk*_{doc_id}.json"))
    if not chunks:
        return None
    all_rows = []
    for p in chunks:
        with open(p, "r", encoding="utf-8") as f:
            all_rows.extend(json.load(f))
    return sorted(all_rows, key=lambda x: x.get("section", 0))


def _merge_by_entry_key(rows, doc_id: str, entry_key: str) -> Optional[str]:
    """Merge rows using entry_eng or entry_rus, with paragraph breaks. Fallback to the other key if empty."""
    if not rows:
        return None
    other_key = "entry_rus" if entry_key == "entry_eng" else "entry_eng"
    break_after = set(PARAGRAPH_BREAKS.get(doc_id, ()))
    output_parts = []
    prev_section = 0
    for r in rows:
        primary = (r.get(entry_key) or "").strip()
        fallback = (r.get(other_key) or "").strip()
        text = primary if primary else fallback
        if not text:
            continue
        section = r.get("section", 0)
        if output_parts:
            if prev_section in break_after:
                output_parts.append("\n\n")
            else:
                output_parts.append(" ")
        output_parts.append(text)
        prev_section = section
    result = "".join(output_parts).strip() if output_parts else None
    if result and doc_id == "1249-0046-0047" and entry_key == "entry_eng":
        result = result.replace("puched out", "pushed out")
    return result


def merge_chunks_to_english(doc_id: str) -> Optional[str]:
    """Load all chunk*_<doc_id>.json, merge by section, return full English text."""
    rows = _load_and_sort_rows(doc_id)
    return _merge_by_entry_key(rows, doc_id, "entry_eng") if rows else None


def merge_chunks_to_russian(doc_id: str) -> Optional[str]:
    """Same structure as English but using entry_rus for chunk-aligned Russian."""
    rows = _load_and_sort_rows(doc_id)
    return _merge_by_entry_key(rows, doc_id, "entry_rus") if rows else None


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python merge_chunks_to_english.py <doc_id>")
        return 1
    doc_id = sys.argv[1]
    eng_text = merge_chunks_to_english(doc_id)
    if not eng_text:
        print(f"No chunks found for {doc_id} or empty result.")
        return 1
    # Output English
    if doc_id == "1249-0046-0047":
        out_name = "F.16-Op.01-Spr.1249-0046-0047 ENG.txt"
    else:
        out_name = f"{doc_id.replace('-', '_')} ENG.txt"
    DEV_EN.mkdir(parents=True, exist_ok=True)
    (DEV_EN / out_name).write_text(eng_text, encoding="utf-8")
    print(f"Wrote: {DEV_EN / out_name}")
    # For 1249-0046-0047, also emit chunk-aligned Russian (same structure as English) so panels match
    if doc_id == "1249-0046-0047":
        rus_text = merge_chunks_to_russian(doc_id)
        if rus_text:
            rus_name = "F.16-Op.01-Spr.1249-0046-0047 RUS chunk-aligned.txt"
            DEV_RU.mkdir(parents=True, exist_ok=True)
            (DEV_RU / rus_name).write_text(rus_text, encoding="utf-8")
            print(f"Wrote: {DEV_RU / rus_name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
