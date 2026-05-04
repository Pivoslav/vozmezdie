#!/usr/bin/env python3
"""
Assess segments using Ollama: for each segment, classify content_category and framing.
Uses filtered segments (body rows only) so output aligns with ground truth.
Requires: Ollama running locally with a model (e.g. llama3.1:8b).

Usage: python scripts/assess_segments_ollama.py <doc_id> [doc_id ...]
  e.g. python scripts/assess_segments_ollama.py 1262_28-32 1262_149-150 1262_198-200

Workflow:
  1. python scripts/export_segments_filtered.py 1262_28-32 1262_149-150 1262_198-200
  2. python scripts/assess_segments_ollama.py 1262_28-32 1262_149-150 1262_198-200
  3. python run.py --agent-assessments

Results are merged into data/output/agent_assessments.json. Expect ~2-3 sec per segment.
"""
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def load_config() -> dict:
    config_path = ROOT / "config" / "pipeline_config.example.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_taxonomy(config: dict) -> dict:
    tax_cfg = config.get("taxonomy", {})
    if isinstance(tax_cfg, dict) and tax_cfg.get("source_html"):
        from config.taxonomy_from_html import load_taxonomy_from_html
        html_path = ROOT / tax_cfg["source_html"]
        merge_path = ROOT / tax_cfg.get("path", "config/taxonomy.json")
        return load_taxonomy_from_html(html_path, merge_path if merge_path.exists() else None)
    tax_path = ROOT / (tax_cfg if isinstance(tax_cfg, str) else "config/taxonomy.json")
    with open(tax_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _call_ollama(prompt: str, config: dict) -> str:
    llm_cfg = config.get("llm", {})
    api_url = llm_cfg.get("api_url", "http://localhost:11434/api/generate")
    model_id = llm_cfg.get("model_id", "llama3.1:8b")
    temperature = llm_cfg.get("temperature", 0.2)
    timeout = llm_cfg.get("timeout", 60)

    body = {
        "model": model_id,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature, "num_predict": 200},
    }
    req = urllib.request.Request(
        api_url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("response", "").strip()


def _classify_segment(
    segment: dict,
    categories: list,
    framings: list,
    config: dict,
) -> tuple:
    """Call Ollama to classify one segment. Returns (content_category, framing)."""
    cat_list = ", ".join(categories)
    fram_list = ", ".join(framings)
    entry_eng = segment.get("entry_eng", "")[:300]
    entry_rus = segment.get("entry_rus", "")[:300]
    context = (segment.get("context") or "")[:200]

    prompt = f"""You are classifying a segment from a Cold War KGB archival document.
Assign exactly one content_category and one framing from the lists below.

Content categories (pick one): {cat_list}
Framing strategies (pick one): {fram_list}

Segment (English): {entry_eng}
Segment (Russian): {entry_rus}
Context: {context}

Respond with ONLY a single JSON object, no other text:
{{"content_category": "...", "framing": "..."}}"""

    try:
        resp = _call_ollama(prompt, config)
    except Exception as e:
        print(f"  Ollama error: {e}")
        return (categories[0] if categories else "", framings[0] if framings else "")

    # Parse response
    resp = resp.strip()
    for prefix in ("```json", "```"):
        if resp.startswith(prefix):
            resp = resp[len(prefix):].strip()
    if resp.endswith("```"):
        resp = resp[:-3].strip()
    try:
        obj = json.loads(resp)
        cat = obj.get("content_category", "").strip()
        fram = obj.get("framing", "").strip()
        if cat not in categories:
            cat = categories[0] if categories else ""
        if fram not in framings:
            fram = framings[0] if framings else ""
        return (cat, fram)
    except json.JSONDecodeError:
        return (categories[0] if categories else "", framings[0] if framings else "")


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python assess_segments_ollama.py <doc_id> [doc_id ...]")
        print("  First run: python scripts/export_segments_filtered.py <doc_id> ...")
        return 1

    config = load_config()
    taxonomy = load_taxonomy(config)
    categories = [c["id"] for c in taxonomy.get("content_categories", [])]
    framings = [f["id"] for f in taxonomy.get("framing_strategies", [])]
    if not categories:
        categories = ["Actions", "Actors", "Places", "Time", "Documents", "Context and Concepts", "Legal Framework"]
    if not framings:
        framings = ["Generic / Neutral Language", "Institutional / Bureaucratic Lingo", "Ideological Framing (Discrediting)", "Ideological Phrasing (Normalizing)", "Action-Focused Language"]

    # Normalize framing: "Generic / Neutral" and "Generic / Neutral Language" both valid
    fram_set = set(framings)
    if "Generic / Neutral" in fram_set and "Generic / Neutral Language" not in fram_set:
        framings = [f if f != "Generic / Neutral" else "Generic / Neutral Language" for f in framings]

    out_dir = ROOT / "data" / "output"
    assessments_path = out_dir / "agent_assessments.json"
    assessments = {}
    if assessments_path.exists():
        assessments = json.loads(assessments_path.read_text(encoding="utf-8"))

    for doc_id in sys.argv[1:]:
        seg_path = out_dir / f"segments_filtered_{doc_id}.json"
        if not seg_path.exists():
            print(f"Run first: python scripts/export_segments_filtered.py {doc_id}")
            continue

        segments = json.loads(seg_path.read_text(encoding="utf-8"))
        rows = []
        total = len(segments)
        for i, seg in enumerate(segments):
            if (i + 1) % 20 == 0 or i == 0:
                print(f"  {doc_id}: {i + 1}/{total}")
            cat, fram = _classify_segment(seg, categories, framings, config)
            rows.append({
                "section": seg.get("section"),
                "entry_eng": seg.get("entry_eng", ""),
                "entry_rus": seg.get("entry_rus", ""),
                "content_category": cat,
                "framing": fram,
                "context": seg.get("context", (seg.get("entry_eng") or "")[:200]),
            })

        assessments[doc_id] = rows
        print(f"  {doc_id}: assessed {len(rows)} segments")

    assessments_path.parent.mkdir(parents=True, exist_ok=True)
    assessments_path.write_text(json.dumps(assessments, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Written to {assessments_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
