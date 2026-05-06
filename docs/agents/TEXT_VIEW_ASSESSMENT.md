# Document text view: how it works and framing colour fix

## How it currently works

### 1. Two ways the text panels get content

**Path A – Server-filled (when raw document text exists)**  
- For each doc the server has `full_text_eng` and `full_text_rus` (from ingest) and `aligned` (comparison rows).  
- It runs overlap resolution **per language** via `_get_accepted_segments(full_text, aligned, entry_key)` for English and for Russian. Each returns a list of (position, length, segment, row, row_index).  
- English and Russian panels are built independently from those matches. A span may correspond to an aligned row whose **other-language** snippet did not match in the opposite full text (different substring occurrence counts, OCR, etc.). Those spans still render like other segments but carry `data-has-partner="false"` for internal consistency only — **no dashed underline, tooltip, or user-facing copy** about “missing” pairs (to avoid implying translation tricks).  
- When both snippets for the same row match in their respective full texts, spans get `data-has-partner="true"`. Category/framing metadata still comes from the same aligned row, so highlighting stays aligned wherever both sides resolved to that row.  
- **Important:** `data-framing` and `data-category` are taken from **`llm_framing` and `llm_category`** (our/agent assessment), not from Human/GT.  
- The returned HTML is written into `<div id="doc-text-eng-{doc_id}">` and `<div id="doc-text-rus-{doc_id}">`.  
- So when you have raw text, the spans in the panels are **LLM-labelled**; partner flags are present in the DOM only for tooling, not advertised in the UI.

**Path B – Table-built (when panels are empty)**  
- On load, the script checks `hasPreFilled = (containerEng.children.length > 0)`.  
- If the panels are empty (e.g. no raw text, or no segments were found in the full text), it **builds** the panels from the **comparison table**: for each row it reads the **second span** (Human column) in the category and framing cells, creates new spans with that text, and sets `data-framing` / `data-category` from that Human value.  
- So when the panels are table-built, the spans are **Human/GT-labelled**.

### 2. How the dropdowns are populated

- **Always from the table:** After the `hasPreFilled` branch, a loop runs over **table rows** and collects category/framing strings from the **second span (Human)** in each cell into `categories` and `framings`. The framing and category dropdowns are then filled from these sets.  
- So the **dropdown options are always the set of Human/GT values** that appear in the table, and are **not** derived from the span content in the text panels.

### 3. How filtering and colour are applied

- `applyDocumentSearchAndFilter(tid)` runs on load and on every change to search or the dropdowns.  
- It loops over **English** `.doc-entry` spans and, for each span, reads that span’s own `data-category`, `data-framing`, and colour attributes; it then sets **that span’s** background (category highlight), colour (framing), dimmed, and search-highlight. It then does a **separate loop** over **Russian** spans and applies the same logic using each Russian span’s own attributes. So English and Russian are not paired by index; each span is styled from its own data.  
- **Framing (text colour):** `framingMatch(spanFram, framFilter)` is used so labels like "Generic / Neutral" and "Generic / Neutral Language" match. `useFramColour` and `framCol` are derived from that span’s `data-framing` and `data-framing-colour` (via `resolveFramingColour`).  
- **Category (highlight/background):** `categoryMatch(spanCat, catFilter)` is used so category filter and highlight use the same logic (trim + case-insensitive). Each span’s `data-category` and `data-category-colour` drive that span’s background and visibility. So category highlighting is consistent between English and Russian in the same way as framing.

### 4. Why Action-Focused doesn’t colour in the text panels

- When the panels are **server-filled**, each span’s `data-framing` is **LLM** (e.g. "Action-Focused Language" where we assigned it).  
- The framing dropdown is filled from the **table’s Human column** only. So the dropdown only contains framings that appear as **Human** in at least one row.  
- If in this document no row has Human = "Action-Focused Language" (e.g. GT always has "Generic / Neutral" or something else), then **"Action-Focused Language" never appears in the dropdown**. The user cannot select it, so the code never runs with `framFilter === 'Action-Focused Language'` and never applies the red colour to those spans.  
- So the failure is **not** in the colour resolution or in the style application; it’s that **the dropdown is populated from the table (Human) while the spans are labelled from LLM**. When LLM uses a value that never appears in the Human column, that value never becomes a dropdown option and can never be selected to trigger colouring.

---

## Fix

**Populate the framing (and category) dropdown from the actual span content when the panels are server-filled.**

- In `buildDocumentTextView`, when `hasPreFilled` is true, **do not** populate `categories` and `framings` from the table.  
- Instead, iterate `containerEng.querySelectorAll('.doc-entry')` and for each span read `getAttribute('data-category')` and `getAttribute('data-framing')`. Collect the unique values and use **these** to build the category and framing dropdown options.  
- When `hasPreFilled` is false (table-built panels), keep the current behaviour: populate the dropdowns from the table (second span per row).  

Result:

- For server-filled panels, the dropdown options exactly match the values that exist on the spans (LLM labels). So "Action-Focused Language" will appear in the dropdown if any span has that framing, and selecting it will set `useFramColour` and apply the correct colour.  
- For table-built panels, behaviour is unchanged: dropdown and spans both come from the Human column, so they already match.

---

## Why "Action-Focused Language" still doesn't colour (simple explanation)

**The table and the text panels are built differently.**

- **Table:** Shows every row. Each row has an English phrase, a Russian phrase, and LLM/Human labels (e.g. "Action-Focused Language"). So you see the option and the row.
- **Text panels:** The server builds them by taking the **raw document text** (e.g. the full English file) and, for each row, doing an **exact string search**: "Does this row's phrase appear in the document?" Only when the phrase is **found** does it wrap it in a span and give it the row's framing. If the phrase is not found, that row gets **no span at all**.

So if the phrases you labelled "Action-Focused Language" (e.g. "D. Hanusiak held a press conference", "Desertion with Weapons") **don't appear in the raw document text**—because of different punctuation, line breaks, spacing, or because the table text came from a different source—then **no span is ever created** with that framing. The dropdown shows "Action-Focused Language" (we added it from the table), but there is literally **no span in the panel** that has that framing, so there is nothing to colour. The colour logic is fine; the segments that should be red were never turned into spans because the exact string wasn't found in the document.

**Fix:** Make the search more tolerant (e.g. normalize whitespace so "word1  word2" and "word1\nword2" both match). Then more rows get spans, and "Action-Focused Language" will colour wherever those segments appear.

---

## Why Action-Focused can still show as Generic (substring order)

If a segment you labelled "Action-Focused" (e.g. "arrived") appears **inside** a longer segment that has "Generic / Neutral Language" (e.g. "delegation arrived"), the order of matching matters. We walk the aligned rows in order and do one `find(segment, pos)` per row. Whichever segment we match **first** at that place in the document gets the span. So if "delegation arrived" is matched first, we output one span for the whole phrase with Generic. Then we search for "arrived" from a position **after** that span, so we never see the "arrived" inside it. So that occurrence of "arrived" never gets its own span and stays part of the Generic span—so it looks grey.

**Fix:** When building spans, process segments so that **shorter segments are considered before longer ones** at the same location. Then we emit "delegation " as plain text, then a span for "arrived" with Action-Focused, and we skip the full "delegation arrived" span where it would overlap. So the short segment gets the correct colour.
