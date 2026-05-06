# Guidance for Agents Working in This Directory

This document helps AI agents and human contributors understand the project state, established workflows, and where to look when making changes.

**All agent guides are in [docs/agents/](docs/agents/).** Start with [docs/agents/README.md](docs/agents/README.md) for the index, or [docs/agents/AGENT_HANDOFF.md](docs/agents/AGENT_HANDOFF.md) for the latest handoff.

---

## Project Summary

**Vozmezdie framework**: Modular pipeline for expert-grounded LLM evaluation on Cold War archival documents. Flow: Ingest → LLM extraction → Ground truth load → Compare → Report.

- **Agent guides**: `docs/agents/` (index: `docs/agents/README.md`)
- **Pipeline contracts**: `docs/agents/FRAMEWORK.md`
- **Output**: `data/output/manual_analysis_report.html`, `data/output/comparison_results.json`

---

## Recent Work (as of Feb 2025)

### Report improvements (latest session)

- **Places map**: "By document" and main count use segment count (not sum of extracted numbers). Segments popup closed by default.
- **Word cloud**: Deterministic layout and colors.
- **Glossary**: "View in document" links on terms; navigate to segment in document via hash `#tab-{docId}-row-{rowIndex}`.
- **Homepage**: "How Categories and Framing Are Qualified" at bottom of page.

### Fresh manual assessments (blind to ground truth)

Three documents were assessed **without** reading human labels first, to avoid anchoring:

1. **1249-0046-0047** (82 segments) — `scripts/write_fresh_assessment_1249.py`
2. **1262_28-32** (235 segments) — `scripts/write_fresh_assessment_1262_28_32.py`
3. **1249-80-83** (237 segments) — `scripts/write_fresh_assessment_1249_80_83.py`

**Workflow used:**
1. Learn taxonomy from `config/Categories Explained.html` and `config/taxonomy.json`
2. Export segments only: `python scripts/export_segments_only.py <doc_id>` → `data/output/segments_only_<doc_id>.json` (section, entry_eng, entry_rus, context; **no labels**)
3. Read Russian text from `data/russian_originals/<doc_id>.txt`
4. Apply taxonomy and record `content_category` and `framing` per segment
5. Write results via a `scripts/write_fresh_assessment_<doc_id>.py` script into `agent_assessments.json`
6. Regenerate report: `python run.py --agent-assessments`

### Glossary enhancements

- Glossary tab now uses **Categories Explained.html** as the authoritative source for definitions.
- Report loads CE when `config.taxonomy.source_html` is set; definitions and examples come from there.
- Added "Terms Found in Documents" sections: summary stats, terms by content category, terms by framing strategy. Terms are extracted from `comparison_by_doc` (aligned rows with `llm_category`, `llm_framing`).
- Structure mirrors `dev/analysis_w_text_highlight.html`.

### Helper scripts

- `scripts/export_segments_only.py <doc_id>` — Exports segment list from ground truth HTML **without** content_category or framing. Use for blind assessment so the assessor does not see human labels.
- `scripts/export_segments_filtered.py <doc_id> [...]` — Exports **body rows only** (same filter as pipeline). Section numbers align with GT. Prefer this for fresh assessment.
- `scripts/assess_segments_ollama.py <doc_id> [...]` — Uses Ollama to classify each segment. Requires filtered segments. Run after `export_segments_filtered.py`.

---

## Two Assessment Modes

| Mode | When | Input | Output |
|------|------|-------|--------|
| **Standard** | Assessor can see GT; comparing to human | Ground truth rows (with labels) | Add/modify rows in `agent_assessments.json` |
| **Fresh blind** | No GT before assessing; independent evaluation | `segments_only_<doc_id>.json` | New `write_fresh_assessment_<doc_id>.py` script that merges into `agent_assessments.json` |

For fresh blind assessment, never read GT labels; only use segment text (entry_eng, entry_rus) and context.

---

## Key Paths

| What | Path |
|------|------|
| Pipeline config | `config/pipeline_config.example.json` |
| Taxonomy (definitions) | `config/Categories Explained.html` |
| Taxonomy (ids, colours) | `config/taxonomy.json` |
| Document mapping | `config/document_map.json` |
| Russian originals | `data/russian_originals/<doc_id>.txt` |
| Ground truth HTML | `data/ground_truth/html/<doc_id>.html` or `<doc_id>.html` (spaces for 1262 docs) |
| Agent assessments | `data/output/agent_assessments.json` |
| Report output | `data/output/manual_analysis_report.html` |
| Segments-only export | `data/output/segments_only_<doc_id>.json` |
| UX roadmap (canonical backlog) | `docs/agents/UI_SCOPE_AND_ROADMAP.md` |
| UI labels vs taxonomy strings | `docs/agents/UI_LABEL_MAP.md` |

---

## Taxonomy Notes

- **For assessment/comparison**: Use the 7 content categories and 5 framing strategies from `taxonomy.json` (or the merged taxonomy when `source_html` is set). Labels must match exactly for comparison to work.
- **Reader-facing copy**: Umbrella terms **Specific Details** and **Ideological Layers** may appear in the UI without renaming stored values — see `docs/agents/UI_LABEL_MAP.md`.
- **For glossary definitions**: Report loads from `Categories Explained.html` when available; it has 12 content categories and 5 framing strategies with full Purpose/Function and Examples.
- **Normalization**: "Generic / Neutral" and "Generic / Neutral Language" are treated as the same in term grouping.

---

## Where to Edit What

| Concern | Module / file |
|---------|---------------|
| Pipeline orchestration | `run.py` |
| Document discovery | `ingest/` |
| LLM extraction | `llm/` |
| Ground truth loading | `ground_truth/` |
| Comparison logic | `compare/` |
| Report HTML/CSS/JS | `report/__init__.py` |
| Glossary definitions source | `config/Categories Explained.html` (report loads via `taxonomy_from_html`) |
| New manual assessment | New `scripts/write_fresh_assessment_<doc_id>.py` |

Report-only iteration: `python run_report_only.py` — no need to re-run full pipeline when changing report code.

---

## Git: merge conflicts in generated `docs/` HTML

When merging **`main`** into a branch or opening a PR, Git often reports conflicts only in **`docs/index.html`** and **`docs/lab_visualization.html`**. Both are **generated** (same content family as the report in `report/__init__.py`), so different branches editing the report will collide there.

**Do not** manually splice conflict markers inside those HTML files.

**Agent workflow (automate on push / merge):**

1. Finish merging non-generated files (`report/__init__.py`, `report/viz_lab_html.py`, config, etc.) as usual.
2. From the repo root run:

   ```bash
   python scripts/build_github_pages_docs.py
   ```

   This rebuilds Pages outputs from the current report code (uses `data/output/comparison_results.json` or `docs/fixtures/comparison_results.json` per the script).

3. `git add docs/index.html docs/lab_visualization.html` and any other paths that script updated (`docs/introduction.html`, `docs/original_pdfs/`, etc.), then complete the merge or amend as needed.

For local **`data/output/manual_analysis_report.html`** only, use `python run_report_only.py`; GitHub Pages artifacts under **`docs/`** are driven by **`scripts/build_github_pages_docs.py`**.

---

## Next Priority

**UX roadmap:** Stakeholder scope, epic list, and decisions (landing page, PDF/image wheel, UI-only label policy, etc.) live in **[docs/agents/UI_SCOPE_AND_ROADMAP.md](docs/agents/UI_SCOPE_AND_ROADMAP.md)**. **Label mapping** (Specific Details / Ideological Layers ↔ JSON and `taxonomy.json`): **[docs/agents/UI_LABEL_MAP.md](docs/agents/UI_LABEL_MAP.md)**.

**Read [docs/agents/AGENT_HANDOFF.md](docs/agents/AGENT_HANDOFF.md)** for user feedback, tabled items (click word for definition), aesthetic direction (archival + KGB), and visualization ideas. Phase A (scroll sync, glossary search, bilingual highlight) is complete. See [NEXT_STEPS.md](docs/agents/NEXT_STEPS.md) for data locations and agent instructions.

**Fork maintainers:** See [docs/agents/HANDOFF_FOR_FORK.md](docs/agents/HANDOFF_FOR_FORK.md) for snapshot summary, new viz integration, and fixes applied.
