# Next agent: experiment redo (zero guesswork)

**Start here.** File migration and empty `data/output/` are already done. Your job is assessments + pipeline runs using fixed paths below.

---

## 1. What was migrated

| Location | Meaning |
|----------|---------|
| **`data/archive/pre_experiment_redo_2026-05-04_195749Z/output/`** | Full previous **`data/output`** tree (reports, `comparison_results.json`, `agent_assessments.json`, synonym chunks, segment exports, etc.). |
| **`data/archive/pre_experiment_redo_2026-05-04_195749Z/README_RESTORE.txt`** | How to move that folder back to `data/output` if someone needs a literal restore. |

If you see a *different* `pre_experiment_redo_*` folder, use the newest one; the naming pattern is always `data/archive/pre_experiment_redo_<UTC-timestamp>/output/`.

---

## 2. Ground rules (do not skip)

1. **Config for all experiment pipeline runs**

   ```bash
   export PIPELINE_CONFIG=config/pipeline_config.experiment_redo.json
   ```

   Windows PowerShell:

   ```powershell
   $env:PIPELINE_CONFIG="config/pipeline_config.experiment_redo.json"
   ```

   This file sets **`ground_truth.json_rows_dir`** to **`data/experiments/shared/filtered_gt_json`** (filtered human labels for comparison). Do not point the pipeline at raw HTML GT for these runs unless you intentionally change the experiment design.

2. **Taxonomy prose before labeling**  
   Read **`data/experiments/shared/TAXONOMY_REFERENCE_FOR_ASSESSORS.md`** first. It is filtered by **`config/experiment_redo_filter.json`** (e.g. **Generic / Neutral Language** is omitted from allowed framings by default). Use **only** the framing bullets listed under **Allowed framing labels for JSON output** in that file. Regenerate after filter or CE edits:  
   `python scripts/export_assessor_taxonomy_reference.py`  
   (`prepare_experiment_redo.py` runs this when rebuilding bundles.)

3. **No bulk LLM “assessment cheating”**  
   Do **not** produce **`agent_assessments.json`** via **`scripts/assess_segments_ollama.py`**, **`python run.py --use-ollama`**, or any bulk model classification. Reason row-by-row from CE + Russian text; use **`--agent-assessments`** only to **evaluate** your JSON.

4. **Blindness**  
   While producing labels, **do not read** `data/experiments/shared/filtered_gt_json/*.json`. Those are for automated compare only after your `agent_assessments.json` is filled.

5. **Row shape**  
   Each assessment row must match pipeline/LLM rows:  
   `section`, `entry_eng`, `entry_rus`, `content_category`, `framing`, `context`.  
   **`framing`** must be one of the allowlisted strings from **`TAXONOMY_REFERENCE_FOR_ASSESSORS.md`** (not everything in **`config/taxonomy.json`**).

---

## 3. Experiment A — same segments as humans (fixed slices)

| Item | Path |
|------|------|
| **READ** blind inputs | `data/experiments/exp_a_human_slices/input_segments/<document_id>.json` |
| **EDIT** deliverable | **`data/experiments/exp_a_human_slices/agent_assessments.json`** |
| Folder README | `data/experiments/exp_a_human_slices/README.md` |

**Rules:** One output row per input segment; **same order** and **same boundaries** as the JSON lists.

**After editing:**

```bash
export PIPELINE_CONFIG=config/pipeline_config.experiment_redo.json
python run.py --agent-assessments --agent-assessments-file=data/experiments/exp_a_human_slices/agent_assessments.json
```

**Report-only later:**

```bash
export PIPELINE_CONFIG=config/pipeline_config.experiment_redo.json
python run_report_only.py
```

(`run_report_only.py` respects `PIPELINE_CONFIG` for defaults.)

---

## 4. Experiment B — free segmentation

Folder on disk: **`data/experiments/exp_b_free_segment/`** (this *is* Experiment B; naming is historical).

| Item | Path |
|------|------|
| **READ** document list + Russian paths | **`data/experiments/exp_b_free_segment/originals_index.json`** (field `russian_original_project_relative`) |
| **EDIT** deliverable | **`data/experiments/exp_b_free_segment/agent_assessments.json`** |
| Folder README | `data/experiments/exp_b_free_segment/README.md` |

**Rules:** Segment each full Russian `.txt` yourself; schema same as pipeline rows.

**After editing:**

Use **`config/pipeline_config.experiment_b.json`** so the Research Lab UI reads ``Experiment B``, assessments default to this folder, and outputs land in **`data/experiments/exp_b_free_segment/pipeline_output/`** (without overwriting Experiment A under ``data/output``):

```bash
export PIPELINE_CONFIG=config/pipeline_config.experiment_b.json
python run.py --agent-assessments --agent-assessments-file=data/experiments/exp_b_free_segment/agent_assessments.json
```

The shared redo config (**`pipeline_config.experiment_redo.json`**) remains the default for **Experiment A** (human-aligned slices). For Experiment B only, avoid relying on that file unless you override paths and UI strings manually.

See **`data/experiments/exp_b_free_segment/README.md`** for preliminary HTML vs full report and report-only commands.

## 5. Audit / counts

- **`data/experiments/shared/FILTER_MANIFEST.json`** — How many HTML rows were dropped (deprecated categories, structural sheet labels, optional generic-neutral framing) vs kept per document.

---

## 6. Changing filters or rebuilding artifacts

- Rules: **`config/experiment_redo_filter.json`**
- Regenerate filtered GT + Experiment A segments + templates:

  ```bash
  python scripts/prepare_experiment_redo.py --no-archive
  ```

  **`agent_assessments.json`** is **only created when missing** (so your filled files are not overwritten). **`agent_assessments.template.json`** is refreshed every run.

- To archive **`data/output`** again before a clean pipeline run:

  ```bash
  python scripts/prepare_experiment_redo.py
  ```

---

## 7. Copy-paste prompts & taxonomy detail

**`docs/agents/EXPERIMENT_AGENT_PROMPTS.md`** — full prompts for Experiment A and Experiment B agents.

---

## 8. Layout map

```
data/
  archive/pre_experiment_redo_<stamp>/output/   ← old pipeline outputs
  output/README.md                               ← expects regen via pipeline
  experiments/
    README.md
    shared/filtered_gt_json/                     ← pipeline GT only (do not peek blind)
    shared/FILTER_MANIFEST.json
    shared/TAXONOMY_REFERENCE_FOR_ASSESSORS.md     ← framing/category prose for assessors (regenerated from CE)
    exp_a_human_slices/input_segments/
    exp_a_human_slices/agent_assessments.json    ← Experiment A fill this
    exp_b_free_segment/originals_index.json
    exp_b_free_segment/agent_assessments.json    ← Experiment B fill this
config/
  pipeline_config.experiment_redo.json           ← PIPELINE_CONFIG target
  experiment_redo_filter.json
```

---

You do **not** need to rerun archival migration unless you deliberately choose **`prepare_experiment_redo.py`** without `--no-archive` again.
