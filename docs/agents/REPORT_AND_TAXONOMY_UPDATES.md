# Report and taxonomy updates (April 2026)

This note documents functional changes to the HTML report, visualization UX, Cyrillic keyboard, word-cloud defaults, and the content-category taxonomy. Paths are relative to the repo root.

## Report regeneration

After pulling these changes, refresh outputs with:

```bash
python run_report_only.py
```

Full pipeline runs (`python run.py`, …) also regenerate `data/output/manual_analysis_report.html` when the report stage executes.

---

## Taxonomy (content categories)

### Intended model

Active **specific-detail** categories (8): **Actors**, **Places**, **Actions**, **Events**, **Date & Time** (renamed from **Time**), **Legal Framework**, **Documents**, **Material Resources**.

Removed from the active taxonomy: **Information**, **Methods**, **Status and Condition** (and **Status and Conditions**), **Context and Concepts** (and **Contexts and Concepts**), and legacy content label **Generic** (not framing).

### Source files

| File | Role |
|------|------|
| `config/taxonomy.json` | Canonical list of content categories (ids, EN/UK labels, colours) and framing strategies. Duplicate framing row for Generic removed; single **`Generic / Neutral Language`** entry. |
| `config/taxonomy_categories.py` | Rename map (`Time` → `Date & Time`), deprecated set for analytics, CE filter helper, **`GROUND_TRUTH_CONTENT_CATEGORY_REDIRECT`** (legacy GT labels → **Documents** or **Date & Time**). |
| `config/taxonomy_from_html.py` | After parsing `Categories Explained.html`, applies **`filter_content_categories_for_taxonomy`** so removed categories never enter merged glossary taxonomy. |

### Ground truth loading

| File | Role |
|------|------|
| `ground_truth/__init__.py` | Applies **`GROUND_TRUTH_CONTENT_CATEGORY_REDIRECT`** before filtering rows against valid taxonomy ids so segments with old labels are retained under **Documents** (or **Date & Time** for **Time**). |

### Report aggregation and display

| File | Role |
|------|------|
| `report/__init__.py` | **`canonical_content_category_id`** drives dataset stats, heatmaps, trends, and glossary term grouping by category (deprecated labels omitted from those aggregates). **`_report_category_colour`** colours LLM/human category chips and document-entry spans; deprecated/unknown categories use muted **`#888888`**. Comparison table cells still show **raw** stored strings. |

### LLM fallbacks

| File | Role |
|------|------|
| `llm/__init__.py` | Stub framing fallback uses **`Generic / Neutral Language`**. |
| `llm/ollama_adapter.py` | Fallback category list matches the 8 active categories; framing fallback aligned with taxonomy. |

### Tests

| File | Role |
|------|------|
| `tests/test_report.py` | Taxonomy fixtures use **`Generic / Neutral Language`**; assertions updated for current HTML structure (`homepage-content`, hidden stats attributes). |

### Categories Explained.html

The exported spreadsheet HTML was **not** hand-edited in-repo. Parsed output is filtered programmatically, so glossary/report definitions match the reduced category set. Update the source spreadsheet and re-export when you want the static HTML prose to match visually.

---

## Per-document visualizations (Research Lab parity)

| Area | Change |
|------|--------|
| `report/viz_lab_html.py` | **Configuration** `<details>` next to each document’s visualization selector; body id **`viz-config-body-{suffix}`**. |
| `report/__init__.py` | **`buildConfigPanel(panelId, data, docCtx?)`** with suffixed control ids for doc context; **`initDocViz`** binds change handlers and refreshes charts; radar on doc tabs shows a short note (multi-doc modes stay on the lab). Empty config hides the panel for chart types with no options. |

---

## Word cloud defaults and layout

| Area | Change |
|------|--------|
| `report/__init__.py` (embedded CSS) | **`.doc-viz-controls`** column layout so Configuration is not squeezed beside the selector. |
| `report/__init__.py` (JS + Python viz defaults) | Default **size factor (weight_factor)** **15** (was 4); input **max** **40**; `config/pipeline_config.example.json` updated to **`weight_factor`: 15**. |

---

## Cyrillic virtual keyboard

| Area | Change |
|------|--------|
| `report/__init__.py` | **`activeCyrillicInputByTab`** tracks focused field; comparison **`table-search-*`** opens the same tab’s popup and receives key inserts via **`notifyCyrillicSearchChanged`**. **`pointerdown`** (capture) ignores **`.comparison-table-search`** so the popup does not close immediately. |
| `report/__init__.py` (`_doc_tab` / `_document_text_view`) | Keyboard markup moved to **end of each document tab** (outside all `<details>`) with class **`doc-cyrillic-popup-floating`**: **fixed** positioning and high **z-index** so it is visible when only Comparison (or other) sections are open. |
| `report/__init__.py` (`UI_TRANSLATIONS`) | **`cyrillic_keyboard_label`**: removed the parenthetical about opening on focus (EN/UK). |

---

## Related constants (quick reference)

- Deprecated content categories for **viz-only** exclusion: see **`DEPRECATED_CONTENT_CATEGORIES`** in `config/taxonomy_categories.py`.
- GT redirect map: **`GROUND_TRUTH_CONTENT_CATEGORY_REDIRECT`** in the same file.

---

## Files touched (summary checklist)

- `config/taxonomy.json`
- `config/taxonomy_categories.py` (new)
- `config/taxonomy_from_html.py`
- `config/pipeline_config.example.json`
- `ground_truth/__init__.py`
- `report/__init__.py` (taxonomy helpers, stats, spans, colours, Cyrillic, viz config, CSS, i18n)
- `report/viz_lab_html.py`
- `llm/__init__.py`
- `llm/ollama_adapter.py`
- `tests/test_report.py`
- `docs/agents/REPORT_AND_TAXONOMY_UPDATES.md` (this file)
