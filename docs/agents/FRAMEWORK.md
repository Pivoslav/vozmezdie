# Vozmezdie modular framework

A pipeline for **expert-grounded LLM evaluation on archival documents**: documents in → LLM extraction (with optional context) → comparison to human labels → metrics and interactive report.

This doc plots the pipeline and module boundaries so pieces can be run, tested, or swapped independently.

**User-visible wording vs stored labels:** The report may use umbrella terms such as “Specific Details” and “Ideological Layers” in copy while JSON rows keep canonical taxonomy strings (`human_category`, `llm_category`, etc.). See [UI_LABEL_MAP.md](UI_LABEL_MAP.md).

---

## 1. Pipeline overview

```
[Documents]     [Taxonomy]      [Config]
     │                │              │
     ▼                ▼              ▼
┌─────────────────────────────────────────┐
│  INGEST                                  │  → document list, raw text per doc
└─────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│  LLM EXTRACTION                          │  → per-doc: phrases + category + framing (raw/structured)
│  (optional: with-context / few-shot)     │
└─────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│  GROUND TRUTH LOAD                       │  → per-doc: human-coded rows (same shape as LLM output)
└─────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│  COMPARE / ACCURACY                      │  → per-doc: match flags, category/framing/both accuracy %
└─────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│  REPORT                                  │  → HTML (tabs, table, document text view, glossary, i18n)
└─────────────────────────────────────────┘
```

Each box is a **module**: clear inputs and outputs. You can replace “LLM EXTRACTION” with another backend, or “REPORT” with a different template, without changing the rest.

---

## 2. Data shapes (what flows between stages)

### 2.1 Document identity and text

- **Document id**: stable id derived from filename or config (e.g. `1127`, `1208`, `1230`).
- **Per document**: `{ document_id, source_path?, raw_text_eng?, raw_text_rus? }`.
- Ingest output: list of such objects (and/or paths the next stage can read).

### 2.2 Taxonomy (categories + framing)

- **Content categories**: fixed list with display name (EN/UK), optional colour, definition (for glossary).
- **Framing strategies**: same.
- Used by: prompts (LLM), ground truth parsing, report (columns, filters, glossary, document text view colours).

### 2.3 Extraction row (one phrase/entity per row)

Same shape for **LLM output** and **ground truth** so comparison is row-aligned or match-based:

| Field           | Description                          |
|----------------|--------------------------------------|
| section        | Optional section/chunk index         |
| entry_eng      | Phrase in English                    |
| entry_rus      | Phrase in Russian (optional)        |
| content_category | One of the taxonomy categories     |
| framing        | One of the framing strategies        |
| context        | Optional surrounding context line    |

- **LLM extraction** output: list of such rows per document (possibly with parsing/normalization so category/framing match taxonomy labels).
- **Ground truth**: same structure (e.g. from CSV with columns aligned to these names).

### 2.4 Comparison result (per document)

- **Inputs**: list of LLM rows, list of ground truth rows (and optionally a matching strategy: by order, by phrase text, or by alignment).
- **Outputs**:
  - **Aligned rows**: each row has LLM category, LLM framing, human category, human framing, match flags (category_match, framing_match, both_match).
  - **Summary metrics**: e.g. category_accuracy_pct, framing_accuracy_pct, both_match_pct.

### 2.5 Report input (aggregate)

- **Per document**: document_id, display_name, stats (category/framing/both %), aligned rows (for table + document text view).
- **Glossary**: categories and framing terms with definitions (and EN/UK strings).
- **i18n**: map of string key → { en, uk } (or similar) for UI.

---

## 3. Module contracts

### 3.1 Ingest

- **Input**: config (paths for documents, allowed extensions, encoding).
- **Output**: List of `{ document_id, display_name?, path }` and optionally raw text per doc (or path that “LLM” and “Report” can read).
- **Slots**: Can add a “load from URL” or “from database” adapter; contract is the same list + text/path.

### 3.2 LLM extraction

- **Input**: Per-doc text (or path), taxonomy (categories + framing), config (model, temperature, prompt variant, with/without context examples).
- **Output**: Per document_id, list of extraction rows (section, entry_eng, entry_rus, content_category, framing, context).
- **Slots**: Ollama, another API, or a mock that returns fixture JSON. Same output shape.

### 3.3 Ground truth load

- **Input**: Config path(s) or directory for CSVs (or other format); document_id → file mapping if needed.
- **Output**: Per document_id, list of extraction rows in the same shape as LLM output (same column names / normalizations).
- **Slots**: CSV today; could be JSON, DB, or API. Contract = map document_id → list of rows.

### 3.4 Compare / accuracy

- **Input**: Per document: list of LLM rows, list of ground truth rows; optional matching strategy (by index, by entry_eng, etc.).
- **Output**: Per document: aligned rows (with match flags) + summary metrics (category_accuracy_pct, framing_accuracy_pct, both_match_pct).
- **Slots**: Matching logic can change (fuzzy phrase match, alignment) as long as it produces aligned rows + three percentages.

### 3.5 Report

- **Input**: Per-doc results (aligned rows + stats), document list (ids + display names), taxonomy + glossary text, i18n strings.
- **Output**: Single HTML file (or multiple; contract = “report artifact(s) at given path”).
- **Report features** (from manual_analysis_report):
  - Master header + language switcher (EN/UK).
  - One tab per document + one Glossary tab.
  - Per-doc tab: stats cards (category %, framing %, both %); document text view (phrases in order, search, filter by category/framing, colour by category or framing); comparison table (Section, Entry ENG, Entry RUS, Content Category [LLM vs Human], Framing [LLM vs Human], Context).
  - Glossary tab: content categories and framing strategies with definitions/examples; optional search/filter; EN/UK.
- **Slots**: Different HTML template or a different format (e.g. JSON + separate viewer). Contract = “receives report input, writes output”.

---

## 4. Where to put code (suggested layout)

```
vozmezdie_framework/
├── docs/agents/                 # Agent guides (this file, etc.)
├── config/                      # Shared config schemas / defaults
│   └── (paths, model, taxonomy refs)
├── ingest/                      # Module: document discovery + optional load
├── llm/                         # Module: call LLM, parse to extraction rows
├── ground_truth/                # Module: load GT per document
├── compare/                     # Module: align rows + compute accuracy
├── report/                      # Module: build HTML from report input
├── data/                        # Default dirs (optional)
│   ├── input/
│   └── output/
└── run.py                       # Thin orchestrator: config → ingest → llm → gt → compare → report
```

Each module can have its own tests and its own “runner” script that reads fixture inputs and writes fixture outputs, so you can develop “compare” without running the LLM, or “report” from a saved JSON of comparison results.

---

## 5. What we had in the manual analysis report (reference)

- **Tabs**: One per document (by filename) + Glossary.
- **Table columns**: Section, Entry (ENG), Entry (RUS), Content Category (My Assessment vs Human), Framing (My Assessment vs Human), Context.
- **Match/mismatch**: Green (match) / red (mismatch) for category and framing cells.
- **Document text view**: Phrases from table rows, in order, as spans; search box; dropdowns for category and framing; colour mode (default vs by category/framing); built client-side from the table body.
- **Glossary**: Content categories and framing strategies with purpose + examples; EN/UK; expand/collapse; filter.
- **i18n**: `data-translate` keys and a small JS dictionary for EN/UK for header, labels, glossary titles, etc.

Keeping these in mind, the **report** module’s input should be enough to generate that HTML (and the JS that builds the document text view from the table). The rest of the pipeline stays agnostic of “how” the report is rendered.

---

## 6. Status and next steps

**Done:**

- **Config**: `config/pipeline_config.example.json` (with `use_fixture: true` by default), `config/taxonomy.json`.
- **Modules**: Ingest, LLM (stub + optional Ollama adapter), ground_truth, compare, report — all implemented to the contracts. Fixtures when paths are missing.
- **Pipeline**: `run.py` runs config → ingest → llm → ground_truth → compare → save JSON → report. Writes `data/output/manual_analysis_report.html` and `data/output/comparison_results.json`.
- **Report**: Tabs per doc, stats, comparison table, document text view (search, category/framing filter, colour mode), glossary tab. JS builds text view from table.
- **Report-only**: `run_report_only.py [path/to/comparison_results.json]` regenerates HTML from saved results.
- **LLM**: Stub by default. Set `llm.use_fixture: false` and ensure Ollama is running to use `llm/ollama_adapter.py`.
- **Tests**: compare, ingest, ground_truth, report, pipeline smoke (`test_run`, `test_pipeline`). Run: `pytest tests/ -v`.
- **CLI**: `run.py --use-ollama`, `run.py --report-only`.

**Optional next:** Point config at real docs/CSVs; refine Ollama prompt/parse; expand glossary and EN/UK i18n.
