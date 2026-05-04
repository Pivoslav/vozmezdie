# Agent Handoff — Vozmezdie Framework

**For the next agent session.** Read this first, then [AGENTS.md](../AGENTS.md), [NEXT_STEPS.md](NEXT_STEPS.md), and [GRAND_DESIGN_PLAN.md](GRAND_DESIGN_PLAN.md).

**Large UX/UI backlog:** [UI_SCOPE_AND_ROADMAP.md](UI_SCOPE_AND_ROADMAP.md) (single source for meeting-derived tasks, statuses, decisions D1–D5). **UI wording vs stored taxonomy:** [UI_LABEL_MAP.md](UI_LABEL_MAP.md).

---

## 0. Latest Session (Feb 2025) — Start Here

**Planning note (Apr 2026):** Before implementing **per-document visualization dropdowns** and taxonomy-light experiments, see **[PER_DOC_VIZ_BASELINE.md](PER_DOC_VIZ_BASELINE.md)** for where corpus viz lives (`viz-data`, `_homepage`), how taxonomy splits glossary vs pipeline, and what document tabs already contain.

Work completed in the most recent session before handoff:


| Change                       | Location                                                | Notes                                                                                                                                                                                |
| ---------------------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Places map counts**        | `_load_places_map_data_enriched`                        | "By document" and main count now use **segment count** (rows), not sum of extracted numbers. Fixes inflated totals (e.g. Kyiv was 4501).                                             |
| **Places map popup**         | `_write_places_map_html`                                | Segments section is **closed by default** (`<details>` without `open`).                                                                                                              |
| **Word cloud deterministic** | `report/__init__.py` viz JS                             | `shuffle: false`; color from `hashStr(word) % palette.length`. Same layout/colors every load.                                                                                        |
| **Glossary → document nav**  | `_collect_terms_from_comparison`, `_glossary_term_item` | Terms have "View in document" links. `term_locations`: (eng, rus) → [(doc_id, row_index)]. Links use `#tab-{docId}-row-{rowIndex}`; hashchange handler calls `onSectionClickToView`. |
| **Homepage layout**          | `_homepage`                                             | "How Categories and Framing Are Qualified" moved to **bottom** of home page (after Feedback).                                                                                        |
| **Five new viz**             | `report/__init__.py`                                    | Mismatch Flow, Document Fingerprint, Document Similarity, Terms by Framing, Term x Framing Heatmap. Compute functions + JS rendering + CSS. See [HANDOFF_FOR_FORK.md](HANDOFF_FOR_FORK.md). |
| **Mismatch Flow fix**        | `_homepage`, `_compute_mismatch_flow`                   | `fram_order` from taxonomy framings only; excludes content categories (e.g. Legal Framework). Normalizes labels.                                                                     |
| **Term x Framing Heatmap fix** | `_compute_term_framing_heatmap`, CSS                    | Uses tokenized words (not full segments); `.heatmap-table .cell-high/mid/low/none` for teal gradient.                                                                                 |


**Regenerate report:** `python run_report_only.py`

**Fork handoff:** [HANDOFF_FOR_FORK.md](HANDOFF_FOR_FORK.md) — snapshot summary for fork maintainers.

---

## 1. What We Have Done

- **Layout B (sidebar)** — Implemented. Left sidebar: Home, Documents (with both-match %), Glossary. Main area shows content.
- **Homepage** — Boilerplate with three placeholder sections. User will add text later. Link to demos.
- **Collapsible sections** — Stats, document text view, comparison table. Sticky controls on text panels.
- **Feature demos** — `presentations/demos/`: scroll sync, span-to-table, bilingual highlight, dashboard, glossary search. All use fake data.
- **Phase A (Feb 2025)** — Scroll sync in document text view; glossary search in Glossary tab; bilingual highlight dropdowns use full taxonomy from `config/taxonomy.json`.
- **Phase B (Feb 2025)** — Segment search normalization (whitespace collapse); dropdown simplification (taxonomy-only); substring overlap verified.
- **Recent (Feb 2025)** — Colour by Both option (highlights only when LLM and Human agree; obeys all filters); unified `evaluateSegmentFilters` for filter logic; search bar width set to 300px.
- **Phase C (Feb 2025)** — Archival + KGB aesthetic: cream (#f5f0e6), sepia (#8b7355), grey (#4a5568), deep red (#8b0000), institutional green (#2d5a27); Crimson Text serif, JetBrains Mono for IDs; darker sidebar; thin borders; "Declassified" badge in header.
- **Glossary per document (Feb 2025)** — Document dropdown in Glossary tab filters terms by document; `_collect_terms_from_comparison` now returns `term_docs` mapping; terms have `data-docs` for JS filtering.

---

## 2. User Feedback and Requests

### Approved and ready to implement

- **Scroll sync** — User likes it. Add to report: sync scroll between Eng and Rus panels in the document text view. See `presentations/demos/scroll_sync_demo.html`.
- **Glossary search** — User likes it. Add text search over category/framing names and definitions in the Glossary tab. See `presentations/demos/glossary_search_demo.html`.

### Approved, with constraints

- **Bilingual highlight** — User likes it and feels it matches what they are trying to do. **Critical:** Use the project’s taxonomy filters, not the demo’s. The demo uses fake categories (Actions, Actors, Context) and framings (Action-Focused, Institutional, Generic). The real report must use:
  **Content categories** (from `config/taxonomy.json`):  
  Actions | Actors | Places | Time | Documents | Context and Concepts | Legal Framework
  **Framing strategies**:  
  Generic / Neutral Language | Institutional / Bureaucratic Lingo | Ideological Framing (Discrediting) | Ideological Phrasing (Normalizing) | Action-Focused Language
  The report already uses these; the demo was illustrative only. Ensure dropdown options and filter behaviour match the taxonomy exactly (including "Generic / Neutral" and "Generic / Neutral Language" normalization — see `report/__init__.py` `canonicalFramingOption`).

### Tabled for later (make note)

- **Click word for definition** — User prefers that clicking a word/segment shows a **definition** (not jumping to the table row). Each term would need definitions in Russian and English. This is a substantial change: a term glossary keyed by segment text, with EN/RU definitions. Worth doing, but not for the immediate next phase. **Action:** Add to backlog; do not implement yet. Document the requirement: click on segment -> tooltip/popover with definition in both languages.

---

## 3. Canonical Taxonomy (Reference)

Use these exact labels **in data** (ground truth, comparison JSON, LLM outputs). Source: `config/taxonomy.json`, `config/Categories Explained.html`.

**UI umbrella terms:** The report may present these dimensions as **Specific Details** (content categories) and **Ideological Layers** (framing) without changing stored strings — see [UI_LABEL_MAP.md](UI_LABEL_MAP.md).


| Content categories   | Framing strategies                 |
| -------------------- | ---------------------------------- |
| Actions              | Generic / Neutral Language         |
| Actors               | Institutional / Bureaucratic Lingo |
| Places               | Ideological Framing (Discrediting) |
| Time                 | Ideological Phrasing (Normalizing) |
| Documents            | Action-Focused Language            |
| Context and Concepts |                                    |
| Legal Framework      |                                    |


---

## 4. Aesthetic Direction: Archival + KGB

User wants the visual style to reflect **archival** documents and a **KGB aesthetic**. Think:

- **Archival:** Faded paper, typewriter or period-appropriate typography, stamps, tape, ageing marks, document-like backgrounds. Sepia, cream, grey. Physicality of declassified files.
- **KGB / Soviet bureaucratic:** Red accents (sparing), institutional greens and greys, stencil or bureaucratic lettering, stamp motifs, file-number style IDs. Cold, formal, slightly ominous. Think: declassified file folders, rubber stamps, official letterhead.

**Concrete suggestions:**

- Palette: cream (#f5f0e6), sepia (#8b7355), grey (#4a5568), deep red (#8b0000 or #991b1b) for accents (e.g. headers, highlights), institutional green (#2d5a27) for matches.
- Typography: serif for headings (e.g. "Archivo", "Crimson Text", or similar); monospace or typewriter-style for document IDs and codes.
- Borders: thin, dark; box shadows that suggest depth but stay restrained.
- Optional motifs: subtle watermark, stamp-like badges for "Declassified" or document IDs, tape/staple visual cues at corners.
- Sidebar: darker, more institutional (charcoal, dark grey). Could read as a "file drawer" or index.

**Avoid:** Overly playful, tech-startup gradients, or anything that feels anachronistic. The tone should be serious, scholarly, and evocative of the archive.

---

## 5. Outside the Box: Insights, Visualizations, Bringing Documents to Life

The user wants to **bring these documents into the light** — not just compare labels, but surface insights and make the archival material resonate.

### 5.1 Insights we can glean from the data

- **Framing distribution over time** — If documents have dates or sections, how does ideological framing (discrediting, normalizing) vs neutral vs action-focused shift across periods?
- **Actor networks** — Which actors appear with which framings? Who is discredited vs normalized? Co-occurrence of actors and framings.
- **Mismatch patterns** — Where does the LLM systematically disagree with humans? E.g. overuse of "Generic" when humans see "Ideological"? Category confusion (Actions vs Actors)?
- **Term frequency by category/framing** — Which terms cluster in Action-Focused vs Institutional? Vocabulary of discrediting vs neutral language.
- **Cross-document comparison** — Which documents have highest/lowest agreement? Which framing strategies dominate per document?
- **Rare categories** — Legal Framework, Places, Time: how often do they appear? Distribution across the corpus.

### 5.2 Visualization ideas

- **Heatmap** — Document x Category (or Framing): cell colour = frequency or agreement %. Reveals which docs lean toward which labels.
- **Sankey or flow** — LLM label -> Human label: show where labels "flow" when they disagree. E.g. LLM "Generic" -> Human "Ideological (Discrediting)".
- **Timeline** — If temporal data exists: framing intensity over time. When does ideological language spike?
- **Word clouds or bar charts** — Top terms per category, per framing. "What words signal Action-Focused vs Generic?"
- **Network graph** — Actors as nodes; edges = co-occurrence in same segment or document. Colour by framing.
- **Document "portrait"** — Single-doc summary: pie or bar of category/framing mix. Quick characterisation of each document.
- **Comparison radar** — For a document: category accuracy, framing accuracy, both-match as axes. Compare docs visually.

### 5.3 Bringing documents into the light

- **Narrative mode** — Read-through view: document text with inline annotations, like marginalia. "As you read, you see: this phrase was framed as Ideological (Discrediting); this one as Action-Focused."
- **Spotlight on mismatches** — A view that highlights only disagreements. "Here is where human and machine diverge — focus on these."
- **Export as "research packet"** — PDF or HTML bundle: document + annotations + glossary + summary stats. Shareable for researchers.
- **Audio or TTS** — (Stretch.) Read document aloud with category/framing announced at each segment. Accessibility + different engagement.
- **"Declassified" stamp** — When a document is fully assessed and validated, visual badge: "Reviewed" or "Declassified". Gives a sense of progress and trust.

---

## 6. Implementation Plan for Next Agent

### Phase A: Quick wins (completed Feb 2025)

1. **Scroll sync** — Done. Scroll sync between `doc-text-eng-{doc_id}` and `doc-text-rus-{doc_id}` panels. Logic copied from `scroll_sync_demo.html`, integrated in `report/__init__.py` via `initScrollSyncForDoc(tid)` called from `onDocumentTabShown`.
2. **Glossary search** — Done. Search input in Glossary tab; filters `.glossary-searchable-section` by text match on `data-text` (name + description + examples). Pattern from `glossary_search_demo.html`.
3. **Bilingual highlight taxonomy** — Done. Dropdown options now use `TAXONOMY_ALL_CATEGORIES` and `TAXONOMY_ALL_FRAMINGS` (from taxonomy.json) instead of document-derived labels. Added note to `bilingual_highlight_demo.html` that the demo uses illustrative labels; production uses the project taxonomy.

### Phase B: Bug fixes (completed Feb 2025)

- **Segment search normalization (2.2)** — Done. Added `_normalize_segment_for_search()` to collapse whitespace; `_get_accepted_segments` uses it so "word1  word2" and "word1\nword2" match. Regex fallback uses normalized segment.
- **Dropdown simplification when hasPreFilled (2.1)** — Done. Removed table/span-derived category/framing collection; dropdowns always use TAXONOMY_ALL_CATEGORIES and TAXONOMY_ALL_FRAMINGS.
- **Substring overlap (2.3)** — Verified. Sort by (length, position) already ensures shorter segments win; docstring clarified.

### Phase C: Aesthetic (archival + KGB) — completed Feb 2025

- Applied palette: cream, sepia, grey, deep red, institutional green; Crimson Text + JetBrains Mono; darker sidebar; "Declassified" badge in header.

### Phase D: Backlog (tabled)

- **Stakeholder UX roadmap** — Landing page (separate HTML), PDF/image wheel, Research Lab rename, comparison table rename, legend UX, horizontal reader, Cyrillic keyboard, highlight overlay fix, glossary/analytics merge, etc.: tracked in [UI_SCOPE_AND_ROADMAP.md](UI_SCOPE_AND_ROADMAP.md). Implement in slices; update epic statuses there when done.
- **Click word for definition** — Requires EN/RU term definitions per segment. Design: segment -> tooltip with definition_eng, definition_rus. Data source: new config file or extension of glossary.
- **Glossary per document** — Done. Dropdown in Glossary tab filters terms by document; `data-docs` on each term; `term_docs` in `_collect_terms_from_comparison`.
- **Glossary → document nav** — Done. Terms have "View in document" links; `term_locations` maps (eng, rus) to (doc_id, row_index); `#tab-{docId}-row-{rowIndex}` triggers scroll-to-segment.
- Dashboard view (aggregate stats as landing optional)
- Visualization prototypes (heatmap, Sankey, etc.)

---

## 7. Key Paths


| Item                 | Path                                                             |
| -------------------- | ---------------------------------------------------------------- |
| Report module        | `report/__init__.py`                                             |
| Taxonomy             | `config/taxonomy.json`, `config/Categories Explained.html`       |
| Demos                | `presentations/demos/`                                           |
| Scroll sync demo     | `presentations/demos/scroll_sync_demo.html`                      |
| Glossary search demo | `presentations/demos/glossary_search_demo.html`                  |
| Places map (report)  | `data/output/places_map.html` (generated with report)            |
| Places extraction    | `scripts/extract_places.py`, `data/output/places_extracted.json` |
| Run report only      | `python run_report_only.py`                                      |
| Tests                | `tests/test_report.py`                                           |


---

## 7a. Handoff Tips for Next Agent

- **Work incrementally:** Prefer small, focused edits. Regenerate with `python run_report_only.py` after report changes.
- **Report is monolithic:** All HTML/CSS/JS lives in `report/__init__.py` (~2950 lines). Use grep/search to find functions (e.g. `_load_places_map_data_enriched`, `_glossary_term_item`, `_homepage`).
- **Hash navigation:** `#tab-{docId}-row-{rowIndex}` switches to document tab and scrolls to segment. Used by glossary "View in document" and places map "View" links.

---

## 8. References

- [UI_SCOPE_AND_ROADMAP.md](UI_SCOPE_AND_ROADMAP.md) — Canonical UX backlog and decisions
- [UI_LABEL_MAP.md](UI_LABEL_MAP.md) — UI labels ↔ JSON/taxonomy mapping
- [AGENTS.md](../AGENTS.md) — Project summary, key paths
- [NEXT_STEPS.md](NEXT_STEPS.md) — Handoff, data locations
- [GRAND_DESIGN_PLAN.md](GRAND_DESIGN_PLAN.md) — Layout options, roadmap
- [DESIGN_EXPLORATION.md](DESIGN_EXPLORATION.md) — Known issues, incremental ideas
- [TEXT_VIEW_ASSESSMENT.md](TEXT_VIEW_ASSESSMENT.md) — Document text view behaviour, fixes
- [INSTRUCTIONS_AGENT_ASSESSMENT.md](INSTRUCTIONS_AGENT_ASSESSMENT.md) — Taxonomy labels, assessment workflow
- [PLACES_MAP_REFERENCE.md](PLACES_MAP_REFERENCE.md) — Places map scripts, data flow, segment-count fix

