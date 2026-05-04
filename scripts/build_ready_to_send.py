#!/usr/bin/env python3
"""
Build ready_to_send_CHUNK.txt from prompt template + chunk JSON.

Ensures prompt and chunk stay in sync. Run after export_synonym_chunks.py.

Usage: python scripts/build_ready_to_send.py [chunk_number]
  chunk_number: 1-138 (default: 1)
Output: data/output/synonym_chunks/ready_to_send_chunk_NNN.txt
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHUNKS_DIR = ROOT / "data" / "output" / "synonym_chunks"

PROMPT = '''You are a JSON output API. Do not ask questions. Do not offer options. Do not comment on the input.

Instructions: For each object in the "terms" array, produce definition_eng, definition_rus, synonyms_eng (array of 1-5), synonyms_rus (array of 1-5). Preserve entry_eng and entry_rus exactly. Formal Cold War archival register. Proper nouns: use synonyms_eng=[], synonyms_rus=[], definition_eng="Proper name; no definition".

Your ENTIRE response must be a single JSON object: {"term_results":[...]}.
The first character you output MUST be {. The last character MUST be }.
No text before. No text after. No "Here is...", no "What would you like...", no analysis.

Input:
'''


def main() -> int:
    chunk_num = 1
    if len(sys.argv) > 1:
        try:
            chunk_num = int(sys.argv[1])
        except ValueError:
            print("Usage: python scripts/build_ready_to_send.py [chunk_number]")
            return 1

    chunk_path = CHUNKS_DIR / f"chunk_{chunk_num:03d}.json"
    if not chunk_path.exists():
        print(f"Not found: {chunk_path}")
        print("Run first: python scripts/export_synonym_chunks.py")
        return 1

    chunk_data = json.loads(chunk_path.read_text(encoding="utf-8"))
    chunk_json = json.dumps(chunk_data, ensure_ascii=False)

    out_path = CHUNKS_DIR / f"ready_to_send_chunk_{chunk_num:03d}.txt"
    out_path.write_text(PROMPT + chunk_json, encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
