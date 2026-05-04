#!/usr/bin/env python3
"""
Archive current data/output, build filtered ground-truth JSON for both experiments,
and emit Experiment A blind segment lists plus Experiment B document index.

Usage (from repo root):
  python scripts/prepare_experiment_redo.py           # archive + rebuild artifacts
  python scripts/prepare_experiment_redo.py --no-archive

Reads HTML ground truth from config in PIPELINE_CONFIG or defaults to config/pipeline_config.experiment_redo.json.
Filter rules: config/experiment_redo_filter.json.
Writes **`agent_assessments.template.json`** always; **`agent_assessments.json`** only if missing (preserves filled assessments).
Regenerates **`data/experiments/shared/TAXONOMY_REFERENCE_FOR_ASSESSORS.md`** from Categories Explained.html (framing + category prose for agents).

Canonical checklist for the next agent: **`docs/agents/NEXT_AGENT_EXPERIMENT_SETUP.md`**.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.taxonomy_categories import DEPRECATED_CONTENT_CATEGORIES, display_framing_for_ui
from ground_truth import _load_taxonomy_for_filter, _redirect_gt_content_categories
from ground_truth.html_loader import load_ground_truth_from_html


FILTER_REL = ROOT / "config" / "experiment_redo_filter.json"
SHARED = ROOT / "data" / "experiments" / "shared"
FILTERED_GT = SHARED / "filtered_gt_json"
EXP_A = ROOT / "data" / "experiments" / "exp_a_human_slices"
EXP_B = ROOT / "data" / "experiments" / "exp_b_free_segment"

STRUCTURAL_SHEET_LABELS = frozenset({"Archival Record Data", "Body of the Text"})
GENERIC_FRAMING_CANONICAL = "Generic / Neutral Language"


def _load_pipeline_config(config_arg: Optional[Path]) -> dict:
    if config_arg and config_arg.exists():
        return json.loads(config_arg.read_text(encoding="utf-8"))
    exp_path = ROOT / "config" / "pipeline_config.experiment_redo.json"
    if exp_path.exists():
        return json.loads(exp_path.read_text(encoding="utf-8"))
    return json.loads((ROOT / "config" / "pipeline_config.example.json").read_text(encoding="utf-8"))


def _find_gt_html(html_dir: Path, doc_id: str) -> Optional[Path]:
    for candidate in (html_dir / f"{doc_id}.html", html_dir / f"{doc_id.replace('_', ' ')}.html"):
        if candidate.exists():
            return candidate
    return None


def _document_ids() -> List[str]:
    dm_path = ROOT / "config" / "document_map.json"
    dm = json.loads(dm_path.read_text(encoding="utf-8"))
    return [str(d["document_id"]) for d in dm.get("documents", [])]


def _russian_original_relpath(doc_entry: Dict[str, Any]) -> str:
    display = doc_entry.get("display_name") or f'{doc_entry.get("document_id", "")}.txt'
    return f"data/russian_originals/{display}"


def _merge_drop_raw(cfg: Dict[str, Any]) -> Set[str]:
    out = set(DEPRECATED_CONTENT_CATEGORIES)
    if cfg.get("drop_archival_and_body_sheet_labels", True):
        out |= set(STRUCTURAL_SHEET_LABELS)
    extra = cfg.get("drop_raw_content_categories_extra") or []
    out |= {str(x).strip() for x in extra if str(x).strip()}
    return out


def _drop_reason(
    raw_cat: str,
    raw_fram: str,
    drop_raw: Set[str],
    drop_generic_framing: bool,
) -> Optional[str]:
    c = (raw_cat or "").strip()
    if c in drop_raw:
        return "category_policy"
    if drop_generic_framing:
        if display_framing_for_ui(raw_fram).strip() == GENERIC_FRAMING_CANONICAL:
            return "generic_neutral_framing"
    return None


def _finalize_rows(rows: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    valid = _load_taxonomy_for_filter(config, ROOT)
    if not valid:
        return rows
    redirected = _redirect_gt_content_categories(rows)
    return [r for r in redirected if (r.get("content_category") or "").strip() in valid]


def archive_output(no_archive: bool) -> Optional[Path]:
    src = ROOT / "data" / "output"
    if no_archive or not src.exists():
        if no_archive:
            print("--no-archive: leaving data/output in place.")
        else:
            print("No data/output; skipping archive.")
        return None
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%SZ")
    archive_parent = ROOT / "data" / "archive" / f"pre_experiment_redo_{stamp}"
    dst = archive_parent / "output"
    archive_parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    src.mkdir(parents=True, exist_ok=True)
    note = archive_parent / "README_RESTORE.txt"
    note.write_text(
        "This folder holds the former contents of data/output before prepare_experiment_redo.py ran.\n"
        "To restore manually (destructive): move archive/pre_experiment_redo_*/output back to data/output .\n",
        encoding="utf-8",
    )
    print(f"Archived previous output -> {dst}")
    return archive_parent


def main() -> int:
    ap = argparse.ArgumentParser(description="Prepare filtered GT + experiment input bundles.")
    ap.add_argument("--no-archive", action="store_true", help="Do not move data/output to archive.")
    ap.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Pipeline JSON for taxonomy paths / html_dir (default: experiment redo config)",
    )
    args = ap.parse_args()

    cfg_filter_path = FILTER_REL
    filter_cfg = json.loads(cfg_filter_path.read_text(encoding="utf-8")) if cfg_filter_path.exists() else {}
    drop_raw = _merge_drop_raw(filter_cfg)
    drop_generic_framing = bool(filter_cfg.get("drop_generic_neutral_framing_rows", True))

    pipe = _load_pipeline_config(args.config)
    gt_cfg = pipe.get("ground_truth", {})
    html_dir_s = gt_cfg.get("html_dir", "data/ground_truth/html")
    html_dir = Path(html_dir_s)
    if not html_dir.is_absolute():
        html_dir = ROOT / html_dir

    archive_output(bool(args.no_archive))

    FILTERED_GT.mkdir(parents=True, exist_ok=True)
    (EXP_A / "input_segments").mkdir(parents=True, exist_ok=True)
    EXP_B.mkdir(parents=True, exist_ok=True)

    pipe_path = args.config if args.config is not None else (ROOT / "config" / "pipeline_config.experiment_redo.json")
    if not pipe_path.is_absolute():
        pipe_path = ROOT / pipe_path

    manifest: Dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "filter_config": str(FILTER_REL.relative_to(ROOT)),
        "pipeline_config_used": str(pipe_path.relative_to(ROOT)),
        "documents": {},
    }

    doc_entries = json.loads((ROOT / "config" / "document_map.json").read_text(encoding="utf-8")).get("documents", [])
    by_id = {str(d["document_id"]): d for d in doc_entries}

    prepared_docs: List[str] = []
    originals_index: List[Dict[str, Any]] = []

    for doc_id in _document_ids():
        html_path = _find_gt_html(html_dir, doc_id)
        if html_path is None:
            manifest["documents"][doc_id] = {"status": "skipped", "reason": "no_gt_html"}
            continue

        raw_rows = load_ground_truth_from_html(html_path)
        stats = {"status": "ok", "html_rows": len(raw_rows), "dropped_category_policy": 0, "dropped_generic_neutral_framing": 0}
        kept: List[Dict[str, Any]] = []

        for r in raw_rows:
            rc = (r.get("content_category") or "").strip()
            rf = (r.get("framing") or "").strip()
            reason = _drop_reason(rc, rf, drop_raw, drop_generic_framing)
            if reason == "category_policy":
                stats["dropped_category_policy"] += 1
                continue
            if reason == "generic_neutral_framing":
                stats["dropped_generic_neutral_framing"] += 1
                continue
            kept.append(dict(r))

        finalized = _finalize_rows(kept, pipe)
        stats["kept_after_policy_filters"] = len(kept)
        stats["final_rows_after_taxonomy_filter"] = len(finalized)
        manifest["documents"][doc_id] = stats

        if not finalized:
            manifest["documents"][doc_id]["status"] = "empty_after_filter"
            continue

        prepared_docs.append(doc_id)
        out_gt = FILTERED_GT / f"{doc_id}.json"
        out_gt.write_text(json.dumps(finalized, indent=2, ensure_ascii=False), encoding="utf-8")

        blind_segments = [
            {
                "section": r.get("section"),
                "entry_eng": r.get("entry_eng", ""),
                "entry_rus": r.get("entry_rus", ""),
                "context": r.get("context", (r.get("entry_eng") or "")[:200]),
            }
            for r in finalized
        ]
        seg_path = EXP_A / "input_segments" / f"{doc_id}.json"
        seg_path.write_text(json.dumps(blind_segments, indent=2, ensure_ascii=False), encoding="utf-8")

        entry = by_id.get(doc_id)
        if entry:
            originals_index.append(
                {
                    "document_id": doc_id,
                    "display_name": entry.get("display_name"),
                    "russian_original_project_relative": _russian_original_relpath(entry),
                    "rus_filename_source_of_truth": entry.get("rus_filename"),
                }
            )

    SHARED.mkdir(parents=True, exist_ok=True)
    (SHARED / "FILTER_MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    (EXP_B / "originals_index.json").write_text(
        json.dumps({"documents": originals_index}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    empty_aa = {doc_id: [] for doc_id in sorted(prepared_docs)}
    empty_aa_json = json.dumps(empty_aa, indent=2, ensure_ascii=False)
    for dest in (
        EXP_A / "agent_assessments.template.json",
        EXP_B / "agent_assessments.template.json",
    ):
        dest.write_text(empty_aa_json, encoding="utf-8")
    for exp_dir in (EXP_A, EXP_B):
        assessment_path = exp_dir / "agent_assessments.json"
        if not assessment_path.exists():
            assessment_path.write_text(empty_aa_json, encoding="utf-8")

    export_script = ROOT / "scripts" / "export_assessor_taxonomy_reference.py"
    if export_script.exists():
        try:
            subprocess.run([sys.executable, str(export_script)], cwd=str(ROOT), check=True)
        except subprocess.CalledProcessError:
            print(
                "Warning: export_assessor_taxonomy_reference.py failed; "
                "see config/Categories Explained.html for full taxonomy prose.",
            )

    print(f"Wrote filtered GT -> {FILTERED_GT} ({len(prepared_docs)} documents)")
    print(f"Experiment A blind segments -> {EXP_A / 'input_segments'}")
    print(f"Experiment B index -> {EXP_B / 'originals_index.json'}")
    print(f"Manifest -> {SHARED / 'FILTER_MANIFEST.json'}")
    print()
    print("Next: set PIPELINE_CONFIG=config/pipeline_config.experiment_redo.json then run the pipeline with")
    print("  python run.py --agent-assessments --agent-assessments-file=<path/to/assessments.json>")
    print("See docs/agents/NEXT_AGENT_EXPERIMENT_SETUP.md for paths and docs/agents/EXPERIMENT_AGENT_PROMPTS.md for prompts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
