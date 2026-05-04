# Ingest module

**Contract (see [FRAMEWORK.md](../docs/agents/FRAMEWORK.md)):**

- **Input**: Config (paths, extensions, encoding).
- **Output**: List of `{ document_id, display_name?, path }` and optionally raw text per doc.

Implementations can read from a directory, a manifest file, or an adapter (URL, DB). Same output shape.
