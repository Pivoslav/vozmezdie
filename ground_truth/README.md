# Ground truth module

**Contract (see [FRAMEWORK.md](../docs/agents/FRAMEWORK.md)):**

- **Input**: Config (path(s) or pattern for CSVs); document_id → file mapping if needed.
- **Output**: Per document_id, list of extraction rows in the same shape as LLM output.

Slots: CSV today; could be JSON, DB, or API. Contract = map document_id → list of rows.
