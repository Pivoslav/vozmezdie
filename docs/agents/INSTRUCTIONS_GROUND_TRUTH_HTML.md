# Instructions: Ground truth from HTML + updated categories

**For the next agent.** The human-coded values that used to be in CSV files are now in **HTML files**. The category/framing definitions are in **Categories Explained.html**. This doc tells you where things are and how to implement loading them in the framework **without** loading huge HTML files into memory at once (to avoid crashes).

---

## 1. Where the files live (vozmezdie repo)

- **Ground truth HTML (one file per document):**  
  `vozmezdie/converted_files/full_html/`  
  Examples: `1127.html`, `1128.html`, `1208.html`, `1209.html`, `1213.html`, `1215.html`, `1230.html`, `1245.html`, `1247.html`, `1249-0046-0047.html`, `1249-80-83.html`, `1256.html`, `1262 149-150.html`, `1262 198-200.html`, `1262 28-32.html`.  
  **Note:** These files are very large (e.g. 1128.html is ~900K+ characters). Do **not** read them with `read_file` in one go. Use streaming, or parse with a library that can handle large HTML (e.g. `lxml` with iterparse, or `bs4` on chunks), or run a small script that extracts only the table and writes a minimal JSON/CSV for the framework to use.

- **Updated categories (content + framing):**  
  `vozmezdie/Categories Explained.html`  
  This file is smaller. It contains:
  - **Framing and Language Strategy Categories** (table rows 3–7): Action-Focused Language; Ideological Framing (Discrediting); Ideological Phrasing (Normalizing); Institutional / Bureaucratic Lingo; Generic / Neutral Language. Columns: Category, Function, Typical Use / Examples.
  - **12-Category System** (content categories): 1. Actors, 2. Places, 3. Actions, 4. Events, 5. Time, 6. Methods, 7. Legal Framework, 8. Documents, 9. Information, 10. Material Resources, 11. Status and Condition, 12. Context and Concepts. Each has a short “Function” and examples in the same table layout (Google Sheets export: `.ritz .waffle` table, `<td class="s...">` cells).

---

## 2. What the framework expects (contract)

- **Ground truth:** `ground_truth.run(config, document_ids)` must return `Dict[document_id, List[dict]]`, where each dict has: `section`, `entry_eng`, `entry_rus`, `content_category`, `framing`, `context`. Same shape as LLM extraction rows (see [FRAMEWORK.md](FRAMEWORK.md)).
- **Taxonomy:** `config/taxonomy.json` (or loaded from elsewhere) with `content_categories` and `framing_strategies`. Each entry has at least `id`, and optionally `label_en`, `label_uk`, `colour`, `description`, `examples`.

---

## 3. How to implement (recommended order)

### Step A: Inspect one ground-truth HTML file safely

- **Do not** open the full 1128.html in one read. Instead:
  1. Use a **small script** (e.g. Python in the repo) that:
     - Opens `vozmezdie/converted_files/full_html/1128.html` with a parser that can stream or parse in chunks (e.g. `lxml.etree.iterparse` or `BeautifulSoup` with a file handle and a max read if needed).
     - Finds the **table** (e.g. `<table class="waffle">` in the Sheets export).
     - Identifies the **header row** (first `<tr>` in `<thead>` or first data row) and which column index is “Entry (ENG)”, “Entry (RUS)”, “Content Category”, “Framing”, “Context” (or the exact headers used in the sheet).
     - Prints or logs the header names and the first 2–3 data rows (cell text only). Run the script and note the column order and any extra columns.
  2. If the table is too large to parse in one go, use **iterparse** (lxml) or **row-by-row** parsing and write rows to an intermediate JSON/CSV; then the framework’s ground_truth module can read that instead of the raw HTML.

### Step B: Add an HTML ground-truth loader

- In **`vozmezdie_framework/ground_truth/`** (or in the main vozmezdie repo and call it from the framework):
  1. Add a function or module that:
     - Takes a **path to one HTML file** (e.g. `converted_files/full_html/1128.html`).
     - Parses the table as in Step A (streaming/chunked if needed), maps columns to `entry_eng`, `entry_rus`, `content_category`, `framing`, `context`, and `section` (or derive section from row index).
     - Returns `List[dict]` in the contract shape.
  2. In `ground_truth/__init__.py`, add config support for **HTML** as well as CSV, e.g.:
     - `ground_truth.html_dir` or `ground_truth.path` pointing to `converted_files/full_html` (or a configurable path).
     - Mapping from **document_id** to **filename**: e.g. document_id `1128` → `1128.html`; document_id `1262 28-32` might map to `1262 28-32.html`. Handle spaces and dashes consistently (list the filenames and document_ids from ingest and define the mapping or a naming convention).
  3. If the path is outside the framework repo (e.g. in vozmezdie), make the path **configurable** in `config/pipeline_config.example.json` (e.g. `ground_truth.html_dir`: `../vozmezdie/converted_files/full_html` or an absolute path) so the framework stays portable.
  4. Keep the existing CSV loader and fixture fallback; when `ground_truth.html_dir` is set and the file for a document_id exists, use the HTML loader; otherwise fall back to CSV or fixture.

### Step C: Update taxonomy from Categories Explained.html

- **Parse** `vozmezdie/Categories Explained.html` (this file is small enough to read).
- Extract:
  - **Framing strategies:** The first table (Framing and Language Strategy Categories). Rows 3–7: Category name (column A), Function (B), Typical Use / Examples (C). Build `framing_strategies` with e.g. `id` = category name, `description` = Function, `examples` = Typical Use.
  - **Content categories:** The “12-Category System” section. Rows 11–82 roughly: bold category names (e.g. “1. Actors”, “2. Places”) and under each the “Function” and example lines. Build `content_categories` with `id` (e.g. “Actors”, “Places”), optional `description`, optional `examples`.
- **Output:** Either (1) update `vozmezdie_framework/config/taxonomy.json` with the parsed content so the framework uses it by default, or (2) add a script that writes `taxonomy.json` from Categories Explained.html and run it when the categories change, or (3) load taxonomy from the HTML path in config (e.g. `taxonomy.from_html`: `../vozmezdie/Categories Explained.html`) and parse on startup. Prefer (1) or (2) so the pipeline stays fast and the contract (taxonomy as JSON-like structure) is unchanged.
- Ensure **report** and **compare** still see the same taxonomy shape: `content_categories` and `framing_strategies` as lists of dicts with at least `id` and optional labels/colours.

### Step D: Config and paths

- In `config/pipeline_config.example.json` (or a copy the user can point to):
  - Add `ground_truth.html_dir` (path to `converted_files/full_html`), and optionally `ground_truth.document_id_to_filename` or a short note that document_id is derived from filename without extension.
  - If taxonomy is loaded from HTML, add `taxonomy.from_html` or similar; otherwise leave `taxonomy` pointing at `config/taxonomy.json` and update that file from Categories Explained (Step C).
- Document in README or NEXT_STEPS that ground truth can come from HTML and that the updated categories are in Categories Explained.html.

### Step E: Tests

- Add a **small fixture HTML** (e.g. a few rows in the same table structure as the real sheets) in `vozmezdie_framework/tests/fixtures/` or similar. Write a test that loads ground truth from that fixture HTML and asserts the returned list has the contract shape and expected content. This avoids parsing the 900K+ file in tests.
- Optionally: test that when `ground_truth.html_dir` is set and a real file exists, the loader returns at least one row (if the test environment has access to that path).

---

## 4. Summary checklist for the agent

- [ ] Do **not** read full 1128.html (or other large HTML) in one go; use streaming/chunked parsing or a small script to dump table structure and sample rows.
- [ ] Implement HTML ground-truth loader: one HTML file → list of rows in contract shape; map document_id to filename; add config for `ground_truth.html_dir`.
- [ ] Parse **Categories Explained.html** into content categories and framing strategies; update `config/taxonomy.json` (or equivalent) and keep report/compare contract unchanged.
- [ ] Keep CSV and fixture fallback in `ground_truth.run()`.
- [ ] Add a test that uses a small HTML fixture with the same table structure.
- [ ] Document config and path assumptions in README or NEXT_STEPS.

Once this is done, the pipeline can use the new HTML ground truth and updated categories without changing the compare or report module contracts.
