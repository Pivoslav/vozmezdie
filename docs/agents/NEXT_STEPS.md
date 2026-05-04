# Summary and handoff for next agent

**UX / UI work:** Use **[UI_SCOPE_AND_ROADMAP.md](UI_SCOPE_AND_ROADMAP.md)** as the canonical backlog (meeting notes, decisions D1–D5, epics E0–E7). When changing user-visible names for categories/framing, follow **[UI_LABEL_MAP.md](UI_LABEL_MAP.md)** (UI-only wording vs canonical stored taxonomy strings).

**Start here:** [AGENT_HANDOFF.md](AGENT_HANDOFF.md) — detailed plan with user feedback, aesthetic direction (archival + KGB), outside-the-box visualizations, and implementation phases.

## Recent completions (Feb 2025)

- **Fresh blind assessments**: 1249-0046-0047 (82 segments), 1262_28-32 (235 segments), 1249-80-83 (237 segments). Workflow: `export_segments_only.py` → read Russian → apply taxonomy → `write_fresh_assessment_<doc_id>.py` → merge into `agent_assessments.json`. See [AGENTS.md](../AGENTS.md) and [INSTRUCTIONS_AGENT_ASSESSMENT.md](INSTRUCTIONS_AGENT_ASSESSMENT.md).
- **Glossary**: Now uses `Categories Explained.html` as the authoritative source for definitions. Terms from documents by content category and framing; summary stats. **Glossary → document nav**: Terms have "View in document" links; `term_locations` maps (eng, rus) to (doc_id, row_index); hash `#tab-{docId}-row-{rowIndex}` triggers scroll-to-segment.
- **Places map**: Counts fixed to segment count (not sum of extracted numbers). Segments popup section closed by default.
- **Word cloud**: Deterministic layout (`shuffle: false`) and hash-based colors.
- **Homepage**: "How Categories and Framing Are Qualified" moved to bottom (after Feedback).
- **Helper**: `scripts/export_segments_only.py <doc_id>` exports segments without labels for blind assessment.

## Next priority: Brainstorming design (design exploration done)

The next agent session should focus on **design exploration** — UI/UX, report structure, workflow improvements, or architectural decisions. Ideas: report layout, document text view enhancements, glossary search/filter, assessor workflow, pipeline extensibility.

**See [DESIGN_EXPLORATION.md](DESIGN_EXPLORATION.md)** (incremental ideas, known issues, recommended fixes) and **[GRAND_DESIGN_PLAN.md](GRAND_DESIGN_PLAN.md)** (grand frontend brainstorm):
- Layout options (tabs vs sidebar vs dashboard-first)
- User personas (Reviewer, Assessor, Researcher) and primary flows
- Feature inventory (current + proposed) by area
- Visual design directions and tech architecture
- Phased roadmap and open questions

---

## What's in place (vozmezdie_framework)

**Modular pipeline:** Ingest → LLM extraction → Ground truth load → Compare → Report.

- **Config:** `config/pipeline_config.example.json` (paths, model, `use_fixture`), `config/taxonomy.json` (categories + framing).
- **Modules:** Each has one job and a clear input/output (see [FRAMEWORK.md](FRAMEWORK.md)). Fixtures when input dirs are missing so the pipeline runs without real data.
- **Run:** `python run.py` (full run), `python run.py --report-only` (regenerate HTML from saved JSON), `python run.py --use-ollama` (use real Ollama). `pytest tests/ -v` runs all tests.
- **Output:** `data/output/manual_analysis_report.html` and `data/output/comparison_results.json`.

**Report:** One HTML file with tabs per document, stats (category/framing/both %), comparison table (LLM vs human), document text view (search, filter by category/framing, colour), and a glossary tab. The document text view is built in the browser from the table (see report module JS). Glossary definitions come from `Categories Explained.html` when `config.taxonomy.source_html` is set.

---

## Data locations (copied from dev)

- **Document texts:** `data/input/` — one `.txt` per document; names match ground-truth HTML stems (e.g. `1128.txt`, `1262 28-32.txt`). Ingest uses stem as `document_id` (spaces → underscores).
- **Ground-truth HTML:** `data/ground_truth/html/` — one HTML per document (e.g. `1128.html`). Same table structure as before; `resources/sheet.css` is under `data/ground_truth/html/resources/`.
- **Taxonomy source:** `config/Categories Explained.html` (framing + 12 content categories). Optional: `config/Codes.html` (coding guide reference).
- **Demo report (reference):** `report/demo_report_reference.html` — last demo version of the analysis page; use when adding or changing report features.

## Ground truth is now HTML + updated categories (detailed instructions)

**Human values are in HTML files, not CSVs.** See **[INSTRUCTIONS_GROUND_TRUTH_HTML.md](INSTRUCTIONS_GROUND_TRUTH_HTML.md)**. It explains:
- Where the ground-truth HTML files are: **`data/ground_truth/html/`** (e.g. `1128.html`).
- Where the updated category definitions are: **`config/Categories Explained.html`**.
- How to implement loading **without** reading huge HTML in one go (streaming/chunked parse or small extraction script).
- Exact contract the ground_truth and taxonomy must satisfy, and a step-by-step checklist for the next agent.

Use that file when the task is "load ground truth from HTML and use Categories Explained for taxonomy."

---

## Context documents have changed (updated sheets as HTML)

You've updated the sheets and saved them as HTML. So:

1. **Where the framework gets "documents":** Ingest reads from `config.documents.input_dir` (default `data/input`) and expects **text** (e.g. `.txt`). It does **not** read HTML by default.
2. **What the next agent should do with the new HTML sheets:**
   - **Option A — Use HTML as the "source":** Add or switch an ingest adapter that reads your HTML files (e.g. from a folder like `data/input` or a path you specify), extracts the text (and any structure you need, e.g. table rows), and outputs the same shape: list of `{ document_id, display_name, path, raw_text }`. Then the rest of the pipeline (LLM, ground truth, compare, report) stays the same.
   - **Option B — Treat HTML as ground truth / reference:** If the new HTML sheets are the human-coded "answers," the agent can add a ground-truth loader that reads those HTML files (e.g. parses tables or specific divs) into the same row shape (section, entry_eng, entry_rus, content_category, framing, context). Then `ground_truth` returns that; compare and report stay the same.
   - **Option C — One-off import:** A script that reads the new HTML sheets, converts them into (1) text files in `data/input` and/or (2) CSVs (or JSON) in `data/ground_truth`, so the existing ingest and ground_truth modules work without changing their contracts.

Tell the next agent which of these you want (or a combination), and where the new HTML files live (path or list of files).

---

## Changing or adding features on the final HTML report (modular way)

The "final HTML" is produced by the **report** module. To change or add features in a modular way:

1. **Single place to edit:** All report layout and behaviour live in `report/__init__.py`. The report is one function: `run(comparison_by_doc, documents, taxonomy, config)` → writes HTML to the path in config. So any change to the final page (new sections, new filters, different styling, EN/UK, etc.) is done by editing the report module (and optionally config/taxonomy), not by scattering logic across ingest/llm/compare.

2. **Data in, HTML out:** The report only gets:
   - `comparison_by_doc`: per-doc aligned rows + category/framing/both accuracy.
   - `documents`: list of doc ids and display names.
   - `taxonomy`: content categories and framing strategies (with labels, colours, etc.).
   - `config`: output path and any extra options you add.

   So to add a new feature (e.g. a new filter or a new column):
   - If it needs **new data**: add that data to the pipeline **upstream** (e.g. in compare or in the row shape), then pass it through to `report.run()` (e.g. add a field to `comparison_by_doc` or to each aligned row). The report then only renders what it receives.
   - If it's **presentation only**: change only the report module (HTML/CSS/JS in `report/__init__.py`). No need to touch ingest/llm/ground_truth/compare.

3. **Optional: split template later:** Right now the HTML is built as strings in Python. For bigger changes, you can later split it into:
   - A **data step** that builds a single structure (e.g. a dict or JSON) from `comparison_by_doc` + documents + taxonomy.
   - A **template** (e.g. one or more HTML/JS files, or a simple template engine) that takes that structure and produces the final HTML.  
   The report module would still be the only place that "owns" the final page; it would just delegate the rendering to the template.

4. **Testing report changes:** Use `run_report_only.py` and the saved `comparison_results.json`. Change the report code, run `python run_report_only.py`, refresh the browser. No need to re-run LLM or ingest. For unit tests, add or extend tests in `tests/test_report.py` with fixture `comparison_by_doc` / documents / taxonomy and assert the generated HTML contains the new elements or strings.

---

## Simple instructions to give the next agent

You can paste something like this:

- **Context:** "We have a modular pipeline in `vozmezdie_framework` (see [FRAMEWORK.md](FRAMEWORK.md) and [NEXT_STEPS.md](NEXT_STEPS.md)). The pipeline produces a single HTML report from documents, LLM extraction, and ground truth. I've updated the sheets and saved them as HTML files."
- **Task 1 — New context documents:** "The context documents have changed. [Describe where the new HTML sheets are, e.g. path or folder.] We need the pipeline to use these. Prefer: (A) ingest that reads from these HTML files and outputs the same document list shape, and/or (B) ground truth loaded from these HTML files in the same row shape, and/or (C) a script that converts these HTML files into the existing input/ground_truth format. Implement the option we need and keep the rest of the pipeline unchanged."
- **Task 2 — Report changes (if any):** "Changes to the final HTML report should be done only in the `report` module. New data needed for the report should be added upstream (e.g. in compare or row shape) and passed into `report.run()`. Use `run_report_only.py` and the saved JSON to iterate on the report without re-running the full pipeline. Add or update tests in `tests/test_report.py` for new report behaviour."

That keeps the agent focused on one place per concern (ingest or ground_truth for new inputs, report for final page changes) and on the existing contracts so the pipeline stays modular.
