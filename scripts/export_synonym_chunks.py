#!/usr/bin/env python3
"""
Split terms_for_synonyms.json into chunk files for the synonym chat agent.

Each chunk contains 15-25 terms (configurable). The chat agent processes one chunk
at a time and returns JSON; use merge_synonym_chunks.py to combine outputs.

Usage: python scripts/export_synonym_chunks.py [--chunk-size N]
Output: data/output/synonym_chunks/chunk_001.json, chunk_002.json, ...
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TERMS_PATH = ROOT / "data" / "output" / "terms_for_synonyms.json"
OUT_DIR = ROOT / "data" / "output" / "synonym_chunks"


def main() -> int:
    ap = argparse.ArgumentParser(description="Split terms into chunks for synonym chat agent")
    ap.add_argument(
        "--chunk-size",
        type=int,
        default=20,
        help="Number of terms per chunk (default: 20)",
    )
    args = ap.parse_args()

    if not TERMS_PATH.exists():
        print(f"Not found: {TERMS_PATH}")
        print("Run first: python scripts/export_terms_for_synonyms.py")
        return 1

    with open(TERMS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    terms = data.get("terms", [])
    if not terms:
        print("No terms in file.")
        return 1

    chunk_size = max(1, args.chunk_size)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    written = 0
    for i in range(0, len(terms), chunk_size):
        chunk_terms = terms[i : i + chunk_size]
        chunk_id = (i // chunk_size) + 1
        chunk_data = {
            "chunk_id": chunk_id,
            "total_chunks": (len(terms) + chunk_size - 1) // chunk_size,
            "terms": chunk_terms,
        }
        out_path = OUT_DIR / f"chunk_{chunk_id:03d}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(chunk_data, f, indent=2, ensure_ascii=False)
        written += 1

    print(f"Wrote {written} chunks to {OUT_DIR}")
    print(f"Terms: {len(terms)}, chunk size: {chunk_size}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
