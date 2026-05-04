# Experiment B — Free segmentation

## Files you edit

| File | Role |
|------|------|
| **`agent_assessments.json`** | **Primary deliverable.** You choose segment boundaries; fill arrays per document. |
| `agent_assessments.template.json` | Backup skeleton only. |

## Inputs (read-only)

- **`originals_index.json`** — For each document: `document_id`, `display_name`, **`russian_original_project_relative`** (path from repo root to the `.txt` to segment).

Do **not** use `input_segments/` from Experiment A as the segmentation source unless explicitly debugging — Experiment B expects whole-document reading.

## Run pipeline after filling assessments

```bash
export PIPELINE_CONFIG=config/pipeline_config.experiment_redo.json
python run.py --agent-assessments --agent-assessments-file=data/experiments/exp_b_free_segment/agent_assessments.json
```

Compare/report use filtered human GT (`shared/filtered_gt_json`) vs your segments via content alignment (`compare.match_by`: `content_rus` in experiment config).

## Prompts & taxonomy prose

- **`docs/agents/EXPERIMENT_AGENT_PROMPTS.md`** — Experiment B prompts.
- **`data/experiments/shared/TAXONOMY_REFERENCE_FOR_ASSESSORS.md`** — Read before labeling.
