"""
Optional Ollama adapter: call local Ollama API for extraction.
Returns same row shape as stub. Used when config.llm.provider == "ollama" and use_fixture is false.
"""
import json
import urllib.request
import urllib.error
from typing import Dict, List, Any


def extract_one_document(
    document_id: str,
    raw_text: str,
    taxonomy: Dict[str, Any],
    config: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Send text to Ollama with a minimal extraction prompt; parse response into rows.
    On failure (timeout, parse error), returns empty list so caller can fall back to stub.
    """
    llm_cfg = config.get("llm", {})
    api_url = llm_cfg.get("api_url", "http://localhost:11434/api/generate")
    model_id = llm_cfg.get("model_id", "llama3.1:8b")
    max_tokens = llm_cfg.get("max_tokens", 5000)
    temperature = llm_cfg.get("temperature", 0.3)
    timeout = llm_cfg.get("timeout", 600)

    categories = [c["id"] for c in taxonomy.get("content_categories", [])]
    framings = [f["id"] for f in taxonomy.get("framing_strategies", [])]
    if not categories:
        categories = [
            "Actors", "Places", "Actions", "Events",
            "Date & Time", "Legal Framework", "Documents", "Material Resources",
        ]
    if not framings:
        framings = ["Generic / Neutral Language", "Institutional / Bureaucratic Lingo"]

    prompt = _build_prompt(raw_text, categories, framings)
    body = {
        "model": model_id,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature, "num_predict": max_tokens},
    }
    req = urllib.request.Request(
        api_url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError):
        return []

    text = data.get("response", "")
    return _parse_response(text, categories, framings)


def _build_prompt(raw_text: str, categories: List[str], framings: List[str]) -> str:
    cat_list = ", ".join(categories)
    fram_list = ", ".join(framings)
    return f"""You are analyzing a short archival document. For each meaningful phrase or entity, output one line as JSON:
{{"entry_eng": "...", "content_category": "...", "framing": "..."}}

Rules:
- content_category must be one of: {cat_list}
- framing must be one of: {fram_list}
- Output only valid JSON lines, one per phrase. No other text.

Document text:
---
{raw_text[:8000]}
---

JSON lines (one per phrase):"""


def _parse_response(text: str, categories: List[str], framings: List[str]) -> List[Dict[str, Any]]:
    """Parse model output into extraction rows. Tolerates JSON lines or a single JSON array."""
    rows = []
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        # Strip markdown code block if present
        if line.startswith("```"):
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                entry_eng = obj.get("entry_eng", obj.get("phrase", ""))
                if not entry_eng:
                    continue
                cat = obj.get("content_category", "")
                fram = obj.get("framing", "")
                if cat not in categories:
                    cat = categories[0] if categories else ""
                if fram not in framings:
                    fram = framings[0] if framings else ""
                rows.append({
                    "section": len(rows) + 1,
                    "entry_eng": entry_eng,
                    "entry_rus": obj.get("entry_rus", ""),
                    "content_category": cat,
                    "framing": fram,
                    "context": obj.get("context", entry_eng),
                })
            elif isinstance(obj, list):
                for item in obj:
                    if isinstance(item, dict):
                        entry_eng = item.get("entry_eng", item.get("phrase", ""))
                        if entry_eng:
                            rows.append({
                                "section": len(rows) + 1,
                                "entry_eng": entry_eng,
                                "entry_rus": item.get("entry_rus", ""),
                                "content_category": item.get("content_category", categories[0] if categories else ""),
                                "framing": item.get("framing", framings[0] if framings else ""),
                                "context": item.get("context", entry_eng),
                            })
        except json.JSONDecodeError:
            continue
    return rows
