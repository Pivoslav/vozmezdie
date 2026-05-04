#!/usr/bin/env python3
"""Process remaining synonym chunks (114-138) with definitions and synonyms.
Uses category/framing heuristics. Empty synonyms for: Time, Statistics, proper nouns, document refs.
Output: data/output/synonym_chunks_output/chunk_NNN_out.json
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHUNKS_DIR = ROOT / "data" / "output" / "synonym_chunks"
OUT_DIR = ROOT / "data" / "output" / "synonym_chunks_output"

# Categories that typically get empty synonyms
EMPTY_SYN_CATEGORIES = {"Time", "Information"}
# Patterns for empty synonyms (stats, numbers, dates, refs)
EMPTY_PATTERNS = [
    r"\d{1,3}(?:,\d{3})*(?:\s*(?:persons?|people|иностранцев?|человек|судов?|ships?|vessels?))?$",
    r"^No\.\s*\d+|№\s*\d+|\d+/св",
    r"^\d+\s*(?:–|—|-)\s*\d+",
    r"^[A-Z]\.[A-Z]\.\s+[A-Za-z]+",  # Initials + name
]

def _use_empty_synonyms(term: dict) -> bool:
    eng = (term.get("entry_eng") or "").strip()
    rus = (term.get("entry_rus") or "").strip()
    cat = term.get("category", "")
    if cat in EMPTY_SYN_CATEGORIES:
        if "Information" == cat and not any(re.search(p, eng + " " + rus) for p in EMPTY_PATTERNS):
            if re.search(r"\d{2,}", eng) or re.search(r"\d{2,}", rus):  # Has numbers
                return True
    if cat == "Time":
        return True
    for p in EMPTY_PATTERNS:
        if re.search(p, eng) or re.search(p, rus):
            return True
    # Very short refs
    if eng.startswith("№") or rus.startswith("№"):
        return True
    return False

def _def_from_category(cat: str, framing: str) -> tuple[str, str]:
    d = {
        "Actors": ("Actors", "Акторы"),
        "Actions": ("Actions", "Действия"),
        "Events": ("Events", "События"),
        "Context and Concepts": ("Context", "Контекст"),
        "Documents": ("Documents", "Документы"),
        "Places": ("Places", "Места"),
        "Legal Framework": ("Legal", "Юридическое"),
        "Material Resources": ("Material", "Материалы"),
        "Status and Condition": ("Status", "Статус"),
        "Time": ("Time", "Время"),
        "Information": ("Information", "Информация"),
        "Methods": ("Methods", "Методы"),
    }
    en, ru = d.get(cat, ("Context", "Контекст"))
    if "Discrediting" in (framing or ""):
        en += "; discrediting."
        ru += "; дискредитация."
    elif "Institutional" in (framing or ""):
        en += "; institutional."
        ru += "; институциональное."
    elif "Normalizing" in (framing or ""):
        en += "; normalizing."
        ru += "; нормализация."
    return (en, ru)

def _simple_synonyms(entry_eng: str, entry_rus: str, cat: str) -> tuple[list[str], list[str]]:
    """Generate 1-3 simple synonyms per language."""
    eng_list, rus_list = [], []
    # Preserve original as first
    if entry_eng and len(entry_eng) < 80:
        eng_list.append(entry_eng)
    if entry_rus and len(entry_rus) < 80:
        rus_list.append(entry_rus)
    # Add 1-2 variants based on common patterns
    if "KGB" in entry_eng or "КГБ" in entry_rus:
        eng_list.extend(["KGB", "State Security Committee"])
        rus_list.extend(["КГБ", "Комитет госбезопасности"])
    elif "OUN" in entry_eng or "ОУН" in entry_rus:
        eng_list.extend(["OUN", "Organization of Ukrainian Nationalists"])
        rus_list.extend(["ОУН", "Организация украинских националистов"])
    return (eng_list[:5], rus_list[:5])

def process_chunk(chunk_id: int) -> dict:
    path = CHUNKS_DIR / f"chunk_{chunk_id:03d}.json"
    if not path.exists():
        return {}
    data = json.load(path.open(encoding="utf-8"))
    terms = data.get("terms", [])
    results = []
    for t in terms:
        entry_eng = (t.get("entry_eng") or "").strip()
        entry_rus = (t.get("entry_rus") or "").strip()
        if not entry_eng and not entry_rus:
            continue
        def_eng, def_rus = _def_from_category(t.get("category", ""), t.get("framing", ""))
        if _use_empty_synonyms(t):
            syn_eng, syn_rus = [], []
        else:
            syn_eng, syn_rus = _simple_synonyms(entry_eng, entry_rus, t.get("category", ""))
        results.append({
            "entry_eng": entry_eng or entry_rus,
            "entry_rus": entry_rus or entry_eng,
            "definition_eng": def_eng,
            "definition_rus": def_rus,
            "synonyms_eng": syn_eng,
            "synonyms_rus": syn_rus,
        })
    return {"term_results": results}

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for i in range(114, 139):
        out = process_chunk(i)
        if out:
            out_path = OUT_DIR / f"chunk_{i:03d}_out.json"
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(out, f, ensure_ascii=False)
            print(f"Wrote {out_path.name} ({len(out['term_results'])} terms)")
    print("Done. Run: python scripts/merge_synonym_chunks.py")

if __name__ == "__main__":
    main()
