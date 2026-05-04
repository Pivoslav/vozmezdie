# Statistics to Collect (Brainstorm)

This document lists statistics we can collect from the comparison pipeline. Accuracy stats are now stored hidden in the report; below are additional metrics to consider.

## Currently Stored (Hidden)

- `category_accuracy_pct` – % of aligned rows where LLM category matches human
- `framing_accuracy_pct` – % of aligned rows where LLM framing matches human
- `both_match_pct` – % where both category and framing match
- `n_human`, `n_llm`, `n_matched` – counts per document

## Proportional / Distribution Statistics

### Whole Dataset

- **Segments by content category** – count (and %) of segments per category (LLM labels, human labels, or both)
- **Segments by framing strategy** – count (and %) per framing
- **Category × framing cross-tab** – heatmap or table of co-occurrence
- **Documents count** – total number of documents
- **Total segments** – sum of aligned rows across all documents

### Per Document

- **Segment count** – number of aligned rows
- **Category distribution** – bar chart or table of categories in this doc
- **Framing distribution** – same for framing
- **Mismatch breakdown** – how many category-only vs framing-only vs both mismatch

## Potential Future Statistics

- **Agreement by category** – which categories does the LLM get right most/least often?
- **Agreement by framing** – same for framing strategies
- **Segment length vs accuracy** – does longer text correlate with better/worse matching?
- **First vs last segments** – does position in document affect accuracy?
- **Vocabulary diversity** – unique terms per document, type-token ratio
- **Temporal trends** – if documents have dates, accuracy over time

## Data Availability

- `comparison_by_doc[doc_id]["aligned_rows"]` – each row has: `section`, `entry_eng`, `entry_rus`, `llm_category`, `human_category`, `llm_framing`, `human_framing`, `category_match`, `framing_match`, `context`
- `documents` – list of `{ document_id, display_name, raw_text_en?, raw_text? }`
