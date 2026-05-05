# Experiments layout (redo)

Read **`docs/agents/NEXT_AGENT_EXPERIMENT_SETUP.md`** first — single checklist with exact paths and commands.

| Path | Purpose |
|------|---------|
| **`shared/filtered_gt_json/`** | Human GT rows **after** policy filters + taxonomy cleanup. Pipeline GT only (**do not read while assessing**). Used by **`pipeline_config.experiment_redo.json`** (Experiment A) and **`pipeline_config.experiment_b.json`** (Experiment B). |
| **`shared/TAXONOMY_REFERENCE_FOR_ASSESSORS.md`** | Framing + category prose extracted from **`config/Categories Explained.html`** — **read before labeling**. |
| **`shared/README.md`** | Short notes on shared artifacts. |
| **`exp_a_human_slices/`** | **Experiment A:** fixed segment boundaries (`input_segments/`) + assessments. Typical **`PIPELINE_CONFIG`**: `experiment_redo`; outputs often **`data/output/`**. |
| **`exp_b_free_segment/`** | **Experiment B:** same doc set; read full `data/russian_originals/*.txt` (see `originals_index.json`), **you** choose segment boundaries + labels. Recommended **`PIPELINE_CONFIG`**: **`experiment_b`**; comparator outputs under **`exp_b_free_segment/pipeline_output/`**. |

Previous `data/output/` lives under **`data/archive/pre_experiment_redo_*/output`**.
