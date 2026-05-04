# Design Exploration — Vozmezdie Framework

This document captures design ideas, known issues, and architectural decisions for the next development phase. It follows the priority set in [NEXT_STEPS.md](NEXT_STEPS.md): focus on **design exploration** — UI/UX, report structure, workflow improvements, architectural decisions.

---

## 1. Current State Summary

### Pipeline
- **Flow:** Ingest → LLM extraction → Ground truth load → Compare → Report
- **Output:** Single HTML report (`manual_analysis_report.html`) + `comparison_results.json`
- **Report:** One HTML file; layout and behaviour live in `report/__init__.py` (strings, no separate template)

### Report features (implemented)
- Master header, tabs per document + Glossary tab
- Stats cards: category %, framing %, both-match %
- Comparison table: Section, Entry ENG, Entry RUS, Content Category (LLM vs Human), Framing (LLM vs Human), Context
- Document text view: two panels (English, Russian), search, category/framing filters, colour by LLM or Human
- Glossary: definitions from `Categories Explained.html`, terms from documents by category/framing
- Colour legend, orphan markers (dashed underline for segments without partner)

### Assessment workflow
- 17 documents assessed; 3 fresh blind (1249-0046-0047, 1262_28-32, 1249-80-83)
- `export_segments_only.py` for blind assessment; `write_fresh_assessment_<doc_id>.py` scripts merge into `agent_assessments.json`

---

## 2. Known Issues (from [TEXT_VIEW_ASSESSMENT.md](TEXT_VIEW_ASSESSMENT.md))

### 2.1 Dropdown vs span label mismatch (mostly addressed)
- **Problem:** When panels are server-filled, spans use LLM labels; dropdown was populated from table (Human column). LLM-only values (e.g. "Action-Focused Language") could be missing from the dropdown.
- **Current code:** `buildDocumentTextView` already collects from spans when `hasPreFilled`; it also adds from the table. Spans are collected first.
- **Recommendation:** Simplify to populate dropdowns *only* from span `data-category`/`data-framing` when `hasPreFilled`, to avoid any edge cases and make the contract explicit.

### 2.2 String matching: segments not found in raw text
- **Problem:** If table phrases (e.g. "D. Hanusiak held a press conference") differ from raw document text (punctuation, line breaks, spacing), no span is created. Dropdown shows the option, but there is nothing in the panel to colour.
- **Fix:** Make segment search more tolerant — e.g. normalize whitespace (`\s+` → single space), trim, optionally case-insensitive for matching.

### 2.3 Substring overlap: shorter segments lose to longer ones
- **Problem:** When "arrived" (Action-Focused) is inside "delegation arrived" (Generic), we match the longer phrase first. The shorter segment never gets its own span and stays grey.
- **Fix:** Sort candidates by segment length ascending before overlap resolution, so shorter segments are considered first. Already partially done: `candidates.sort(key=lambda x: (x[1], x[0]))` — length is first, so shorter wins. Need to verify the overlap logic keeps the right behaviour.

---

## 3. Design Ideas by Area

### 3.1 Report Layout

| Idea | Description | Effort |
|------|-------------|--------|
| **Sidebar navigation** | Replace flat tabs with a sidebar for document list + Glossary; leaves more horizontal space for table and text view | Medium |
| **Collapsible sections** | Stats, text view, table as collapsible panels so users can focus on one at a time | Low |
| **Summary dashboard** | First tab or section showing aggregate stats across all documents before diving into per-doc detail | Medium |
| **Sticky controls** | Keep search/filter/colour controls sticky when scrolling long documents | Low |
| **EN/UK i18n expansion** | Extend `data-translate` coverage to stats labels, filter placeholders, glossary section titles | Low |

### 3.2 Document Text View Enhancements

| Idea | Description | Effort |
|------|-------------|--------|
| **Scroll sync** | Sync scroll position between English and Russian panels for easier comparison | Medium |
| **Click-to-table** | Clicking a span in the text view scrolls/highlights the corresponding row in the comparison table | Medium |
| **Highlight mode** | Toggle "highlight only filtered" vs "dim non-matching" — current behaviour could be a setting | Low |
| **Search in both languages** | Search box that finds matches in either panel and highlights both | Low (partially done) |
| **Keyboard navigation** | Arrow keys to jump between highlighted spans; Enter to focus table row | Medium |

### 3.3 Glossary

| Idea | Description | Effort |
|------|-------------|--------|
| **Search/filter** | Text search over category/framing names and definitions; filter by "terms found in documents" | Medium |
| **Expand/collapse by section** | Collapse "Content categories" and "Framing strategies" until opened | Low |
| **Link from text view** | Clicking a category/framing in the legend could scroll to its glossary entry | Medium |
| **Tooltip preview** | Hover over a term in the text view shows a short definition tooltip | Medium |

### 3.4 Assessor Workflow

| Idea | Description | Effort |
|------|-------------|--------|
| **In-report editing** | Allow editing LLM/agent labels directly in the report and save back to `agent_assessments.json` (requires JS + backend or local file write) | High |
| **Chunk progress indicator** | Show which segments are assessed vs missing for each document | Medium |
| **Export for review** | Export current view (e.g. filtered rows) to CSV or JSON for external review | Low |
| **Side-by-side assessment UI** | Dedicated page: segment list + taxonomy reference + form to record category/framing — separate from the analysis report | High |
| **Keyboard shortcuts for taxonomy** | Quick keys (e.g. 1–7 for categories, A–E for framing) during assessment | Medium |

### 3.5 Pipeline Extensibility

| Idea | Description | Effort |
|------|-------------|--------|
| **Split report template** | Move HTML/CSS/JS from Python strings to separate files; `report` builds a data structure and renders via template | Medium |
| **Pluggable output formats** | Support JSON-only output for report data; or PDF/LaTeX for printable reports | Medium |
| **Configurable comparison strategy** | Make matching strategy (by index, by phrase, fuzzy) configurable in pipeline_config | Low |
| **Multiple LLM backends** | Already have Ollama + fixture; add OpenAI/Anthropic adapters with same output contract | Low |
| **Batch document selection** | Run pipeline for a subset of documents (e.g. only those in `document_map` with `assessed: true`) | Low |

---

## 4. Recommended Priority Order

1. **Bug fixes (2.2, 2.3):** Normalize segment search and verify substring overlap behaviour. These directly affect assessor experience.
2. **Dropdown simplification (2.1):** When `hasPreFilled`, use only span content for dropdowns. Quick cleanup.
3. **Glossary search/filter:** High value for navigating 12 categories + 5 framing strategies with many terms.
4. **Collapsible sections + sticky controls:** Low effort, improves focus when documents are long.
5. **Scroll sync for text panels:** Strong UX upgrade for bilingual comparison.
6. **Split report template:** Enables larger UI changes without touching Python logic.

---

## 5. References

| Document | Purpose |
|----------|---------|
| [AGENT_HANDOFF.md](AGENT_HANDOFF.md) | Primary handoff: user feedback, aesthetic (archival+KGB), outside-the-box visualizations, implementation plan |
| [GRAND_DESIGN_PLAN.md](GRAND_DESIGN_PLAN.md) | Grand design brainstorm: layout options, feature inventory, personas, roadmap, open questions |
| [AGENTS.md](../AGENTS.md) | Project summary, key paths, where to edit |
| [NEXT_STEPS.md](NEXT_STEPS.md) | Handoff, data locations, simple instructions for next agent |
| [FRAMEWORK.md](FRAMEWORK.md) | Pipeline contracts, data shapes, module boundaries |
| [TEXT_VIEW_ASSESSMENT.md](TEXT_VIEW_ASSESSMENT.md) | Document text view behaviour, known fixes |
| `INSTRUCTIONS_AGENT_ASSESSMENT.md` | Assessment workflow, taxonomy, document status |
| `report/demo_report_reference.html` | Reference layout for report features |
| `dev/analysis_w_text_highlight.html` | Dev reference for text view styling |

---

## 6. Next Agent Instructions

To continue from this design exploration:

1. **Implement fixes:** Start with segment search normalization and dropdown simplification (`report/__init__.py`).
2. **Pick 1–2 design ideas:** E.g. glossary search and collapsible sections. Implement in `report/__init__.py`; use `run_report_only.py` for iteration.
3. **Test with real data:** Ensure `comparison_results.json` exists (run full pipeline or `run.py --agent-assessments`). Verify report behaviour on a document with both Eng and Rus text.
4. **Update tests:** Add or extend `tests/test_report.py` for new behaviour.

For template split or larger architectural changes, create a separate task and branch.
