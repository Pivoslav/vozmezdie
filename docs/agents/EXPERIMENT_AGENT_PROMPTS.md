# Experiment redo: agent prompts (human slices vs free segmentation)

This guide complements **`docs/agents/NEXT_AGENT_EXPERIMENT_SETUP.md`** (exact paths and commands). Migration is done: former outputs live under **`data/archive/pre_experiment_redo_*/output`**; edit **`agent_assessments.json`** under each experiment folder.

To regenerate filtered GT + segments **without** archiving output again:

```bash
python scripts/prepare_experiment_redo.py --no-archive
```

Pipeline runs for evaluation should use:

```bash
export PIPELINE_CONFIG=config/pipeline_config.experiment_redo.json
# Windows (PowerShell): $env:PIPELINE_CONFIG="config/pipeline_config.experiment_redo.json"
python run.py --agent-assessments --agent-assessments-file=PATH_TO_YOUR_ASSESSMENTS.json
```

Use **different** assessment filenames for each experiment (copy from `agent_assessments.template.json` in the experiment folder).

---

## Shared rules for both agents

1. **Taxonomy**  
   - **Content categories:** Use **only** the headings under **Content categories** and the bullet list **Allowed content category labels for JSON output** in **`data/experiments/shared/TAXONOMY_REFERENCE_FOR_ASSESSORS.md`** (exact strings). Deprecated sheet-only labels (for example Information, Methods, Context and Concepts) are **not** in that file — they were removed from experiment GT and must **not** appear in assessments.  
   - **Framing strategies:** Use **only** the framing headings and **Allowed framing labels for JSON output** at the bottom of the same digest (exact strings).  
     By default **`Generic / Neutral Language` is not allowed** when `drop_generic_neutral_framing_rows` is true and `assessor_allow_generic_neutral_framing` is false — even though CE HTML may still describe it for corpus literacy.  
     Add more exclusions via **`assessor_excluded_framing_strategies`** / **`assessor_excluded_content_categories`**.  
     Regenerate the digest after editing that file: `python scripts/export_assessor_taxonomy_reference.py`.

2. **Mandatory definitions before labeling (do not skip)**  
   Flat label lists are **not** enough for reliable framing work.

   - Read **`data/experiments/shared/TAXONOMY_REFERENCE_FOR_ASSESSORS.md`** end-to-end first. It reflects **`config/experiment_redo_filter.json`**: prose and **allowed label lists** only for categories and framings permitted in this experiment (others may appear in CE but are omitted here).
   - Keep **`config/Categories Explained.html`** open if you want the full sheet layout or to resolve edge cases—the Markdown digest is a companion, not a replacement for primary material when in doubt.  
   - **`config/taxonomy.json`** supplies canonical ids and colours only; it does **not** replace the prose in CE.

   Regenerate the digest after CE changes:

   ```bash
   python scripts/export_assessor_taxonomy_reference.py
   ```

   (`scripts/prepare_experiment_redo.py` runs this automatically when you rebuild experiment bundles.)

3. **Language**  
   Base judgments on the **Russian** originals under `data/russian_originals/` (see `originals_index.json` for Experiment B paths). English snippets are supporting glosses only.

4. **Blindness**  
   Do **not** open filtered ground-truth JSON under `data/experiments/shared/filtered_gt_json/` while assessing. Those files exist only for pipeline comparison after your assessment is written.

5. **No automation — do not “cheat” with bulk LLM labeling**  
   Experiment assessments must come from **your** reasoning using CE + **`TAXONOMY_REFERENCE_FOR_ASSESSORS.md`** + Russian originals — **not** from piping segments through Ollama or another model to fill JSON.

   **Forbidden for producing `agent_assessments.json`:** running **`scripts/assess_segments_ollama.py`**, bulk classification scripts, or asking an LLM API to emit the whole assessment file.  
   **Forbidden command pattern:** `python run.py --use-ollama` (or any path that generates assessments via the pipeline LLM instead of **`--agent-assessments`** + your JSON).  

   **Allowed workflow:** manual Cursor/agent reasoning row-by-row (or careful human oversight equivalent), then **`python run.py --agent-assessments --agent-assessments-file=…`** only to **evaluate** against filtered GT.

6. **Output shape**  
   Produce rows identical to LLM/agent pipeline rows:

   ```json
   {
     "section": <number>,
     "entry_eng": "...",
     "entry_rus": "...",
     "content_category": "<taxonomy category>",
     "framing": "<taxonomy framing>",
     "context": "short quote / rationale"
   }
   ```

   Merge into one JSON object keyed by `document_id`, same shape as `data/output/agent_assessments.json`.

---

## Experiment A — Human-aligned slices (fixed boundaries)

### Inputs

For each document, load:

`data/experiments/exp_a_human_slices/input_segments/<document_id>.json`

Each item provides **only**: `section`, `entry_eng`, `entry_rus`, `context` (no human labels).

### Task

For **each segment exactly as provided**:

1. Choose **content_category** and **framing** by comparing the segment to **Purpose / function** and **examples** in **`data/experiments/shared/TAXONOMY_REFERENCE_FOR_ASSESSORS.md`** (not by label alone). Keep **`config/Categories Explained.html`** handy for ambiguous cases.
2. Assign **one** `content_category` and **one** `framing` using **only** labels allowed in **`TAXONOMY_REFERENCE_FOR_ASSESSORS.md`** (exact spelling).
3. Treat segment boundaries as **fixed**. Do not merge or split rows.
4. Use `context` to cite the minimal phrase from the Russian original that supports the classification.

### Deliverable

- Copy `data/experiments/exp_a_human_slices/agent_assessments.template.json` to e.g. `data/experiments/exp_a_human_slices/agent_assessments.json`.
- Fill every listed document key with the full row array (same length and order as the corresponding `input_segments` file).
- Save UTF-8 JSON.

### Cursor / chat prompt (paste as system or first message)

You are an archival-document annotation assistant for the Vozmezdie Cold War corpus.

Hard constraints:
- Before labeling any segment, read **`data/experiments/shared/TAXONOMY_REFERENCE_FOR_ASSESSORS.md`** (category + framing definitions and both **Allowed … labels for JSON output** lists). Use **`config/Categories Explained.html`** when anything is unclear.
- Use **only** content category strings from **Allowed content category labels for JSON output** in that digest (exact spelling). Do **not** use deprecated sheet-only labels that were dropped from experiment GT.
- Use **only** framing strings from **Allowed framing labels for JSON output** in the same file (default excludes Generic / Neutral Language). Do **not** invent framing labels.
- Do **not** run Ollama, `assess_segments_ollama.py`, or bulk LLM classification to produce this JSON — row-by-row reasoning only.
- Never open or read `data/experiments/shared/filtered_gt_json/` or **`data/ground_truth/html/`** (per-document coding sheets). **`config/Categories Explained.html`** is the taxonomy definition guide — read it freely alongside **`data/experiments/shared/TAXONOMY_REFERENCE_FOR_ASSESSORS.md`**.

Task — Experiment A (human-aligned slices):
1. For document IDs present in `data/experiments/exp_a_human_slices/agent_assessments.template.json`, load `input_segments/<document_id>.json`.
2. For each segment in order, read the matching Russian text in `data/russian_originals/` using filenames from `config/document_map.json`.
3. Output one assessment row per input segment with fields: section, entry_eng, entry_rus, content_category, framing, context.
4. Do not merge or split segments; preserve order and section numbers from the input file.
5. Write merged JSON to `data/experiments/exp_a_human_slices/agent_assessments.json` (same top-level keys as the template).

Before finishing, verify row counts match each `input_segments` file.

---

## Experiment B — Free segmentation

### Inputs

1. `data/experiments/exp_b_free_segment/originals_index.json` — document ids and paths to Russian `.txt` files (project-relative).
2. Full document text only — **no** pre-cut segment list.

### Task

1. Read **`data/experiments/shared/TAXONOMY_REFERENCE_FOR_ASSESSORS.md`** (and **`config/Categories Explained.html`** as needed) before deciding boundaries or labels.
2. Read each Russian original end-to-end.
3. **Segment the document yourself**: divide into meaningful phrases/clauses for extraction (you may differ from human boundary choices).
4. For **each** segment you create, assign `content_category` and `framing` using CE-aligned definitions (exact pipeline strings).
5. Number `section` sequentially from 1 within each document (or keep a stable scheme you document in a short note field inside `context` if needed).
6. `entry_eng` / `entry_rus` should quote your segment in both languages when possible; if only Russian is available, leave `entry_eng` empty only when unavoidable.

### Deliverable

- Copy `data/experiments/exp_b_free_segment/agent_assessments.template.json` to e.g. `data/experiments/exp_b_free_segment/agent_assessments.json`.
- Replace each document’s empty array with your segmented rows.
- Ensure JSON is valid UTF-8.

### Cursor / chat prompt (paste as system or first message)

You are an archival-document annotation assistant for the Vozmezdie Cold War corpus.

Hard constraints:
- Before segmenting or labeling, read **`data/experiments/shared/TAXONOMY_REFERENCE_FOR_ASSESSORS.md`** (categories + framings; both **Allowed … labels for JSON output** lists). Use **`config/Categories Explained.html`** when unclear.
- Content categories: **only** strings listed under **Allowed content category labels for JSON output** (exact spelling). No deprecated sheet-only categories removed from experiment GT.
- Framing: **only** strings under **Allowed framing labels for JSON output**. Default excludes Generic / Neutral Language.
- Do **not** use Ollama, `assess_segments_ollama.py`, or bulk LLM labeling to generate assessments.
- Do not read **`data/ground_truth/html/`** (document coding sheets) or **`filtered_gt_json`**. **`config/Categories Explained.html`** is allowed — it defines taxonomy only. Load Russian originals from `originals_index.json`.

Task — Experiment B (free segmentation):
1. Read **`data/experiments/shared/TAXONOMY_REFERENCE_FOR_ASSESSORS.md`** and keep **`config/Categories Explained.html`** available for framing/category edge cases.
2. For each document in `data/experiments/exp_b_free_segment/originals_index.json`, load the Russian text from the path given (relative to repo root).
3. Produce your own segmentation of the full text into analytic segments (you choose boundaries).
4. For each segment emit: section (integer order), entry_eng, entry_rus, content_category, framing, context (brief rationale or quote).
5. Merge all documents into `data/experiments/exp_b_free_segment/agent_assessments.json` matching template keys.

Optional sanity check: total segments per doc should reflect thorough coverage of the body text (excluding boilerplate you explicitly skip — if you skip, note once in the PR/commit message).

---

## Evaluation checklist

1. `PIPELINE_CONFIG=config/pipeline_config.experiment_redo.json`
2. Run pipeline with `--agent-assessments-file` pointing at **either** Experiment A or B assessments JSON (run separately).
3. Compare reports under `data/output/`; archive or rename report filenames between runs if you need side-by-side HTML.

---

## Tweaking what gets removed from human GT

Edit `config/experiment_redo_filter.json`:

- **`drop_generic_neutral_framing_rows`**: remove human GT rows whose framing normalizes to Generic / Neutral.
- **`assessor_allow_generic_neutral_framing`**: set `true` only if assessors **may** assign Generic / Neutral (digest + prompts follow this).
- **`assessor_excluded_framing_strategies`** / **`assessor_excluded_content_categories`**: extra labels to omit from **`TAXONOMY_REFERENCE_FOR_ASSESSORS.md`** and from allowed experiment outputs.
- After changing exclusions, run **`python scripts/export_assessor_taxonomy_reference.py`** (or full **`prepare_experiment_redo.py --no-archive`**).
- **`drop_raw_content_categories_extra`**: sheet-specific strings beyond deprecated defaults.

Re-run `python scripts/prepare_experiment_redo.py` (use `--no-archive` while iterating) when GT filtering inputs change.
