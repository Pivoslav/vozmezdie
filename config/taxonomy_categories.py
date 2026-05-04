"""
Content-category taxonomy churn: canonical IDs used after Categories Explained merge.

Renames legacy labels (e.g. Time → Date & Time) and drops deprecated categories
from glossary/taxonomy-driven lists. Report aggregation uses canonical IDs so
removed buckets disappear from corpus charts. Compare output and report loading
normalize aligned rows to canonical category/framing strings so retired labels do not
persist in JSON or HTML.
"""

from __future__ import annotations

from typing import Any, Dict, FrozenSet, List, Optional, Set

CONTENT_CATEGORY_RENAMES: Dict[str, str] = {
    "Time": "Date & Time",
}

DEPRECATED_CONTENT_CATEGORIES: FrozenSet[str] = frozenset({
    "Methods",
    "Information",
    "Status and Condition",
    "Status and Conditions",
    "Context and Concepts",
    "Contexts and Concepts",
    "Generic",
})

# When loading ground-truth HTML/CSV, fold legacy sheet labels into the current taxonomy
# so rows are kept instead of dropped during validation.
GROUND_TRUTH_CONTENT_CATEGORY_REDIRECT: Dict[str, str] = {
    **CONTENT_CATEGORY_RENAMES,
    "Archival Record Data": "Documents",
    "Body of the Text": "Documents",
    "Generic": "Documents",
    "Information": "Documents",
    "Methods": "Documents",
    "Status and Condition": "Documents",
    "Status and Conditions": "Documents",
    "Context and Concepts": "Documents",
    "Contexts and Concepts": "Documents",
}


def display_content_category_for_ui(cat: Optional[str]) -> str:
    """Fold legacy sheet/LLM labels into current taxonomy names for report UI (tables, spans, filters)."""
    if not cat:
        return ""
    s = str(cat).strip()
    if not s:
        return ""
    return GROUND_TRUTH_CONTENT_CATEGORY_REDIRECT.get(s, s)


def display_framing_for_ui(fram: Optional[str]) -> str:
    """Single canonical framing label for storage and UI (short Generic variants → taxonomy id)."""
    if not fram:
        return ""
    t = str(fram).strip()
    if not t:
        return ""
    if t in ("Generic / Neutral", "Generic / Neutral Language", "Generic"):
        return "Generic / Neutral Language"
    return t


def scrub_retired_multiword_category_labels(text: str) -> str:
    """In glossary prose, replace retired multi-word category headings with canonical names."""
    if not text or not text.strip():
        return text
    out = text
    keys = [k for k in GROUND_TRUTH_CONTENT_CATEGORY_REDIRECT if " " in k]
    keys.sort(key=len, reverse=True)
    for k in keys:
        if k in out:
            out = out.replace(k, GROUND_TRUTH_CONTENT_CATEGORY_REDIRECT[k])
    return out


def normalize_comparison_row_for_canonical_storage(row: Dict[str, Any]) -> Dict[str, Any]:
    """Canonical labels + recomputed match flags (idempotent if already canonical)."""
    r = dict(row)
    lc = display_content_category_for_ui(str(r.get("llm_category") or "")).strip()
    hc = display_content_category_for_ui(str(r.get("human_category") or "")).strip()
    lf = display_framing_for_ui(str(r.get("llm_framing") or "")).strip()
    hf = display_framing_for_ui(str(r.get("human_framing") or "")).strip()
    r["llm_category"] = lc
    r["human_category"] = hc
    r["llm_framing"] = lf
    r["human_framing"] = hf
    r["category_match"] = lc == hc
    r["framing_match"] = lf == hf
    r["both_match"] = bool(r["category_match"] and r["framing_match"])
    return r


def _aligned_rows_for_accuracy_metrics(aligned: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """When rows include paired_with_llm (content alignment with full GT listing), metrics use paired rows only."""
    if not aligned or not any("paired_with_llm" in r for r in aligned):
        return aligned
    return [r for r in aligned if r.get("paired_with_llm")]


def normalize_comparison_by_doc(comparison_by_doc: Optional[Dict[str, Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
    """Normalize every aligned row and refresh accuracy fields (for stale JSON or report-only runs)."""
    if not comparison_by_doc:
        return {}
    out: Dict[str, Dict[str, Any]] = {}
    for doc_id, comp in comparison_by_doc.items():
        c = dict(comp)
        aligned = [normalize_comparison_row_for_canonical_storage(r) for r in comp.get("aligned_rows", [])]
        c["aligned_rows"] = aligned
        acc_rows = _aligned_rows_for_accuracy_metrics(aligned)
        n = len(acc_rows)
        if n == 0:
            c["category_accuracy_pct"] = 0.0
            c["framing_accuracy_pct"] = 0.0
            c["both_match_pct"] = 0.0
        else:
            c["category_accuracy_pct"] = round(100.0 * sum(1 for r in acc_rows if r.get("category_match")) / n, 1)
            c["framing_accuracy_pct"] = round(100.0 * sum(1 for r in acc_rows if r.get("framing_match")) / n, 1)
            c["both_match_pct"] = round(100.0 * sum(1 for r in acc_rows if r.get("both_match")) / n, 1)
        out[doc_id] = c
    return out


GENERIC_FRAMING_CANONICAL = "Generic / Neutral Language"


def row_has_generic_framing_strategy(row: Dict[str, Any]) -> bool:
    """True if LLM or human framing normalizes to Generic / Neutral Language."""
    lf = display_framing_for_ui(str(row.get("llm_framing") or "")).strip()
    hf = display_framing_for_ui(str(row.get("human_framing") or "")).strip()
    g = GENERIC_FRAMING_CANONICAL
    return lf == g or hf == g


def drop_comparison_rows_with_generic_framing(
    comparison_by_doc: Optional[Dict[str, Dict[str, Any]]],
) -> Dict[str, Dict[str, Any]]:
    """Remove aligned rows where either side uses generic/neutral framing; refresh stats and n_matched."""
    if not comparison_by_doc:
        return {}
    out: Dict[str, Dict[str, Any]] = {}
    for doc_id, comp in comparison_by_doc.items():
        aligned_all = comp.get("aligned_rows", [])
        kept = [r for r in aligned_all if not row_has_generic_framing_strategy(r)]
        c = dict(comp)
        c["aligned_rows"] = kept
        n = len(kept)
        if n == 0:
            c["category_accuracy_pct"] = 0.0
            c["framing_accuracy_pct"] = 0.0
            c["both_match_pct"] = 0.0
        else:
            c["category_accuracy_pct"] = round(100.0 * sum(1 for r in kept if r.get("category_match")) / n, 1)
            c["framing_accuracy_pct"] = round(100.0 * sum(1 for r in kept if r.get("framing_match")) / n, 1)
            c["both_match_pct"] = round(100.0 * sum(1 for r in kept if r.get("both_match")) / n, 1)
        c["n_matched"] = n
        out[doc_id] = c
    return out


def rename_content_category_id(cat: Optional[str]) -> Optional[str]:
    if not cat:
        return None
    s = cat.strip()
    if not s:
        return None
    return CONTENT_CATEGORY_RENAMES.get(s, s)


def canonical_content_category_id(cat: Optional[str]) -> Optional[str]:
    """Stable category id for stats/colours/filters taxonomy; None if deprecated or empty."""
    s = rename_content_category_id(cat)
    if not s:
        return None
    if s in DEPRECATED_CONTENT_CATEGORIES:
        return None
    return s


def restrict_content_categories_to_allowed_ids(
    items: List[Dict[str, Any]],
    allowed_ids: FrozenSet[str],
) -> List[Dict[str, Any]]:
    """Drop any category not in taxonomy.json allowlist; normalize id to canonical."""
    if not allowed_ids:
        return list(items)
    out: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    for c in items:
        raw = (c.get("id") or c.get("label_en") or "").strip()
        folded = display_content_category_for_ui(raw)
        canon = canonical_content_category_id(folded)
        if not canon or canon not in allowed_ids:
            continue
        if canon in seen:
            continue
        seen.add(canon)
        row = dict(c)
        row["id"] = canon
        row["label_en"] = canon
        out.append(row)
    return out


def restrict_framing_strategies_to_allowed_ids(
    items: List[Dict[str, Any]],
    allowed_ids: FrozenSet[str],
) -> List[Dict[str, Any]]:
    """Drop framings not listed in taxonomy.json; normalize Generic shorthand."""
    if not allowed_ids:
        return list(items)
    out: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    for f in items:
        raw = (f.get("id") or f.get("label_en") or "").strip()
        canon = display_framing_for_ui(raw)
        if not canon or canon not in allowed_ids:
            continue
        if canon in seen:
            continue
        seen.add(canon)
        row = dict(f)
        row["id"] = canon
        row["label_en"] = canon
        out.append(row)
    return out


def filter_content_categories_for_taxonomy(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Drop deprecated CE categories; rename Time; dedupe by canonical id."""
    out: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for c in items:
        raw = (c.get("id") or c.get("label_en") or "").strip()
        canon = canonical_content_category_id(raw)
        if canon is None:
            continue
        if canon in seen:
            continue
        seen.add(canon)
        row = dict(c)
        row["id"] = canon
        row["label_en"] = canon
        out.append(row)
    return out
