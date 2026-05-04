"""
Compare / accuracy module: align LLM rows to ground truth, compute match stats.
Supports index-based alignment (legacy), content-based matching by entry_eng (content),
or by entry_rus (content_rus) for Russian-first pipeline.
Output: per document { aligned_rows, n_human, n_llm, n_matched, category_accuracy_pct, framing_accuracy_pct, both_match_pct }.

With match_by content / content_rus, aligned_rows lists every ground-truth segment in order; rows without an
LLM pair have empty llm_category / llm_framing and paired_with_llm False. Accuracy percentages use only
paired_with_llm rows (same denominator as n_matched).
"""
from typing import Dict, List, Any, Optional, Tuple, Callable

from config.taxonomy_categories import normalize_comparison_row_for_canonical_storage


def _normalize(text: str) -> str:
    """Normalize phrase for matching: strip, collapse whitespace, lowercase."""
    if not text:
        return ""
    s = " ".join((text or "").split()).strip().lower()
    return s


def _content_match_pairs_with(
    gt_rows: List[Dict[str, Any]],
    llm_rows: List[Dict[str, Any]],
    text_getter: Callable[[Dict[str, Any], int, str], str],
) -> List[Tuple[int, int]]:
    """
    Pair each human row with at most one LLM row by normalized text (exact then containment).
    text_getter(row, idx, label) returns the phrase to match (e.g. entry_eng or entry_rus).
    """
    gt_used = set()
    llm_used = set()
    pairs: List[Tuple[int, int]] = []

    gt_norm = [(i, _normalize(text_getter(gt_rows[i], i, "gt"))) for i in range(len(gt_rows))]
    llm_norm = [(i, _normalize(text_getter(llm_rows[i], i, "llm"))) for i in range(len(llm_rows))]

    # 1) Exact match
    gt_by_norm: Dict[str, List[int]] = {}
    for i, n in gt_norm:
        if n:
            gt_by_norm.setdefault(n, []).append(i)
    for llm_i, n in llm_norm:
        if not n or n not in gt_by_norm:
            continue
        for gt_i in gt_by_norm[n]:
            if gt_i not in gt_used:
                gt_used.add(gt_i)
                llm_used.add(llm_i)
                pairs.append((gt_i, llm_i))
                break

    # 2) Containment: one phrase contains the other (unmatched only).
    MIN_CONTAINMENT_LEN = 4
    for gt_i in range(len(gt_rows)):
        if gt_i in gt_used:
            continue
        gt_text = _normalize(text_getter(gt_rows[gt_i], gt_i, "gt"))
        if not gt_text:
            continue
        for llm_i in range(len(llm_rows)):
            if llm_i in llm_used:
                continue
            llm_text = _normalize(text_getter(llm_rows[llm_i], llm_i, "llm"))
            if not llm_text:
                continue
            shorter = min(len(gt_text), len(llm_text))
            if shorter < MIN_CONTAINMENT_LEN:
                continue
            if gt_text in llm_text or llm_text in gt_text:
                gt_used.add(gt_i)
                llm_used.add(llm_i)
                pairs.append((gt_i, llm_i))
                break

    return pairs


def _content_match_pairs(
    gt_rows: List[Dict[str, Any]],
    llm_rows: List[Dict[str, Any]],
) -> List[Tuple[int, int]]:
    """Match by entry_eng (English)."""
    def eng(r: Dict, idx: int, label: str) -> str:
        return (r.get("entry_eng") or "").strip()
    return _content_match_pairs_with(gt_rows, llm_rows, eng)


def _content_match_pairs_rus(
    gt_rows: List[Dict[str, Any]],
    llm_rows: List[Dict[str, Any]],
) -> List[Tuple[int, int]]:
    """Match by entry_rus (Russian original)."""
    def rus(r: Dict, idx: int, label: str) -> str:
        return (r.get("entry_rus") or "").strip()
    return _content_match_pairs_with(gt_rows, llm_rows, rus)


def _align_by_index(
    llm_rows: List[Dict[str, Any]],
    gt_rows: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Legacy: align by row index (pad/truncate)."""
    aligned = []
    n = max(len(llm_rows), len(gt_rows))
    for i in range(n):
        llm = llm_rows[i] if i < len(llm_rows) else {}
        gt = gt_rows[i] if i < len(gt_rows) else {}
        cat_match = (llm.get("content_category") or "").strip() == (gt.get("content_category") or "").strip()
        fram_match = (llm.get("framing") or "").strip() == (gt.get("framing") or "").strip()
        aligned.append({
            "section": llm.get("section", gt.get("section", i + 1)),
            "entry_eng": gt.get("entry_eng", llm.get("entry_eng", "")),
            "entry_rus": gt.get("entry_rus", llm.get("entry_rus", "")),
            "llm_category": llm.get("content_category", ""),
            "llm_framing": llm.get("framing", ""),
            "human_category": gt.get("content_category", ""),
            "human_framing": gt.get("framing", ""),
            "context": llm.get("context", gt.get("context", "")),
            "category_match": cat_match,
            "framing_match": fram_match,
            "both_match": cat_match and fram_match,
        })
    return [normalize_comparison_row_for_canonical_storage(r) for r in aligned]


def _align_by_content(
    llm_rows: List[Dict[str, Any]],
    gt_rows: List[Dict[str, Any]],
    match_rus: bool = False,
) -> Tuple[List[Dict[str, Any]], int, int, int]:
    """
    Align by matching entry_eng or entry_rus text.
    Returns one row per ground-truth segment (human order), plus (n_human, n_llm, n_matched pair count).
    """
    n_human = len(gt_rows)
    n_llm = len(llm_rows)
    pair_list = _content_match_pairs_rus(gt_rows, llm_rows) if match_rus else _content_match_pairs(gt_rows, llm_rows)
    gt_to_llm = {gt_i: llm_i for gt_i, llm_i in pair_list}
    n_pair = len(pair_list)

    raw_rows: List[Dict[str, Any]] = []
    for gt_i in range(len(gt_rows)):
        gt = gt_rows[gt_i]
        if gt_i in gt_to_llm:
            llm_i = gt_to_llm[gt_i]
            llm = llm_rows[llm_i]
            cat_match = (llm.get("content_category") or "").strip() == (gt.get("content_category") or "").strip()
            fram_match = (llm.get("framing") or "").strip() == (gt.get("framing") or "").strip()
            raw_rows.append({
                "section": llm.get("section", gt.get("section", "")),
                "entry_eng": gt.get("entry_eng", llm.get("entry_eng", "")),
                "entry_rus": gt.get("entry_rus", llm.get("entry_rus", "")),
                "llm_category": llm.get("content_category", ""),
                "llm_framing": llm.get("framing", ""),
                "human_category": gt.get("content_category", ""),
                "human_framing": gt.get("framing", ""),
                "context": llm.get("context", gt.get("context", "")),
                "category_match": cat_match,
                "framing_match": fram_match,
                "both_match": cat_match and fram_match,
                "paired_with_llm": True,
            })
        else:
            raw_rows.append({
                "section": gt.get("section", gt_i + 1),
                "entry_eng": gt.get("entry_eng", ""),
                "entry_rus": gt.get("entry_rus", ""),
                "llm_category": "",
                "llm_framing": "",
                "human_category": gt.get("content_category", ""),
                "human_framing": gt.get("framing", ""),
                "context": gt.get("context", ""),
                "category_match": False,
                "framing_match": False,
                "both_match": False,
                "paired_with_llm": False,
            })

    normalized = [normalize_comparison_row_for_canonical_storage(r) for r in raw_rows]
    return normalized, n_human, n_llm, n_pair


def run(
    llm_by_doc: Dict[str, List[Dict[str, Any]]],
    gt_by_doc: Dict[str, List[Dict[str, Any]]],
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Dict[str, Any]]:
    """
    Align LLM and ground-truth rows per document; compute accuracy.
    When config.compare.match_by is "index", align by row index (legacy).
    When "content_rus", match by entry_rus (Russian); when "content", match by entry_eng.
    """
    compare_cfg = (config or {}).get("compare", {})
    match_by = compare_cfg.get("match_by", "content")
    match_rus = match_by == "content_rus"

    doc_ids = sorted(set(llm_by_doc.keys()) | set(gt_by_doc.keys()))
    result = {}
    for doc_id in doc_ids:
        llm_rows = llm_by_doc.get(doc_id, [])
        gt_rows = gt_by_doc.get(doc_id, [])

        if match_by == "index":
            aligned = _align_by_index(llm_rows, gt_rows)
            n_human = len(gt_rows)
            n_llm = len(llm_rows)
            n_matched = len(aligned)
            total = len(aligned)
            if total == 0:
                cat_pct = fram_pct = both_pct = 0.0
            else:
                cat_pct = 100.0 * sum(1 for r in aligned if r["category_match"]) / total
                fram_pct = 100.0 * sum(1 for r in aligned if r["framing_match"]) / total
                both_pct = 100.0 * sum(1 for r in aligned if r["both_match"]) / total
            result[doc_id] = {
                "aligned_rows": aligned,
                "n_human": n_human,
                "n_llm": n_llm,
                "n_matched": n_matched,
                "category_accuracy_pct": round(cat_pct, 1),
                "framing_accuracy_pct": round(fram_pct, 1),
                "both_match_pct": round(both_pct, 1),
            }
            continue
        aligned, n_human, n_llm, n_matched = _align_by_content(llm_rows, gt_rows, match_rus=match_rus)
        paired_only = [r for r in aligned if r.get("paired_with_llm")]
        if not paired_only:
            cat_pct = fram_pct = both_pct = 0.0
        else:
            cat_pct = 100.0 * sum(1 for r in paired_only if r["category_match"]) / len(paired_only)
            fram_pct = 100.0 * sum(1 for r in paired_only if r["framing_match"]) / len(paired_only)
            both_pct = 100.0 * sum(1 for r in paired_only if r["both_match"]) / len(paired_only)

        result[doc_id] = {
            "aligned_rows": aligned,
            "n_human": n_human,
            "n_llm": n_llm,
            "n_matched": n_matched,
            "category_accuracy_pct": round(cat_pct, 1),
            "framing_accuracy_pct": round(fram_pct, 1),
            "both_match_pct": round(both_pct, 1),
        }
    return result
