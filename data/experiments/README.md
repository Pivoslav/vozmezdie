# Experiments layout (redo)

Read **`docs/agents/NEXT_AGENT_EXPERIMENT_SETUP.md`** first — single checklist with exact paths and commands.

| Path | Purpose |
|------|---------|
| **`shared/filtered_gt_json/`** | Human GT rows **after** policy filters + taxonomy cleanup. Used **only by the pipeline** (`PIPELINE_CONFIG=config/pipeline_config.experiment_redo.json`). **Do not read while assessing.** |
| **`shared/TAXONOMY_REFERENCE_FOR_ASSESSORS.md`** | Framing + category prose extracted from **`config/Categories Explained.html`** — **read before labeling**. |
| **`shared/README.md`** | Short notes on shared artifacts. |
| **`exp_a_human_slices/`** | Experiment A: fixed human segment boundaries — blind inputs + assessments file. |
| **`exp_b_free_segment/`** | Experiment B: full-document Russian texts — assessments file + index of paths. |

Previous `data/output/` lives under **`data/archive/pre_experiment_redo_*/output`**.
