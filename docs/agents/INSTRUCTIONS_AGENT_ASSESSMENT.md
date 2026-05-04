# Agent assessment: how to do it and how it fits the pipeline

This doc is for a new agent (human or AI) who will **read the documents and assign content category and framing to each segment by hand**. No scripts do the classifying; you read, you decide, you record. Work in chunks. When a document is fully assessed, we run the pipeline and compare your labels to ground truth.

There are two modes: **standard** (you can see ground truth labels) and **fresh blind** (you do not see human labels until after assessing). See "Fresh blind assessment" below.

---

## What you are doing

- **Input:** One document at a time (Russian original in `data/russian_originals/<document_id>.txt`, and optionally English in `data/input/`).
- **Segments:** The segments to label come from **ground truth** (human-coded sheet). So you are not deciding *what* a segment is; you are deciding *how to label* each existing segment: **content category** (what kind of content) and **framing** (how it is framed).
- **Output:** Your judgements are stored in `data/output/agent_assessments.json`. Each document key holds a list of rows. Each row has: `section`, `entry_eng`, `entry_rus`, `content_category`, `framing`, `context`. You keep `section`, `entry_eng`, `entry_rus`, and `context` **identical** to the ground-truth row (so the pipeline can align your row to the human row by text). You only set **your** `content_category` and `framing`.

---

## Taxonomy (use these exact labels)

The pipeline loads taxonomy from `config/Categories Explained.html` (merged with `config/taxonomy.json`). Use the **English labels** below so comparison and the report work.

**Content categories (pick one per segment)** — pipeline uses these 7 from `taxonomy.json`:  
Actions | Actors | Places | Time | Documents | Context and Concepts | Legal Framework

**Framing strategies (pick one per segment):**  
Generic / Neutral Language | Institutional / Bureaucratic Lingo | Ideological Framing (Discrediting) | Ideological Phrasing (Normalizing) | Action-Focused Language

If you are unsure, read the taxonomy: `config/Categories Explained.html` and `config/taxonomy.json` for full definitions and colours.

---

## Fresh blind assessment (no GT before assessing)

When you want to assess **without** seeing human labels (to avoid anchoring):

### Option A: Ollama-based (automated)

Uses filtered segments (body rows only) so output aligns with ground truth. Requires Ollama running locally.

```bash
python scripts/export_segments_filtered.py 1262_28-32 1262_149-150 1262_198-200
python scripts/assess_segments_ollama.py 1262_28-32 1262_149-150 1262_198-200
python run.py --agent-assessments
```

Expect ~2–3 seconds per segment. Results merge into `agent_assessments.json`.

### Option B: Manual (export_segments_only + write_fresh_assessment)

1. **Export segments only** (no labels):
   ```bash
   python scripts/export_segments_only.py <doc_id>
   ```
   Writes `data/output/segments_only_<doc_id>.json` with section, entry_eng, entry_rus, context only.
   Note: For body-only alignment, prefer `export_segments_filtered.py` (uses same filter as pipeline).

2. **Read** `data/russian_originals/<doc_id>.txt` (and English if available).

3. **Apply taxonomy** and record your content_category and framing for each segment.

4. **Write results** via a script like `scripts/write_fresh_assessment_<doc_id>.py` that merges into `agent_assessments.json`. See `write_fresh_assessment_1249.py`, `write_fresh_assessment_1262_28_32.py`, or `write_fresh_assessment_1249_80_83.py` as templates.

5. **Regenerate report**: `python run.py --agent-assessments`

Do not read ground truth HTML or labels until after you have finished your assessment.

---

## Working in chunks

1. **Pick a document** (e.g. `1127`). Document IDs are in `config/document_map.json`.
2. **Get the segments for that doc** from ground truth. Ground truth lives in `data/ground_truth/html/<document_id>.html` (or `<doc_id>.html` with underscores in the ID; for IDs like `1262_149-150` the file may be `1262 149-150.html`). The repo loads them via `ground_truth.html_loader`; you can export a chunk to JSON for yourself (e.g. first 30 rows) with a small Python one-off if that helps.
3. **Read the Russian (and English if present) document** so you have context. Paths: `data/russian_originals/<document_id>.txt`, and optionally `data/input/<display_name>` for English.
4. **For each segment in the chunk:**  
   - Keep `section`, `entry_eng`, `entry_rus`, `context` as in the ground-truth row.  
   - Choose one **content_category** and one **framing** from the taxonomy list above and write them into the row.
5. **Append your chunk to `data/output/agent_assessments.json`.**  
   - The file is keyed by document ID, e.g. `"1127": [ ... ]`.  
   - Add rows to the list for that document. If you are continuing a doc, merge your new rows with the existing list (keep section order).  
   - Do not change `entry_eng` / `entry_rus` / `section` / `context` — only `content_category` and `framing` are your assessments.

Repeat with the next chunk (next 30–50 segments, or next document) until the document (or all documents) are done.

---

## Running the pipeline with your assessments

The framework supports this directly. From the project root:

```bash
python run.py --agent-assessments
```

This runs: ingest → **load `data/output/agent_assessments.json` as llm_by_doc** → ground truth → compare → report. Documents not in the file (or with no rows) get an empty list; compare will show 0 matched for those. The report is written to `data/output/manual_analysis_report.html`.

- **Partial doc:** You can have only part of a document assessed (e.g. only sections 16–45 of 1127). The compare step aligns your rows to ground truth by `entry_rus` (or `entry_eng`, per config). Rows you did not assess have no matching “LLM” row; the report still shows what you did assess.
- **Full experiment:** Run `python run.py --agent-assessments` whenever you want to regenerate the report from the current agent_assessments.json.

---

## File layout (quick reference)

| What | Where |
|------|--------|
| Document list / IDs | `config/document_map.json` |
| Russian originals | `data/russian_originals/<document_id>.txt` |
| English (optional) | `data/input/` (see document_map `display_name`) |
| Ground truth (segments to label) | `data/ground_truth/html/<document_id>.html` (or with space for 1262 docs) |
| Taxonomy (categories + framing) | `config/Categories Explained.html`, `config/taxonomy.json` |
| Your assessments | `data/output/agent_assessments.json` |
| Segments only (blind) | `data/output/segments_only_<doc_id>.json` (from `export_segments_only.py`) |
| Segments filtered (body only) | `data/output/segments_filtered_<doc_id>.json` (from `export_segments_filtered.py`) |
| Report output | `data/output/manual_analysis_report.html` |

---

## Document 1127 status

- **Sections 17–270** (254 segments) are assessed and stored in `agent_assessments.json` under `"1127"`.  
- Chunks completed: 1 (17–45), 2–4 (46–136), 5 (137–176), 6 (177–216), 7 (217–256), 8 (257–270).  
- Ground truth for 1127 has section range 2–270 (268 rows); sections 2–16 are not yet in agent_assessments and can be added if needed.

## Document 1128 status

- **Sections 16–380** (362 segments) are assessed and stored in `agent_assessments.json` under `"1128"`.  
- Chunks completed: 1 (16–55), 2 (56–98), 3 (99–138), 4 (139–178), 5 (179–218), 6 (219–258), 7 (259–298), 8 (299–338), 9 (339–378), 10 (379–380).  
- Document 1128 is fully assessed (all filtered ground-truth segments).

## Document 1206 status

- **Sections 16–297** (282 segments) are assessed and stored in `agent_assessments.json` under `"1206"`.
- Chunks completed: 1 (16–55), 2 (56–95), 3 (96–135), 4 (136–175), 5 (176–215), 6 (216–255), 7 (256–295), 8 (296–297).
- Document 1206 is fully assessed (all filtered ground-truth segments).

## Document 1208 status

- **Sections 16–232** (217 segments) are assessed and stored in `agent_assessments.json` under `"1208"`.
- Chunks completed: 1 (16–55), 2 (56–95), 3 (96–135), 4 (136–175), 5 (176–215), 6 (216–232).
- Document 1208 is fully assessed (all filtered ground-truth segments).

## Document 1209 status

- **Sections 16–184** (169 segments) are assessed and stored in `agent_assessments.json` under `"1209"`.
- Chunks completed: 1 (16–55), 2 (56–95), 3 (96–135), 4 (136–175), 5 (176–184).
- Document 1209 is fully assessed (all filtered ground-truth segments).

## Document 1213 status

- **Sections 16–143** (128 segments) are assessed and stored in `agent_assessments.json` under `"1213"`.
- Chunks completed: 1 (16–55), 2 (56–95), 3 (96–135), 4 (136–143).
- Document 1213 is fully assessed (all filtered ground-truth segments).

## Document 1215 status

- **Sections 16–182** (167 segments) are assessed and stored in `agent_assessments.json` under `"1215"`.
- Chunks completed: 1 (16–55), 2 (56–95), 3 (96–135), 4 (136–175), 5 (176–182).
- Document 1215 is fully assessed (all filtered ground-truth segments).

## Document 1230 status

- **Sections 1-121** (105 segments) are assessed and stored in `agent_assessments.json` under `"1230"`.
- Chunks completed: 1 (sections 1-56), 2 (sections 2-96), 3 (sections 97-121).
- Document 1230 is fully assessed (all filtered ground-truth segments).

## Document 1245 status

- **227 segments** are assessed and stored in `agent_assessments.json` under `"1245"`.
- Chunks completed: 1–6 (40 segments each for chunks 1–5, 27 for chunk 6).
- Document 1245 is fully assessed (all filtered ground-truth segments).

## Document 1249-0046-0047 status

- **82 segments** are assessed and stored in `agent_assessments.json` under `"1249-0046-0047"`.
- Fresh blind assessment (no GT before assessing); script: `scripts/write_fresh_assessment_1249.py`.
- Document 1249-0046-0047 is fully assessed.

## Document 1262_28-32 status

- **235 segments** are assessed and stored in `agent_assessments.json` under `"1262_28-32"`.
- Fresh blind assessment; script: `scripts/write_fresh_assessment_1262_28_32.py`.
- Document 1262_28-32 is fully assessed.

## Document 1249-80-83 status

- **237 segments** are assessed and stored in `agent_assessments.json` under `"1249-80-83"`.
- Fresh blind assessment; script: `scripts/write_fresh_assessment_1249_80_83.py`.
- Document 1249-80-83 is fully assessed.

## Document 1256 status

- **Sections 15–120** (106 segments) are assessed and stored in `agent_assessments.json` under `"1256"`.
- Chunks completed: 1 (15–54), 2 (55–94), 3 (95–120).
- Document 1256 is fully assessed (all filtered ground-truth segments).

## Document 1262_198-200 status

- **163 segments** are assessed and stored in `agent_assessments.json` under `"1262_198-200"`.
- Chunks completed: 1–4 (40 rows each), 5 (3 rows).
- Document 1262_198-200 is fully assessed (all filtered ground-truth segments).

## Document 1262_149-150 status

- **Sections 17–72** (54 segments) are assessed and stored in `agent_assessments.json` under `"1262_149-150"`.
- Chunks completed: 1 (17–57), 2 (58–72).
- Document 1262_149-150 is fully assessed (all filtered ground-truth segments).

## Document 1247 status

- **Sections 16–204** (189 segments) are assessed and stored in `agent_assessments.json` under `"1247"`.
- Chunks completed: 1 (16–55), 2 (56–95), 3 (96–135), 4 (136–175), 5 (176–204).
- Document 1247 is fully assessed (all filtered ground-truth segments).
- All other documents remain to be assessed; use the same taxonomy labels above.
