"""
Ground truth module: load human-coded rows per document.
Output: dict document_id -> list of extraction rows (same shape as LLM output).
When loading from HTML, rows whose content_category is not in the taxonomy are dropped (metadata rows like "Title 2", "Document Type").
"""
from pathlib import Path
from typing import Dict, List, Any, Set
import csv


def _load_taxonomy_for_filter(config: Dict[str, Any], root: Path) -> Set[str]:
    """Load taxonomy from config and return set of valid content_category ids (for filtering metadata rows)."""
    tax_cfg = config.get("taxonomy")
    if not tax_cfg:
        return set()
    if isinstance(tax_cfg, dict) and tax_cfg.get("source_html"):
        try:
            from config.taxonomy_from_html import load_taxonomy_from_html
            html_path = root / tax_cfg["source_html"]
            merge_path = root / tax_cfg.get("path", "config/taxonomy.json")
            data = load_taxonomy_from_html(html_path, merge_path if merge_path.exists() else None)
        except Exception:
            return set()
    else:
        tax_path = root / (tax_cfg if isinstance(tax_cfg, str) else "config/taxonomy.json")
        if not tax_path.exists():
            return set()
        try:
            import json
            with open(tax_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return set()
    return {c.get("id", "").strip() for c in data.get("content_categories", []) if c.get("id")}


# Map archival/fragment GT categories (used in some HTML sheets) to taxonomy categories.
# Fragments of the same document may use different column schemas; this lets them pass the filter.
_ARCHIVAL_CATEGORY_MAP = {
    "Archival Record Data": "Information",
    "Body of the Text": "Context and Concepts",
}


def _map_row_categories(rows: List[Dict[str, Any]], valid_categories: Set[str]) -> List[Dict[str, Any]]:
    """
    For rows whose content_category is not in valid_categories, try mapping from archival
    schema (Archival Record Data, Body of the Text) to a taxonomy category. Preserves rows
    that would otherwise be dropped when fragment GTs use a different schema.
    """
    if not rows or not valid_categories:
        return rows
    out = []
    for r in rows:
        cat = (r.get("content_category") or "").strip()
        if not cat or cat in valid_categories:
            out.append(r)
            continue
        mapped = _ARCHIVAL_CATEGORY_MAP.get(cat)
        if mapped and mapped in valid_categories:
            out.append({**r, "content_category": mapped})
        else:
            out.append(r)  # keep anyway for optional later filter
    return out


def run(config: Dict[str, Any], document_ids: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Load ground truth for each document_id. Returns same row shape as LLM: section, entry_eng, entry_rus, content_category, framing, context.
    When ground_truth.html_dir is set, load from HTML there; drop rows whose content_category is not in the taxonomy (so metadata rows like "Title 2" are excluded).
    """
    gt_config = config.get("ground_truth", {})
    html_dir = gt_config.get("html_dir")
    path = Path(gt_config.get("path", "data/ground_truth"))
    pattern = gt_config.get("pattern", "*.csv")
    root = Path(__file__).resolve().parent.parent
    valid_categories = _load_taxonomy_for_filter(config, root)

    result = {}
    for doc_id in document_ids:
        rows = None
        if html_dir:
            html_path = Path(html_dir)
            for candidate in (html_path / f"{doc_id}.html", html_path / f"{doc_id.replace('_', ' ')}.html"):
                if candidate.exists():
                    from ground_truth.html_loader import load_ground_truth_from_html
                    rows = load_ground_truth_from_html(candidate)
                    break
        if rows is None and path.exists():
            candidates = list(path.glob(pattern))
            matching = [c for c in candidates if doc_id in c.stem or c.stem in doc_id]
            if matching:
                rows = _load_csv(matching[0])
        if rows is None:
            rows = _fixture_rows(doc_id)
        if rows and valid_categories:
            rows = _map_row_categories(rows, valid_categories)
            rows = [r for r in rows if (r.get("content_category") or "").strip() in valid_categories]
        result[doc_id] = rows
    return result


def _load_csv(path: Path) -> List[Dict[str, Any]]:
    """Load CSV with expected columns; normalize to extraction row shape."""
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                "section": int(r.get("section", r.get("Section", 0)) or 0),
                "entry_eng": r.get("entry_eng", r.get("Entry (ENG)", "")).strip(),
                "entry_rus": r.get("entry_rus", r.get("Entry (RUS)", "")).strip(),
                "content_category": r.get("content_category", r.get("Content Category", "")).strip(),
                "framing": r.get("framing", r.get("Framing", "")).strip(),
                "context": r.get("context", r.get("Context", "")).strip(),
            })
    return rows


def _fixture_rows(doc_id: str) -> List[Dict[str, Any]]:
    """Fixture ground truth so compare has something to run on."""
    return [
        {"section": 1, "entry_eng": "Sample phrase one", "entry_rus": "", "content_category": "Context and Concepts", "framing": "Generic / Neutral", "context": "Sample phrase one."},
        {"section": 2, "entry_eng": "Sample phrase two", "entry_rus": "", "content_category": "Actions", "framing": "Institutional / Bureaucratic Lingo", "context": "Sample phrase two."},
    ]
