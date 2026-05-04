"""
LLM extraction module: call LLM (or mock), return extraction rows per document.
Output: dict document_id -> list of { section, entry_eng, entry_rus, content_category, framing, context }.

When config.llm.provider == "ollama" and use_fixture is not true, uses llm.ollama_adapter.
Otherwise uses stub (fixture rows from raw_text) so pipeline runs without Ollama.
"""
from typing import Dict, List, Any


def run(
    documents: List[Dict[str, Any]],
    taxonomy: Dict[str, Any],
    config: Dict[str, Any],
) -> Dict[str, List[Dict[str, Any]]]:
    """
    For each document, produce list of extraction rows.
    Uses Ollama adapter if configured; else stub.
    """
    llm_cfg = config.get("llm", {})
    use_ollama = (
        llm_cfg.get("provider") == "ollama"
        and not llm_cfg.get("use_fixture", False)
    )

    result = {}
    for doc in documents:
        doc_id = doc.get("document_id", "unknown")
        raw = doc.get("raw_text", "")

        if use_ollama and raw:
            try:
                from .ollama_adapter import extract_one_document
                rows = extract_one_document(doc_id, raw, taxonomy, config)
            except Exception:
                rows = []
            if not rows:
                result[doc_id] = _stub_rows(doc_id, raw, taxonomy)
            else:
                result[doc_id] = rows
        else:
            result[doc_id] = _stub_rows(doc_id, raw, taxonomy)

    return result


def _stub_rows(doc_id: str, raw_text: str, taxonomy: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Stub: one row per sentence/phrase from raw_text, categories/framing cycled from taxonomy.
    Russian-first: raw_text is the Russian original; phrase goes to entry_rus, entry_eng left empty
    (English comes from GT in aligned rows). Splits on sentence boundaries and newlines; keeps
    phrases with at least 4 characters.
    """
    categories = [c["id"] for c in taxonomy.get("content_categories", [])]
    framings = [f["id"] for f in taxonomy.get("framing_strategies", [])]
    if not categories:
        categories = ["Actions", "Actors"]
    if not framings:
        framings = ["Generic / Neutral Language"]

    text = (raw_text or "").replace("\r\n", "\n")
    # Split on sentence end then on newline (works for both English and Russian/Cyrillic)
    parts = []
    for chunk in text.replace(". ", ". \n").split("\n"):
        for p in chunk.split(". "):
            s = p.strip()
            if s:
                parts.append(s)
    MIN_PHRASE_LEN = 4
    phrases = [p for p in parts if len(p) >= MIN_PHRASE_LEN][:25]
    rows = []
    for i, phrase in enumerate(phrases, 1):
        rows.append({
            "section": i,
            "entry_eng": "",
            "entry_rus": phrase,
            "content_category": categories[i % len(categories)],
            "framing": framings[i % len(framings)],
            "context": phrase,
        })
    return rows if rows else [{"section": 1, "entry_eng": "", "entry_rus": "(no text)", "content_category": categories[0], "framing": framings[0], "context": ""}]
