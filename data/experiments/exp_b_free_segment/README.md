# Experiment B — Free segmentation

**Experiment B** in the repo lives in this folder: **`data/experiments/exp_b_free_segment/`** (not a separate `exp_b/` path). Same 18 document IDs as Experiment A; segmentation and row order are **assessor-defined** from full Russian originals.

| | Experiment A (`exp_a_human_slices/`) | Experiment B (this folder) |
|---|--------------------------------------|------------------------------|
| Segments | Fixed slices in `input_segments/*.json` | You split `data/russian_originals/*.txt` as you judge fit |
| Primary read | Slice rows (+ Russian gloss) | Whole document `.txt` from `originals_index.json` |
| Taxonomy | `shared/TAXONOMY_REFERENCE_FOR_ASSESSORS.md` (same allowlists) | Same |

## Files you edit

| File | Role |
|------|------|
| **`agent_assessments.json`** | **Primary deliverable.** You choose segment boundaries; fill arrays per document. |
| `agent_assessments.template.json` | Backup skeleton only. |

## Inputs (read-only)

- **`originals_index.json`** — For each document: `document_id`, `display_name`, **`russian_original_project_relative`** (path from repo root to the `.txt` to segment).

Do **not** use `input_segments/` from Experiment A as the segmentation source unless explicitly debugging — Experiment B expects whole-document reading.

## Integrate after assessments are complete

**Two artefacts serve different roles:**

| Artefact | Purpose |
|----------|---------|
| **`preliminary_results.html`** | Static browse of segment boundaries and label marginals only (no GT comparison). Regenerate: `python scripts/exp_b_preliminary_html.py`. |
| **Research Lab HTML + `comparison_results.json`** | Full comparator against filtered expert GT (`shared/filtered_gt_json`), content-aligned on Russian (`compare.match_by`: `content_rus`). Written under **`pipeline_output/`** when using the Experiment B config below so **`data/output`** is left untouched. **`pipeline_config.example.json`** / **`experiment_redo`** load this path as **`report.secondary_comparison_json`** so the main report's Research Lab can toggle corpus-level charts vs Experiment A. |

**Recommended pipeline command** (writes `pipeline_output/manual_analysis_report.html`, `pipeline_output/comparison_results.json`, etc.):

```bash
export PIPELINE_CONFIG=config/pipeline_config.experiment_b.json
python run.py --agent-assessments --agent-assessments-file=data/experiments/exp_b_free_segment/agent_assessments.json
```

Report-only refresh after editing report code:

```bash
export PIPELINE_CONFIG=config/pipeline_config.experiment_b.json
python run_report_only.py data/experiments/exp_b_free_segment/pipeline_output/comparison_results.json
```

To compare **Experiment A vs Experiment B** formally, keep **two** JSON exports side by side (`exp_a_human_slices` run → archive or default `data/output`; Experiment B → `pipeline_output/comparison_results.json`) and diff aggregates in analysis or the whitepaper; the single-site UI is one experiment at a time.

Legacy single-config invocation (still works but labels the UI as Experiment A unless you edit `pipeline_config.experiment_redo.json`):

```bash
export PIPELINE_CONFIG=config/pipeline_config.experiment_redo.json
python run.py --agent-assessments --agent-assessments-file=data/experiments/exp_b_free_segment/agent_assessments.json
```

## Prompts & taxonomy prose

- **`docs/agents/EXPERIMENT_AGENT_PROMPTS.md`** — Experiment B prompts.
- **`data/experiments/shared/TAXONOMY_REFERENCE_FOR_ASSESSORS.md`** — Read before labeling.
