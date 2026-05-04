# Report module

**Contract (see [FRAMEWORK.md](../docs/agents/FRAMEWORK.md)):**

- **Input**: Per-doc results (aligned rows + stats), document list, taxonomy + glossary, i18n strings.
- **Output**: Report artifact(s) (e.g. single HTML) at given path.

Features (from manual_analysis_report): tabs per doc + Glossary; stats; comparison table; document text view (search, filter by category/framing, colour); EN/UK. Glossary definitions and examples come from `Categories Explained.html` when `config.taxonomy.source_html` is set; terms from documents grouped by category/framing.

Slots: Different HTML template or format; contract = receives report input, writes output.
