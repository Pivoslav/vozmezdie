# Grand Design Plan — Vozmezdie Report GUI

A brainstorm document for the frontend vision: layout, features, user experience, and long-term direction. Exploratory, not prescriptive.

---

## 1. Vision and Goals

**What the tool is:** An expert-grounded LLM evaluation report for Cold War archival documents. Users compare human-coded ground truth to LLM (or agent) extractions: content categories and framing strategies per segment.

**Core user goals:**
- **Review** — Understand how well the model matches human annotations; spot patterns and errors.
- **Assess** — Perform blind or standard manual assessment; record category and framing.
- **Reference** — Look up taxonomy definitions; see terms in context across documents.

**Design principles:**
- **Focus** — Long documents and 17+ docs mean information overload. Prioritize one task at a time.
- **Bilingual parity** — English and Russian must stay in sync; comparison is central.
- **Low friction** — Single-file HTML, no build step; runs offline after pipeline.
- **Accessibility** — Keyboard navigation, screen-reader-friendly structure.

---

## 2. User Personas and Primary Flows

| Persona | Primary task | Pain points |
|---------|-------------|-------------|
| **Reviewer** | Compare LLM vs human; write up findings | Switching between table and text; finding mismatches; getting lost in long docs |
| **Assessor** | Label segments (category + framing); stay blind or compare | Taxonomy lookup; chunk progress; exporting/importing work |
| **Researcher** | Cross-document patterns; term frequency; framing distribution | No aggregate view; glossary separate from data |

**Primary flows to optimize:**
1. **"Show me mismatches"** — Filter to category/framing mismatches; jump from table to text.
2. **"What does this term mean?"** — Hover or click term in text view -> definition tooltip or glossary scroll.
3. **"Where am I in this document?"** — Scroll sync; table row highlights when viewing text.
4. **"Compare across documents"** — Summary dashboard; per-doc stats at a glance.

---

## 3. Layout Options

### Option A: Current — Flat tabs
- Tabs for each document + Glossary; one active at a time.
- **Pros:** Simple, familiar, no extra navigation.
- **Cons:** Document list grows (17+); horizontal space cramped; no persistent navigation.

### Option B: Sidebar + main content
- Left sidebar: document list (with mini-stats) + Glossary; main area: selected document content.
- **Pros:** Persistent doc list; more horizontal space; can show aggregate stats in header.
- **Cons:** Sidebar takes width; narrower on small screens.

### Option C: Dashboard-first
- First view: aggregate stats, mismatch summary, doc list; click doc -> detail view.
- **Pros:** Overview before detail; good for "what needs attention?"
- **Cons:** Extra click to content; may feel redundant if user always goes to one doc.

### Option D: Split-view (document-centric)
- Top: document selector + stats.
- Bottom: two-pane layout — text view (Eng | Rus) and table side-by-side, or stacked.
- **Pros:** Everything visible; no tab switching within a doc.
- **Cons:** Crowded on smaller screens; table can be very long.

**Recommendation:** **B (Sidebar)** for 10+ documents; **A (Flat tabs)** if we stay under ~8 docs. Consider **C (Dashboard)** as an optional landing view even with sidebar.

**Implemented (Feb 2025):** Layout B (sidebar) is now the default. Homepage with placeholders added as the landing view. See `report/__init__.py`.

---

## 4. Feature Inventory (Current + Proposed)

### 4.1 Navigation and structure
| Feature | Status | Notes |
|---------|--------|-------|
| Tab per document | Done | Flat tabs |
| Glossary tab | Done | Categories Explained + terms from docs |
| Collapsible sections | Done | Stats, text view, table |
| Sidebar navigation | Proposed | Replace or complement tabs |
| Summary dashboard | Proposed | Aggregate stats, mismatch counts |
| Breadcrumb / "You are here" | Proposed | Doc name, section, current filter |

### 4.2 Document text view
| Feature | Status | Notes |
|---------|--------|-------|
| Two panels (Eng, Rus) | Done | |
| Search in text | Done | Highlights matches |
| Category filter | Done | Dropdown |
| Framing filter | Done | Dropdown |
| Colour by LLM/Human | Done | Toggle |
| Sticky controls | Done | When scrolling |
| Scroll sync (Eng <-> Rus) | Proposed | Panels stay aligned |
| Click span -> table row | Tabled | User prefers click-word-for-definition instead |
| Click word -> definition (EN+RU) | Backlog | User requested; requires term glossary with definitions in both languages |
| Hover term -> tooltip | Proposed | Short definition |
| Keyboard: next/prev span | Proposed | Arrow keys |

### 4.3 Comparison table
| Feature | Status | Notes |
|---------|--------|-------|
| Match/mismatch colouring | Done | Green/red |
| LLM vs Human columns | Done | Category, framing |
| Sticky header | Partial | Some browsers |
| Sort by column | Proposed | Section, match status |
| Filter by match status | Proposed | Matches only, mismatches only |
| Pagination / virtual scroll | Proposed | Long tables |
| Row highlight on text click | Proposed | Link from text view |

### 4.4 Glossary
| Feature | Status | Notes |
|---------|--------|-------|
| Definitions from CE | Done | |
| Terms by category/framing | Done | From aligned rows |
| Search / filter | Proposed | Text search over names + definitions |
| Expand/collapse sections | Proposed | Categories, Framing |
| Link from legend to entry | Proposed | Click swatch -> scroll |
| Print-friendly view | Proposed | Collapsed, compact |

### 4.5 Assessment workflow
| Feature | Status | Notes |
|---------|--------|-------|
| Export segments only | Done | Blind assessment |
| Script merge to agent_assessments | Done | Python scripts |
| Chunk progress indicator | Proposed | % assessed per doc |
| In-report label edit | Proposed | High effort; file write or API |
| Dedicated assessment UI | Proposed | Separate page/mode |
| Keyboard shortcuts | Proposed | 1–7 category, A–E framing |

### 4.6 Output and export
| Feature | Status | Notes |
|---------|--------|-------|
| Single HTML report | Done | |
| EN/UK i18n | Partial | Some labels |
| Export filtered rows to CSV | Proposed | Current view |
| Export to PDF | Proposed | Print CSS |
| Shareable link with state | Proposed | URL params for doc, filters |

---

## 5. Visual Design Direction

### 5.1 Current aesthetic
- Gradient header (purple/blue)
- Light grey background (#f8f9fa)
- White cards, rounded corners
- Match = green, mismatch = red

### 5.2 Possible directions

**A. Refined current** — Same palette, cleaner hierarchy. Slightly more contrast, better typography scale. Low risk.

**B. Archival / KGB** — User-requested. Archival documents + Soviet bureaucratic aesthetic: cream/sepia/grey, red accents, serif headings, stamp motifs, institutional tone. See [AGENT_HANDOFF.md](AGENT_HANDOFF.md) section 4.

**B-alt. Archival / scholarly** — Warmer, paper-like. Sepia accents, serif headings. Evokes document analysis.

**C. Minimal / neutral** — Near monochrome; colour only for data (category, framing, match status). Focus on content.

**D. Dark mode** — Toggle for long sessions; reduce eye strain.

**Recommendation:** **A (Refined)** as default; **D (Dark)** as future option if users request it. Avoid **B** unless it resonates with the team — can feel gimmicky.

### 5.3 Typography and density
- Consider a slightly larger base font for long reading (document text).
- Tighter line-height in table; looser in prose (glossary).
- Consistent spacing scale (e.g. 4px, 8px, 16px, 24px).

---

## 6. Technical Architecture for Frontend

### Current
- Single HTML file; inline CSS and JS in Python strings.
- No build step; no frameworks.

### Options for evolution

**A. Stay monolithic** — Keep one file; extract CSS/JS to separate strings or `report/static/` files that get inlined at build time. Easiest.

**B. Template split** — Python builds a JSON data structure; a simple template (Jinja, or even a single HTML with `{{ placeholders }}`) renders it. Enables non-Python contributors to edit layout.

**C. SPA / framework** — React/Vue/Svelte; load `comparison_results.json`; render client-side. More flexibility, but adds build, deployment, and offline story.

**D. Progressive enhancement** — Start with server-rendered HTML (current); add JS for interactions (scroll sync, click-to-table). No framework.

**Recommendation:** **D (Progressive enhancement)** for now. Add features with vanilla JS. Consider **B (Template split)** when the report module exceeds ~1200 lines or when layout changes become frequent. Avoid **C** unless we need real-time updates or a full app.

---

## 7. Phased Roadmap

### Phase 1: Polish (low risk)
- Bug fixes: segment search, dropdown simplification, substring overlap.
- Glossary search/filter.
- Scroll sync for text panels.
- i18n expansion (EN/UK).

### Phase 2: Layout shift
- Sidebar navigation (if doc count justifies).
- Summary dashboard (optional landing).
- Click span -> table row; table row -> scroll to span.

### Phase 3: Assessment support
- Chunk progress indicator.
- Export filtered view to CSV.
- Tooltip on term hover (glossary preview).

### Phase 4: Deeper changes
- Template split.
- Dark mode.
- Dedicated assessment UI (if workflow demands it).
- In-report editing (if we solve persistence).

---

## 8. Open Questions

1. **How many documents will we typically have?** Sidebar vs tabs depends on this.
2. **Do assessors prefer a separate tool or in-report editing?** Affects Phase 4.
3. **Is EN/UK i18n a requirement or nice-to-have?** Affects Phase 1 scope.
4. **Print/PDF:** Do users need to print reports? If yes, Phase 1 or 2 should include print CSS.
5. **Mobile/tablet:** Is this desktop-only? Mobile changes layout priorities (stack everything, no sidebar).

---

## 9. Insights and Visualizations (Outside the Box)

See [AGENT_HANDOFF.md](AGENT_HANDOFF.md) section 5 for: insights we can glean (framing over time, actor networks, mismatch patterns), visualization ideas (heatmaps, Sankey, timelines, word clouds, document portraits), and ways to "bring documents into the light" (narrative mode, spotlight on mismatches, research packet export).

---

## 10. References

- [AGENT_HANDOFF.md](AGENT_HANDOFF.md) — Primary handoff: user feedback, aesthetic direction, implementation plan
- `presentations/vozmezdie_gui_design_pitch.html` — HTML presentation of this design pitch (reveal.js)
- [DESIGN_EXPLORATION.md](DESIGN_EXPLORATION.md) — Incremental ideas, known issues
- [AGENTS.md](../AGENTS.md) — Project summary, key paths
- [FRAMEWORK.md](FRAMEWORK.md) — Pipeline contracts
- `report/demo_report_reference.html` — Reference layout
- `dev/analysis_w_text_highlight.html` — Text view reference
