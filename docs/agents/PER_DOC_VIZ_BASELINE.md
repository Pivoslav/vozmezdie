# Baseline: Report, Visualizations & Dynamic Taxonomy (April 2026)

**Purpose:** Snapshot of where the codebase stands **before** adding per-document visualization dropdowns and tightening dynamic taxonomy support (re-running experiments with fewer categories).

**Related:** [FRAMEWORK.md](FRAMEWORK.md) (data shapes), [AGENT_HANDOFF.md](AGENT_HANDOFF.md) (recent UX work), root [AGENTS.md](../../AGENTS.md) (paths and workflows).

---

## 1. Report layout and navigation

- **Single-page HTML** (`report.run` → `data/output/manual_analysis_report.html` by default): sidebar + main `tab-contents`.
- **Tabs:** Introduction (`tab-intro`), Research Lab (`tab-home`), Glossary (`tab-glossary`), one tab per document (`tab-{document_id}`).
- **Tab switching:** Inline `onclick="showTab('tab-…')"` on sidebar + tab buttons; `showTab` in embedded JS (`report/__init__.py` `_script()`).
- **Document tabs** include: header/stats, PDF block (if configured), comparison table, bilingual document text view (search, Cyrillic keyboard popup, category/framing filters), colour legend.

**Regenerate report only:** `python run_report_only.py`  
**Full pipeline:** `python run.py` (see root `run.py` orchestrator).

---

## 2. Data entering the report

| Input | Role |
|-------|------|
| **`comparison_by_doc`** | Map `document_id` → `{ aligned_rows, metrics?, … }`. Aligned rows drive tables, document text spans, glossary term extraction, and most viz aggregates. |
| **`documents`** | Ingest list: `document_id`, `display_name`, paths to full text for word clouds / vocab, optional `pdf_relative_path`, etc. |
| **`taxonomy`** | `content_categories` + `framing_strategies`: ids, colours, labels used for prompts/GT; merged with Categories Explained when configured. |
| **`config`** | Pipeline + report: paths, `report.visualizations` (word cloud stopwords, etc.), PDF base URL, glossary HTML source, feedback. |

**Pipeline contract:** Compare module writes comparison JSON; report reads it in memory when invoked from `run.py`. Shapes are summarized in [FRAMEWORK.md](FRAMEWORK.md) §2–3.

---

## 3. Taxonomy: two layers you must keep in sync

1. **Pipeline / comparison taxonomy**  
   - Typically `config/taxonomy.json`, or merged from **`config/Categories Explained.html`** when `config.taxonomy.source_html` is set (`config/taxonomy_from_html.py`).  
   - Row fields use canonical strings: `llm_category`, `human_category`, `llm_framing`, `human_framing` (aligned with GT).

2. **Glossary display taxonomy**  
   - `_load_glossary_taxonomy_from_categories_explained` in `report/__init__.py` loads definitions for the Glossary tab; may expose **more** category ids than the slim 7 used for strict comparison (see project notes on 12 vs 7 categories).

**Dynamic / fewer categories:** Any future experiment that **drops categories** must update:
- taxonomy source(s),
- GT / LLM outputs (or filters at compare/report time),
- viz aggregation (`stats["categories"]`, `fram_order`, filtering out ids mistaken as framings via `cat_ids` sets in `_homepage`),

so charts and dropdowns do not assume a fixed hard-coded list beyond what appears in data + taxonomy objects.

---

## 4. Research Lab visualizations today (corpus-wide only)

**Location:** `tab-home` → section `#lab-visualizations`.

**Markup:** `report/viz_lab_html.py` → `viz_lab_visualizations_section(viz_json, heatmap_html, places_map_srcdoc)`  
- Embeds **one** JSON blob: `<script type="application/json" id="viz-data">…</script>`  
- Single `#viz-select` dropdown chooses chart type; panels are sibling divs (Chart.js, WordCloud, DOM tables, iframes for Voyant/places).

**Payload construction:** `report/__init__.py` → `_homepage()`  
- `_compute_dataset_stats(comparison_by_doc, documents)` drives **per-doc** category/framing counts and heatmap tables.  
- `_word_frequencies_from_documents(documents, …)` builds **corpus** EN/RU word lists for word clouds.  
- Additional `_compute_*` helpers: agreement stats, terms-by-category/framing, vocab diversity, segment length vs accuracy, trends, mismatch flow, document fingerprint, document similarity, term × framing heatmap, places map payload, etc.  
- Assembled into **`viz_data`** dict (~1922–1964) then `json.dumps` → `viz_json`.

**Rendering:** Large block of JavaScript in `_script()` (`renderVizPanel`, `initViz`, Chart.js, WordCloud). Radar chart already has a **per-document selector** inside the corpus-wide viz (`radar-doc-select`).

**Standalone chart page:** Same `viz_json` can be written to `lab_visualization.html` (see `run_report_only.py` / report output config).

**Important gap for upcoming work:** There is **no** per-document visualization strip on each `tab-{docId}` yet; all charts consume **full corpus** `comparison_by_doc` + **all** `documents` for text-derived viz.

---

## 5. Document tab: what exists vs what you plan

| Present | Not present |
|---------|-------------|
| Comparison table + filters | Doc-scoped viz dropdown |
| Bilingual text view + search + Cyrillic popup | Doc-filtered `viz_data` or lazy-built charts |
| Quick nav links (PDF / text / compare) | Shared viz renderer parameterized by `docId` |

**Likely implementation directions** (for the next phase, not done in this note):
- Either **slice** `comparison_by_doc` to one doc (and optionally slice word-frequency inputs to that doc’s texts) and reuse `renderVizPanel` with a second JSON script per tab or a merged payload keyed by `docId`.  
- Or **lazy-init** charts when the user opens a doc tab + selects a viz (performance consideration).

---

## 6. Key files (quick reference)

| Area | Files |
|------|--------|
| Report orchestration | `report/__init__.py` (`run`, `_homepage`, `_doc_tab`, `_document_text_view`, `_script`, `_compute_*`, glossary, intro) |
| Viz HTML shell | `report/viz_lab_html.py` |
| Pipeline entry | `run.py`, `run_report_only.py` |
| Compare output shape | `compare/` (consumers in report assume `aligned_rows`) |
| Taxonomy | `config/taxonomy.json`, optional `config/Categories Explained.html`, `config/taxonomy_from_html.py` |
| Agent/process docs | `docs/agents/*.md`, root `AGENTS.md` |

---

## 7. Constraints for “fewer categories” re-runs

- **Report filters:** Category/framing dropdowns in document text view are filled from **`TAXONOMY_ALL_*`** arrays injected from taxonomy in `_script()`; removing categories from taxonomy JSON updates options automatically if the script is regenerated.  
- **Viz ordering:** `cat_order` / `fram_order` derive from **observed counts** and glossary framing lists; empty or removed categories should fall out of charts if they never appear in `comparison_by_doc`.  
- **Label normalization:** Framing variants (e.g. Generic / Neutral) are normalized in JS (`canonicalFramingOption`) and in Python (`_normalize_for_group`); keep behaviour consistent when taxonomy changes.  
- **Glossary:** `_glossary_tab` builds sections from **taxonomy lists +** terms from comparison; fewer categories reduce sections but term grouping logic must still match new ids.

---

*Last updated: baseline snapshot for per-document visualization work and dynamic taxonomy experiments.*
