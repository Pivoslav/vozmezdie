# Experiment A — Human-aligned slices

## Files you edit

| File | Role |
|------|------|
| **`agent_assessments.json`** | **Primary deliverable.** Same keys as template; replace each `[]` with assessment rows (see prompts doc). |
| `agent_assessments.template.json` | Reset copy from `prepare_experiment_redo.py`; do not rely on it for edits. |

## Inputs (read-only)

- **`input_segments/<document_id>.json`** — Arrays of `{ section, entry_eng, entry_rus, context }` **without** labels. Row order and boundaries are fixed.

## Doc IDs in this bundle

Same keys as in `agent_assessments.json` (16 documents with GT HTML present).

## Run pipeline after filling assessments

```bash
export PIPELINE_CONFIG=config/pipeline_config.experiment_redo.json
python run.py --agent-assessments --agent-assessments-file=data/experiments/exp_a_human_slices/agent_assessments.json
```

## Prompts & taxonomy prose

- **`docs/agents/EXPERIMENT_AGENT_PROMPTS.md`** — Copy-paste agent prompts.
- **`data/experiments/shared/TAXONOMY_REFERENCE_FOR_ASSESSORS.md`** — Read before labeling (framing Purpose/function + examples from Categories Explained).
