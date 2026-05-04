# UI / UX scope and roadmap (canonical backlog)

**Purpose:** One place for stakeholders and agents to see **what was requested**, **what was decided**, and **what remains**. Meeting notes were consolidated here so scope stays unambiguous.

**Companion:** [UI_LABEL_MAP.md](UI_LABEL_MAP.md) — exact rules for **Specific Details** / **Ideological Layers** vs stored taxonomy strings.

---

## 1. Authoritative decisions (do not contradict without new sign-off)

| # | Decision | Implication |
|---|-----------|-------------|
| D1 | **UI-only renaming** for “content categories” / “framing” umbrella terms | Change copy in report + landing via translations/HTML; **do not** change canonical label strings in `comparison_results.json`, GT HTML, or `taxonomy.json` without a separate data migration. Follow [UI_LABEL_MAP.md](UI_LABEL_MAP.md). |
| D2 | **Landing page = separate new HTML file** | Not the generated `manual_analysis_report.html` home tab alone; a distinct entry page (path TBD when implemented; likely under `landing/` or `presentations/`). |
| D3 | **PDF ≡ image wheel** | One conceptual feature: primary surface for scans. Prefer embedding **PDF** when assets exist; otherwise a **slideshow-style** viewer (images). Document manifest in config (e.g. extend `document_map.json` — see §6). |
| D4 | **Video** | **Placeholder only** on landing until a real embed URL exists (YouTube/Vimeo/unlisted). |
| D5 | **Paper / academic prose** | **Out of scope** for this roadmap item (e.g. mismatches, AI bias narrative in the paper). No requirement to edit manuscript text in-repo unless separately requested. |

---

## 2. Git workflow expectation

**Goal:** Modular history and review.

- **One feature per branch** (or one coherent epic slice), merge via PR or explicit merge after smoke test.
- **Suggested branch naming:** `feat/landing-page`, `feat/pdf-view`, `fix/highlight-overlay`, `ui/specific-details-copy`, etc.
- **Smoke test after report changes:** `python run_report_only.py` (or full `run.py` when pipeline touched).

---

## 3. Status legend

| Status | Meaning |
|--------|---------|
| **Planned** | Agreed, not started |
| **In progress** | Active branch / partial implementation |
| **Done** | Shipped in default workflow |
| **Deferred** | Explicitly later or blocked on data/design |
| **Cancelled** | Superseded; do not implement unless reopened |

*(Update statuses as work lands.)*

---

## 4. Epic inventory (from meeting notes + decisions)

### E0 — Documentation (this wave)

| ID | Item | Status | Notes |
|----|------|--------|-------|
| E0.1 | `UI_LABEL_MAP.md` + `UI_SCOPE_AND_ROADMAP.md` | Done | Canonical references for agents |
| E0.2 | Index handoff docs → link here | Done | `README.md`, `NEXT_STEPS.md`, `AGENT_HANDOFF.md`, root `AGENTS.md` |

### E1 — Landing + entry experience

| ID | Item | Status | Acceptance criteria (high level) |
|----|------|--------|-----------------------------------|
| E1.1 | Standalone **landing** HTML | Planned | Explains what users can do (a–d style bullets); highlights analytical framing; CTA to open **Research Lab / Analytics** report |
| E1.2 | **Video placeholder** | Planned | Obvious reserved region + short caption (“Video coming soon” or similar); easy swap for iframe/embed later |
| E1.3 | **Analytical Framework** section on landing | Planned | Lay language: Specific Details → bridge to Content Data; Ideological Layers → Language Data; optional diagram title “Vozmezdie Analytical Framework” |
| E1.4 | Rename report sidebar **Home** → **Research Lab** / **Analytics** | Planned | Align wording with “current homepage becomes lab”; `data-i18n` + UK |

### E2 — PDF / image wheel (single feature)

| ID | Item | Status | Acceptance criteria |
|----|------|--------|---------------------|
| E2.1 | Config contract for **PDF path(s)** or **image list** per `document_id` | Planned | Document in `document_map.json` schema or adjacent JSON; fail gracefully if missing |
| E2.2 | Per-document **PDF view** UI | Planned | Clearly labeled (e.g. “PDF view” / “Scanned document”); embed PDF **or** slideshow |
| E2.3 | Optional **AI summary** copy per doc | Deferred | Slideshow sidecar or overlay — needs content source |

### E3 — Report IA / navigation / document layout

| ID | Item | Status | Notes |
|----|------|--------|-------|
| E3.1 | **Comparison table** rename | Planned | e.g. “Human-led vs AI-led Analysis — Comparison Table” ([UI_LABEL_MAP](UI_LABEL_MAP.md)) |
| E3.2 | **Legend**: collapsible / dropdown / sticky / modal | Planned | Pick best UX; must stay usable on narrow screens |
| E3.3 | Per-document **dropdown areas** (image/PDF, transcription, search & analysis, viz, human vs AI) | Planned | Major `_doc_tab` / CSS refactor |
| E3.4 | **Headers + helper text** above document-view filters | Planned | Specific Details / Ideological Layers + four bullets from meeting notes (search specifics, highlight ideological layers, compare intersections, viz human vs AI) |
| E3.5 | **Horizontal reader** (Internet Archive–style) | Planned | Layout toggle or dedicated mode |
| E3.6 | **Cyrillic virtual keyboard** for search | Planned | Client-side insert into search input |
| E3.7 | Open **analytics in new tab** from selected controls | Planned | Define which widgets; stable URL/hash |
| E3.8 | Per-document tab for **analytics** | Planned | Aggregates doc-level stats/charts |
| E3.9 | **Glossary + Analytics** merge | Planned | Single nav or tabbed combined view |

### E4 — Feedback + exports

| ID | Item | Status | Notes |
|----|------|--------|-------|
| E4.1 | Feedback as **popup per label** | Planned | Replace or augment inline “suggest” UX |
| E4.2 | Optional **Export comparison table to JSON** | Planned | Nice-to-have for researchers |

### E5 — Copy / glossary / lab content

| ID | Item | Status | Notes |
|----|------|--------|-------|
| E5.1 | Apply **Specific Details** / **Ideological Layers** across report strings | Planned | `_UI_TRANSLATIONS` + glossary headings |
| E5.2 | **Lab** page: remove or hide **Dataset Statistics** | Planned | Per stakeholder request |
| E5.3 | Glossary: remove “Purpose” prefix before descriptions | Deferred | May touch `Categories Explained.html` or report renderer — clarify CE vs template |
| E5.4 | Taxonomy **content** edits (drop Generic category, Information, Methods, Status, Contexts; rename Time; Events/Material Resources/Purpose wording) | **Deferred** | These change **canonical labels** → data migration, not UI-only. See [UI_LABEL_MAP.md §6](UI_LABEL_MAP.md). |

### E6 — Bugs + housekeeping

| ID | Item | Status | Notes |
|----|------|--------|-------|
| E6.1 | Highlight **grey overlay** bug (seen on doc **1208**) | Planned | Z-index / filter-active stacking; verify other docs |
| E6.2 | **Rename files** with clearer names | Planned | Inventory paths; avoid breaking ingest/report references |

### E7 — Process / visibility

| ID | Item | Status | Notes |
|----|------|--------|-------|
| E7.1 | **GitHub**: branches per feature | Ongoing | Human process; document in CONTRIBUTING if repo goes public |

---

## 5. Meeting-note bullets → epic mapping (quick reference)

| Original ask | Epic ID |
|--------------|---------|
| Branches, one feature at a time | E7.1 |
| Landing pages + video | E1 |
| PDF / slideshow / AI summary | E2 |
| Legend collapsible / dropdown / sticky | E3.2 |
| Research Lab / Analytics (ex-home) | E1.4 |
| Feedback popups | E4.1 |
| Horizontal IA-style reader | E3.5 |
| Combine glossary + analytics | E3.9 |
| Rename comparison tables | E3.1 |
| New tab for page analytics | E3.7 |
| Homepage a,b,c,d capabilities | E1.1 |
| Export JSON | E4.2 |
| Headers above config dropdowns + 4 bullets | E3.4 |
| Virtual Cyrillic keyboard | E3.6 |
| Per-document layout dropdowns | E3.3 |
| Dataset stats off lab | E5.2 |
| Grey overlay highlight bug | E6.1 |
| Taxonomy removals / renames in **data** | E5.4 Deferred |

**Paper / mismatch narrative / AI bias (paper):** explicitly **out of scope** (D5).

---

## 6. PDF / image wheel — config direction and verification

**Current behaviour:** `ingest` forwards optional `pdf_relative_path` and `scan_images` from `document_map.json` into each document record. The report renders a per-document **PDF view** collapsible: embedded iframe when the resolved file exists, otherwise short placeholder copy. A slideshow viewer for `scan_images` is **not** implemented yet.

**Suggested convention** (same as before; extend when the image wheel ships):

- Extend each document entry in `config/document_map.json` (or a parallel file) with optional fields, for example:
  - `"pdf_relative_path": "data/scans/1208.pdf"` **or**
  - `"scan_images": ["data/scans/1208/page01.jpg", ...]`
- Resolve paths **relative to the repository root** (the directory that contains `run.py`).
- If neither field is usable: keep the placeholder branch (no silent failure).

**Local verification**

- Example: `"pdf_relative_path": "data/scans/1208.pdf"` — place the file under that path relative to repo root.
- Opening `data/output/manual_analysis_report.html` via **file://** may block iframes or PDF embedding in some browsers; serve the folder over HTTP locally if the PDF area stays blank.

---

## 7. Deferred cluster rationale (taxonomy content)

Requests like **remove Generic framing**, **delete Methods category**, **rename Time → Date & Time** in the **data** change agreement metrics, historical comparisons, and stored GT. They belong to:

1. Expert consensus on new taxonomy version  
2. Migration scripts + re-run pipeline  
3. Optional compatibility layer in `compare/`

Do **not** implement as pure CSS/copy without D1 sign-off change.

---

## 8. References

| Doc | Role |
|-----|------|
| [UI_LABEL_MAP.md](UI_LABEL_MAP.md) | UI ↔ data string rules |
| [FRAMEWORK.md](FRAMEWORK.md) | JSON shapes |
| [GRAND_DESIGN_PLAN.md](GRAND_DESIGN_PLAN.md) | Broader design brainstorm |
| [DESIGN_EXPLORATION.md](DESIGN_EXPLORATION.md) | Incremental UX ideas |
| [TEXT_VIEW_ASSESSMENT.md](TEXT_VIEW_ASSESSMENT.md) | Document text view behaviour |
| [FILTER_DIMMING_INVESTIGATION.md](../FILTER_DIMMING_INVESTIGATION.md) | May relate to E6.1 overlay |

---

## 9. Changelog

| Date | Change |
|------|--------|
| 2026-04-01 | Initial scope doc from meeting notes + D1–D5 decisions |
| 2026-04-01 | Stage 2: glossary i18n + params/tooltips; glossary summary spans preserved under filters; document/comparison toolbar grids; §6 PDF verification notes |
| 2026-04-01 | Stage 3 (partial): hashes `#tab-{docId}-sec-{pdf|text|compare}`, `#tab-home-viz-{viz}`; doc jump links; reader layout toggle (persisted); “Open this chart in new tab”; `lab-visualizations` anchor; hash-nav `setTimeout` brace fix |
