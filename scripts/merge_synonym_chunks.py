#!/usr/bin/env python3
"""
Merge synonym chunk outputs into a single term_synonyms.json.

Reads JSON files from a directory. Each file should have either:
- term_results: array of {entry_eng, entry_rus, synonyms_eng, synonyms_rus, ...}
- term_synonyms: array of {entry_eng, entry_rus, synonyms_eng, synonyms_rus}

Preserves definitions (definition_eng, definition_rus) if present.
Deduplicates by (entry_eng, entry_rus); last occurrence wins.

Usage: python scripts/merge_synonym_chunks.py [--input-dir DIR] [--output PATH]
  --input-dir: directory with chunk output files (default: data/output/synonym_chunks_output)
  --output: output path (default: config/term_synonyms.json)
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Dict

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT_DIR = ROOT / "data" / "output" / "synonym_chunks_output"
DEFAULT_OUTPUT = ROOT / "config" / "term_synonyms.json"


def main() -> int:
    ap = argparse.ArgumentParser(description="Merge synonym chunk outputs into term_synonyms.json")
    ap.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help=f"Directory with chunk output JSON files (default: {DEFAULT_INPUT_DIR.relative_to(ROOT)})",
    )
    ap.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output path (default: {DEFAULT_OUTPUT.relative_to(ROOT)})",
    )
    ap.add_argument(
        "--pattern",
        type=str,
        default="*.json",
        help="Glob pattern for input files (default: *.json)",
    )
    args = ap.parse_args()

    input_dir = args.input_dir if args.input_dir.is_absolute() else ROOT / args.input_dir
    output_path = args.output if args.output.is_absolute() else ROOT / args.output

    if not input_dir.exists():
        print(f"Input directory not found: {input_dir}")
        print("Create it and add chunk output files (e.g. chunk_001_out.json).")
        return 1

    files = sorted(input_dir.glob(args.pattern))
    if not files:
        print(f"No matching files in {input_dir}")
        return 1

    merged: Dict[tuple, dict] = {}
    for p in files:
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Skipping {p.name}: {e}")
            continue

        for key in ("term_results", "term_synonyms"):
            items = data.get(key, [])
            if not isinstance(items, list):
                continue
            for item in items:
                eng = (item.get("entry_eng") or "").strip()
                rus = (item.get("entry_rus") or "").strip()
                if not eng and not rus:
                    continue
                key_tuple = (eng or rus, rus or eng)
                merged[key_tuple] = {
                    "entry_eng": eng or rus,
                    "entry_rus": rus or eng,
                    "synonyms_eng": item.get("synonyms_eng") or [],
                    "synonyms_rus": item.get("synonyms_rus") or [],
                }
                if "definition_eng" in item:
                    merged[key_tuple]["definition_eng"] = item["definition_eng"]
                if "definition_rus" in item:
                    merged[key_tuple]["definition_rus"] = item["definition_rus"]
            break

    term_list = list(merged.values())
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"term_synonyms": term_list}, f, indent=2, ensure_ascii=False)

    print(f"Merged {len(term_list)} terms into {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
