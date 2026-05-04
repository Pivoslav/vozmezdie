# Instructions for Synonym Agent

**Task:** For each term extracted from Vozmezdie archival documents, produce **1 to 5 synonyms** in English and 1 to 5 synonyms in Russian. The results will feed the glossary and "click word for definition" (which will show synonyms instead of definitions).

**Alternative workflow:** For chunk-by-chunk processing via an LLM chat agent (with definitions and synonyms), see [INSTRUCTIONS_SYNONYM_CHAT_AGENT.md](INSTRUCTIONS_SYNONYM_CHAT_AGENT.md).

---

## 1. Input

Run this script to generate the input file:

```
python scripts/export_terms_for_synonyms.py
```

This reads `data/output/comparison_results.json` and writes `data/output/terms_for_synonyms.json`.

The input file has this structure:

```json
{
  "terms": [
    {
      "entry_eng": "authorized personnel",
      "entry_rus": "уполномоченный персонал",
      "category": "Actors",
      "framing": "Institutional / Bureaucratic Lingo"
    },
    ...
  ],
  "source": "...",
  "count": 123
}
```

Each term has:
- `entry_eng` — English segment text
- `entry_rus` — Russian segment text (original)
- `category` — Content category (Actions, Actors, Places, Time, etc.)
- `framing` — Framing strategy (Generic, Institutional, Ideological, Action-Focused)

---

## 2. Task

For each term in `terms`:

1. **Synonym quality**
   - Synonyms should be **close substitutes** for the term in the same language
   - Fit the **bureaucratic / institutional / Cold War** register where appropriate
   - Prefer formal, period-appropriate language over colloquial
   - Synonyms need not be single words; short phrases are fine (e.g. "authorized personnel" → "cleared staff", "accredited representatives")

2. **Quantity**
   - **Minimum 1** synonym per language
   - **Maximum 5** synonyms per language
   - Provide `synonyms_eng` for the English term and `synonyms_rus` for the Russian term

3. **Optional use of context**
   - `category` and `framing` can help guide register and domain (e.g. "Actors" + "Ideological" may suggest discrediting or normalizing language)
   - Use them to improve synonym relevance; do not force every synonym to fit the category

---

## 3. Output Format

Produce a JSON file with this exact structure:

```json
{
  "term_synonyms": [
    {
      "entry_eng": "authorized personnel",
      "entry_rus": "уполномоченный персонал",
      "synonyms_eng": ["cleared staff", "accredited personnel", "authorized staff"],
      "synonyms_rus": ["уполномоченные сотрудники", "аккредитованный персонал", "служебный персонал"]
    },
    ...
  ]
}
```

**Rules:**
- Preserve `entry_eng` and `entry_rus` exactly as in the input (for matching)
- `synonyms_eng`: array of 1–5 strings, English synonyms
- `synonyms_rus`: array of 1–5 strings, Russian synonyms
- Order of terms can match input or be alphabetical; matching is by (entry_eng, entry_rus)
- If you cannot supply synonyms for a term (e.g. proper noun, unclear), use empty arrays `[]` and add a note in `notes` if desired (see below)

**Optional per-term field:**
- `notes`: string with any caveat (e.g. "Proper name; limited synonymy")

---

## 4. Where to Save

Save the output as:

```
config/term_synonyms.json
```

or

```
data/output/term_synonyms.json
```

The report will be configured to load from one of these paths. Prefer `config/` if you want it versioned with the project.

---

## 5. Example Entry

Input:
```json
{
  "entry_eng": "counterintelligence measures",
  "entry_rus": "контрразведывательные меры",
  "category": "Actions",
  "framing": "Institutional / Bureaucratic Lingo"
}
```

Output:
```json
{
  "entry_eng": "counterintelligence measures",
  "entry_rus": "контрразведывательные меры",
  "synonyms_eng": ["counterespionage measures", "security measures", "intelligence countermeasures", "counterintelligence operations"],
  "synonyms_rus": ["меры контрразведки", "контрразведывательные операции", "меры по борьбе с разведкой", "оперативные мероприятия контрразведки"]
}
```

---

## 6. Checklist for Synonym Agent

- [ ] Read `data/output/terms_for_synonyms.json`
- [ ] For each term, produce 1–5 synonyms in English and 1–5 in Russian
- [ ] Match formal/bureaucratic register where appropriate
- [ ] Output valid JSON with `term_synonyms` array
- [ ] Save to `config/term_synonyms.json` (or `data/output/term_synonyms.json`)
- [ ] Return the file path to the user so they can integrate it

---

## 7. Integration (for later)

After you have `term_synonyms.json`, the report module will:

1. Load it at report generation time
2. Add synonym data to glossary term items
3. Add `data-synonyms-eng` and `data-synonyms-rus` (or similar) to document text spans
4. Implement click handler to show a tooltip with synonyms when a segment is clicked
