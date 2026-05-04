# LLM extraction module

**Contract (see [FRAMEWORK.md](../docs/agents/FRAMEWORK.md)):**

- **Input**: Per-doc text (or path), taxonomy (categories + framing), config (model, prompt, with/without context).
- **Output**: Per document_id, list of extraction rows: section, entry_eng, entry_rus, content_category, framing, context.

Slots: Ollama, another API, or a mock returning fixture JSON. Same output shape.
