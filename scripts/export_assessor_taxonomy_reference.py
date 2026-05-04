#!/usr/bin/env python3
"""
Emit a readable Markdown digest of Categories Explained.html for experiment assessors.

Includes Purpose/Function (and examples text where parsed) for each framing strategy and
each allowed content category — richer context than taxonomy.json ids alone.

Respects config/experiment_redo_filter.json:
  assessor_excluded_framing_strategies / assessor_excluded_content_categories
  When drop_generic_neutral_framing_rows is true and assessor_allow_generic_neutral_framing
  is false, Generic / Neutral Language is excluded from the digest (aligned with GT policy).

Output ends with explicit **Allowed … labels for JSON output** lists for both content categories
and framing (exact strings assessors should paste into agent_assessments.json).

Usage:
  python scripts/export_assessor_taxonomy_reference.py

Output:
  data/experiments/shared/TAXONOMY_REFERENCE_FOR_ASSESSORS.md
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Set

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.taxonomy_categories import (
    display_content_category_for_ui,
    display_framing_for_ui,
)
from config.taxonomy_from_html import load_taxonomy_from_html

FILTER_JSON = ROOT / "config" / "experiment_redo_filter.json"


def _load_filter_cfg() -> Dict[str, Any]:
    if not FILTER_JSON.exists():
        return {}
    try:
        return json.loads(FILTER_JSON.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _assessor_excluded_framing_canonical(cfg: Dict[str, Any]) -> Set[str]:
    """Canonical framing ids excluded from assessor digest and allowed labels."""
    out: Set[str] = set()
    for x in cfg.get("assessor_excluded_framing_strategies") or []:
        s = str(x).strip()
        if not s:
            continue
        out.add(display_framing_for_ui(s))
        out.add(s)
    allow_generic = bool(cfg.get("assessor_allow_generic_neutral_framing"))
    drop_generic_gt = bool(cfg.get("drop_generic_neutral_framing_rows"))
    if drop_generic_gt and not allow_generic:
        out.add("Generic / Neutral Language")
        out.add(display_framing_for_ui("Generic"))
        out.add(display_framing_for_ui("Generic / Neutral"))
    return {x for x in out if x}


def _assessor_excluded_category_canonical(cfg: Dict[str, Any]) -> Set[str]:
    out: Set[str] = set()
    for x in cfg.get("assessor_excluded_content_categories") or []:
        s = str(x).strip()
        if not s:
            continue
        out.add(display_content_category_for_ui(s))
        out.add(s)
    return {x for x in out if x}


def _framing_allowed_for_digest(fid: str, excluded_canon: Set[str]) -> bool:
    canon = display_framing_for_ui(fid)
    if not canon:
        return False
    if canon in excluded_canon:
        return False
    if fid.strip() in excluded_canon:
        return False
    return True


def _category_allowed_for_digest(cid: str, excluded_canon: Set[str]) -> bool:
    canon = display_content_category_for_ui(cid)
    if not canon:
        return False
    if canon in excluded_canon:
        return False
    if cid.strip() in excluded_canon:
        return False
    return True


def _allowed_framing_ids_from_taxonomy_json(json_path: Path) -> Set[str]:
    if not json_path.exists():
        return set()
    data = json.loads(json_path.read_text(encoding="utf-8"))
    return {str(f.get("id") or "").strip() for f in data.get("framing_strategies", []) if f.get("id")}


def _allowed_category_ids_from_taxonomy_json(json_path: Path) -> Set[str]:
    if not json_path.exists():
        return set()
    data = json.loads(json_path.read_text(encoding="utf-8"))
    return {str(c.get("id") or "").strip() for c in data.get("content_categories", []) if c.get("id")}


def _esc(s: str) -> str:
    return (s or "").replace("\r\n", "\n").strip()


def write_reference_markdown(out_path: Path) -> None:
    cfg = _load_filter_cfg()
    excluded_fram = _assessor_excluded_framing_canonical(cfg)
    excluded_cat = _assessor_excluded_category_canonical(cfg)

    ce_path = ROOT / "config" / "Categories Explained.html"
    merge_path = ROOT / "config" / "taxonomy.json"
    tax = load_taxonomy_from_html(ce_path, merge_path if merge_path.exists() else None)
    json_allowed_fram = _allowed_framing_ids_from_taxonomy_json(merge_path)
    json_allowed_cat = _allowed_category_ids_from_taxonomy_json(merge_path)

    lines: list[str] = []
    lines.append("# Taxonomy reference for assessors")
    lines.append("")
    lines.append(
        "Auto-generated from **`config/Categories Explained.html`** (merged with `config/taxonomy.json`). "
        "Framing strategies and categories below follow **`config/experiment_redo_filter.json`**: "
        "some CE labels may be omitted when they are excluded from experiment assessments."
    )
    if excluded_fram:
        lines.append("")
        lines.append(
            "**Excluded framing for this experiment (do not assign):** "
            + ", ".join(sorted(set(excluded_fram)))
            + "."
        )
    if excluded_cat:
        lines.append("")
        lines.append(
            "**Excluded content categories for this experiment (do not assign):** "
            + ", ".join(sorted(set(excluded_cat)))
            + "."
        )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Content categories")
    lines.append("")
    lines.append(
        "Choose **exactly one** content category per segment **from the headings below only**. "
        "Compare segments against **Purpose** text and **Examples** — not the label name alone."
    )
    lines.append("")
    kept_categories: list[str] = []
    for c in tax.get("content_categories", []):
        cid = _esc(str(c.get("id") or c.get("label_en") or ""))
        if not cid:
            continue
        if json_allowed_cat and cid not in json_allowed_cat:
            continue
        if not _category_allowed_for_digest(cid, excluded_cat):
            continue
        kept_categories.append(cid)
        lines.append(f"### {cid}")
        desc = _esc(str(c.get("description") or ""))
        if desc:
            lines.append("")
            lines.append(desc)
        ex = _esc(str(c.get("examples") or ""))
        if ex:
            lines.append("")
            lines.append(f"**Examples (from CE):** {ex}")
        lines.append("")
    lines.append("**Allowed content category labels for JSON output (exact strings):**")
    lines.append("")
    if kept_categories:
        for k in kept_categories:
            lines.append(f"- `{k}`")
    else:
        lines.append("*None after filters — fix config/Categories Explained.html or experiment_redo_filter.json.*")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Framing strategies (experiment allowlist)")
    lines.append("")
    lines.append(
        "Choose **exactly one** framing label per segment **from the headings below only**. "
        "Compare segments against **Purpose / function** and **Examples** — not the label name alone."
    )
    lines.append("")
    kept_framings: list[str] = []
    for f in tax.get("framing_strategies", []):
        fid = _esc(str(f.get("id") or f.get("label_en") or ""))
        if not fid:
            continue
        if json_allowed_fram and fid not in json_allowed_fram:
            continue
        if not _framing_allowed_for_digest(fid, excluded_fram):
            continue
        kept_framings.append(fid)
        lines.append(f"### {fid}")
        func = _esc(str(f.get("description") or ""))
        if func:
            lines.append("")
            lines.append(f"**Purpose / function:** {func}")
        ex = _esc(str(f.get("examples") or ""))
        if ex:
            lines.append("")
            lines.append(f"**Typical use / examples:** {ex}")
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("**Allowed framing labels for JSON output (exact strings):**")
    lines.append("")
    if kept_framings:
        for k in kept_framings:
            lines.append(f"- `{k}`")
    else:
        lines.append("*None after filters — fix config/Categories Explained.html or experiment_redo_filter.json.*")
    lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    out_path.write_text(text, encoding="utf-8")


def main() -> int:
    out = ROOT / "data" / "experiments" / "shared" / "TAXONOMY_REFERENCE_FOR_ASSESSORS.md"
    write_reference_markdown(out)
    print(f"Wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
