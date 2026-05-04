# UI labels ↔ data model (canonical mapping)

**Purpose:** Prevent ambiguity when renaming user-visible strings. Agents must treat this file as the reference when editing copy in the report or landing pages.

**Policy (confirmed):** User-facing names may say **Specific Details** and **Ideological Layers** (and related phrasing). **Underlying data must keep canonical taxonomy strings** exactly as stored in `config/taxonomy.json`, ground truth HTML, LLM output, and `comparison_results.json`. Do **not** rename category/framing values in JSON or HTML rows unless running a dedicated **data migration** project (separate from UI-only work).

---

## 1. Conceptual layers (how language maps to code)

| Layer | English UI term (target) | Technical / pipeline term | Notes |
|-------|--------------------------|---------------------------|--------|
| Reader-facing | **Specific Details** | Content categories | Describes *what* the segment is about (actors, places, time, …). |
| Reader-facing | **Ideological Layers** | Framing strategies | Describes *how* the segment is phrased (neutral, bureaucratic, ideological, …). |
| More technical copy | **Content Data** | Same as content categories | Use on homepage/analytical framework when bridging lay → technical. |
| More technical copy | **Language Data** | Same as framing strategies | Same as above. |

These pairs are **synonyms for presentation**, not separate dimensions in the database.

---

## 2. JSON / Python field names (do not rename for UI work)

Aligned comparison rows and related structures use these keys (see [FRAMEWORK.md](FRAMEWORK.md)):

| Field | Meaning |
|-------|---------|
| `human_category` | Human-assigned content category (canonical string) |
| `llm_category` | LLM-assigned content category (canonical string) |
| `human_framing` | Human-assigned framing (canonical string) |
| `llm_framing` | LLM-assigned framing (canonical string) |

Ground truth and ingest may use labels such as `content_category` and `framing` in spreadsheets/HTML columns; they must match taxonomy ids after normalization.

---

## 3. Taxonomy file ↔ stored values

**Source:** `config/taxonomy.json`

- **Content categories** live in `taxonomy["content_categories"]`. Each item has at least `id` (the value stored in data rows). Display labels may use `label_en` / `label_uk` in some contexts, but filters and comparisons match **`id`** (and aliases documented in report JS, e.g. framing normalization).
- **Framing strategies** live in `taxonomy["framing_strategies"]`. Same rule: persisted values align with **`id`** where the pipeline writes them; UI may show `label_en` / `label_uk`.

**Authoritative definitions** for humans: `config/Categories Explained.html` when present (merged into taxonomy at report generation per pipeline config).

### Current canonical content category `id` values (as of taxonomy.json)

Use exact spelling for data; UI copy may describe them under “Specific Details”:

| `id` in data |
|----------------|
| Actions |
| Actors |
| Places |
| Time |
| Documents |
| Context and Concepts |
| Legal Framework |

### Current canonical framing `id` values (representative)

| Example `id` / stored forms |
|-----------------------------|
| Generic / Neutral |
| Generic / Neutral Language |
| Institutional / Bureaucratic Lingo |
| Ideological Framing (Discrediting) |
| Ideological Phrasing (Normalizing) |
| Action-Focused Language |

Report code normalizes some framing aliases (e.g. “Generic / Neutral” vs “Generic / Neutral Language”). Do not remove normalization without checking compare/report/tests.

---

## 4. UI translation keys (report)

Report strings are centralized in `report/__init__.py` in **`_UI_TRANSLATIONS`** (dict keyed by logical id, values `{ "en": "...", "uk": "..." }`).

When changing user-visible wording:

1. Prefer editing **`_UI_TRANSLATIONS`** entries (and any `data-i18n="..."` attributes that reference those keys).
2. Keep **dropdown `<option>` values** and **segment `data-*` attributes** on canonical taxonomy strings unless implementing a full remap layer.
3. Update this document if introducing **new** umbrella terms or keys.

### Mapping table: old ↔ new reader-facing labels (UI only)

| Typical old UI string | New UI string (English target) | Typical `_UI_TRANSLATIONS` key(s) to adjust |
|-----------------------|---------------------------------|---------------------------------------------|
| Content Categories | Specific Details | `content_categories`, `content_categories_stats`, glossary headings, etc. |
| Content Category (column) | Specific Detail / Specific Details (pick one consistently) | `content_category` |
| Framing (column / section) | Ideological Layer(s) | `framing`, `framing_text_colour`, related viz strings |
| Framing strategies / language strategy (section titles) | Ideological Layers (+ subtitle as needed) | `framing_categories`, `framing_strategies_stats`, `framing_categories_desc` |
| Home (sidebar; analytics hub) | Research Lab / Analytics | `home` (or new key if split) |
| Comparison table | Human-led vs AI-led Analysis — Comparison Table | `comparison_table` |

Ukrainian strings must be updated in parallel for every changed English string.

---

## 5. Landing page vs report

- **Standalone landing** (separate HTML file, not generated by `report.run()`): may use plain English/Ukrainian without `_UI_TRANSLATIONS`. Copy should still **respect the same conceptual mapping** (Specific Details ↔ content categories, etc.) so users are not confused when they open the report.
- **Link target:** Generated report path is normally `data/output/manual_analysis_report.html` (relative path from repo root depends on where the landing file lives — document the chosen path in [UI_SCOPE_AND_ROADMAP.md](UI_SCOPE_AND_ROADMAP.md) when the landing file is added).

---

## 6. Future: data migration (out of scope for UI-only policy)

Meeting notes mentioned **removing** categories (e.g. Generic, Information, Methods), **renaming** “Time” → “Date & Time”, editing glossary “Purpose” headings, etc. Those actions change **canonical strings** and require:

- Updating `taxonomy.json`, `Categories Explained.html`, ground truth, LLM prompts/outputs, compare logic, and historical JSON; **or**
- Adding an explicit **legacy → new label** map in code and re-exporting data.

Until that project exists, treat those items as **backlog / data redesign**, not as part of UI-only renaming. See [UI_SCOPE_AND_ROADMAP.md](UI_SCOPE_AND_ROADMAP.md) § Deferred.

---

## Related docs

- [FRAMEWORK.md](FRAMEWORK.md) — pipeline data shapes  
- [UI_SCOPE_AND_ROADMAP.md](UI_SCOPE_AND_ROADMAP.md) — full UX backlog and decisions  
- [INSTRUCTIONS_AGENT_ASSESSMENT.md](INSTRUCTIONS_AGENT_ASSESSMENT.md) — assessment labels must match taxonomy for scoring  
