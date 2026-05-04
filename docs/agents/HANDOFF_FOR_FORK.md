# Handoff for Fork — Vozmezdie Framework

**Prepared:** Feb 2025  
**Purpose:** Handoff document for maintainers of a fork of the Vozmezdie framework. Read this first, then [AGENTS.md](../AGENTS.md) and [AGENT_HANDOFF.md](AGENT_HANDOFF.md).

---

## 1. Fork Snapshot Summary

This fork snapshot includes:

- **Full pipeline:** Ingest → LLM extraction → Ground truth load → Compare → Report
- **Five new visualizations** integrated into the main report (Visualizations tab)
- **Fixes** for Mismatch Flow (Legal Framework exclusion) and Term x Framing Heatmap (colours, tokenized terms)
- **Demos** in `presentations/demos/` for reference and prototyping

---

## 2. New Visualizations (Integrated)

| Viz | Purpose | Data source |
|-----|---------|-------------|
| **Mismatch Flow** | LLM framing vs Human framing matrix; diagonal = agreement, off-diagonal = confusion | `comparison_by_doc` aligned_rows (llm_framing, human_framing) |
| **Document Fingerprint** | Per-document framing mix as stacked bars | `stats.per_doc.framings` |
| **Document Similarity** | Cosine similarity of framing profiles between documents | `stats.per_doc.framings` |
| **Terms by Framing** | Top 10 terms (entry_eng/entry_rus) per framing strategy | `comparison_by_doc` aligned_rows |
| **Term x Framing Heatmap** | Top 15 tokenized words × framing strategies; cell = count | Tokenized words from entry_eng/entry_rus, `llm_framing` |

**Compute functions** (in `report/__init__.py`):  
`_compute_mismatch_flow`, `_compute_document_fingerprint`, `_compute_document_similarity`, `_compute_terms_by_framing_detailed`, `_compute_term_framing_heatmap`

**viz_data keys:** `mismatchFlow`, `docFingerprint`, `docSimilarity`, `termsByFramingDetailed`, `termFramingHeatmap`

---

## 3. Fixes Applied (This Session)

### Mismatch Flow — Legal Framework

- **Issue:** Content category "Legal Framework" was appearing in the framing matrix (it belongs to content categories, not framing strategies).
- **Fix:** `fram_order` is built from taxonomy framing strategies only. Content category IDs (`cat_ids`) are excluded when building `fram_order`. `_compute_mismatch_flow` filters to pairs where both llm and human are in `fram_order`. Uses `_normalize_for_group` for "Generic / Neutral" vs "Generic / Neutral Language".

### Term x Framing Heatmap — Colours and Data

- **Issue:** Heatmap had no colour; data was sparse when using full segment text as "terms".
- **Fix:**  
  - CSS: `.heatmap-table .cell-high`, `.cell-mid`, `.cell-low`, `.cell-none` (teal gradient).  
  - Terms: Use **tokenized words** from `entry_eng`/`entry_rus` (min 3 chars, stopwords filtered). Top 15 words by total count across framings.

---

## 4. Key Paths for Fork Maintainers

| Item | Path |
|------|------|
| Report (monolithic) | `report/__init__.py` (~3300 lines) |
| Viz compute functions | `report/__init__.py` lines ~1070–1190 |
| Viz JS rendering | `report/__init__.py` `renderVizPanel` ~2717–2870 |
| Viz CSS | `report/__init__.py` `.flow-matrix`, `.heatmap-table`, `.sim-matrix`, etc. |
| Demos (reference) | `presentations/demos/` |
| Taxonomy | `config/taxonomy.json`, `config/Categories Explained.html` |
| Regenerate report | `python run_report_only.py` |

---

## 5. How to Run and Iterate

```bash
# Full pipeline
python run.py

# Report only (uses saved comparison_results.json)
python run_report_only.py
```

Output: `data/output/manual_analysis_report.html`

To verify viz: Open report → Visualizations tab → Select each new viz from the dropdown.

---

## 6. Data Flow for New Viz

1. `_compute_dataset_stats` → `stats` (categories, framings, per_doc)
2. `fram_order` = taxonomy framing IDs only (excludes content categories)
3. Compute functions use `comparison_by_doc`, `stats`, `fram_order`
4. `viz_data` passed to JS; `renderVizPanel(panelId, data, cfg)` builds HTML

---

## 7. Normalization and Taxonomy

- **`_normalize_for_group`:** Maps "Generic / Neutral" and "Generic / Neutral Language" to canonical form for grouping.
- **Framing colours:** From `config/taxonomy.json`; fallback in `_FRAMING_COLOUR_FALLBACK` in report.
- **Content categories** (do not use in framing viz): Actions, Actors, Places, Time, Documents, Context and Concepts, Legal Framework.

---

## 8. Known Issues / Verification

- **Empty heatmap:** If `fram_order` is empty (e.g. no taxonomy framings) or no tokenized terms pass filters, heatmap will be empty. Check `stats["framings"]` and `comparison_by_doc` aligned_rows.
- **Mismatch Flow:** Ensure `glossary_framings` or taxonomy framing_strategies are loaded; fallback excludes `cat_ids` from `stats["framings"]`.
- **Document Similarity:** Requires `doc_id` in `perDoc` for display-name lookup.

---

## 9. Demos Not in Main Report

These demos exist but were **not** approved for the main report:

- `viz_framing_over_position_demo.html`
- `viz_declassified_progress_demo.html`

---

## 10. References

| Doc | Use |
|-----|-----|
| [AGENT_HANDOFF.md](AGENT_HANDOFF.md) | User feedback, aesthetic direction, visualization ideas |
| [AGENTS.md](../AGENTS.md) | Project summary, key paths, assessment workflows |
| [FRAMEWORK.md](FRAMEWORK.md) | Pipeline contracts, data shapes |
| [NEXT_STEPS.md](NEXT_STEPS.md) | Data locations, config, simple instructions |
| [PLACES_MAP_REFERENCE.md](PLACES_MAP_REFERENCE.md) | Places map scripts and data flow |
