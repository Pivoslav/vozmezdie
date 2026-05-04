# Compare / accuracy module

**Contract (see [FRAMEWORK.md](../docs/agents/FRAMEWORK.md)):**

- **Input**: Per document: list of LLM rows, list of ground truth rows; optional matching strategy.
- **Output**: Per document: aligned rows (with category_match, framing_match, both_match) + category_accuracy_pct, framing_accuracy_pct, both_match_pct.

Slots: Matching logic can change (by index, by phrase, fuzzy) as long as output shape is preserved.
