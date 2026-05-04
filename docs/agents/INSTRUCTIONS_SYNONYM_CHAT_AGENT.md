# Chunked Chat-Agent Workflow for Synonyms and Definitions

**Purpose:** Process archival terms in small chunks via an LLM chat agent. For each term, the agent produces a formatted data structure, definitions (EN/RU), and synonyms (EN/RU). This mirrors the framing-assessment workflow (chunk by chunk, expert-grounded output) but is suitable for automation via API or chat.

---

## 1. Why Chunked?

- **Context limits:** A full `terms_for_synonyms.json` can have hundreds of terms. Chunking keeps each request within token limits.
- **Quality:** Smaller batches let the model focus; fewer hallucinations and alignment drift.
- **Incremental:** Process a few chunks per session; merge results later.
- **Auditable:** Each chunk is a separate file; easy to re-run or fix a single chunk.

---

## 2. Workflow Overview

```
terms_for_synonyms.json  →  split into chunks  →  chat agent processes each chunk  →  merge into term_synonyms.json
```

1. **Export terms:** `python scripts/export_terms_for_synonyms.py`
2. **Split into chunks:** Run a script (or manually) to write `data/output/synonym_chunks/chunk_001.json`, `chunk_002.json`, …
3. **For each chunk:** Send the chunk + prompt to your LLM (Claude, GPT, etc.). Paste or save the raw JSON output.
4. **Merge:** Combine all chunk outputs into `config/term_synonyms.json` (or extended format with definitions).

---

## 3. Copy-Paste Prompt (Ready to Use)

1. Run `python scripts/build_ready_to_send.py 1` (or `2`, `3`, … for other chunks).
2. Open `data/output/synonym_chunks/ready_to_send_chunk_001.txt`.
3. Copy the entire file (Ctrl+A, Ctrl+C).
4. Paste into your LLM. Send.
5. Save the raw JSON response to `data/output/synonym_chunks_output/chunk_001_out.json`.

The prompt is designed to prevent meta-responses: it explicitly forbids questions, commentary, or "What would you like me to focus on?"-style replies. The LLM must output ONLY the JSON object.

```
TASK: Process the JSON below. For each term in the "terms" array, produce definition_eng, definition_rus, synonyms_eng (1–5 items), synonyms_rus (1–5 items). Preserve entry_eng and entry_rus exactly.

REQUIREMENTS:
- Formal, bureaucratic, Cold War archival register; period-appropriate (late Soviet era)
- Proper nouns/titles/statistics: synonyms_eng=[], synonyms_rus=[], definition_eng="Proper name; no definition"
- Use category and framing to guide register
- Output structure: {"term_results":[{"entry_eng":"","entry_rus":"","definition_eng":"","definition_rus":"","synonyms_eng":[],"synonyms_rus":[]}]}

CRITICAL: Your response must be ONLY the JSON object. No questions. No commentary. No "I see...", "What would you like...", or options. Start with { and end with }. Nothing before or after.

INPUT JSON:
[chunk JSON follows]
```

---

## 4. Chunk Format

- **Recommended chunk size:** 15–25 terms per chunk.
- **Input per chunk:** JSON array of terms, each with `entry_eng`, `entry_rus`, `category`, `framing`.

Example `chunk_001.json`:
```json
{
  "chunk_id": 1,
  "terms": [
    {
      "entry_eng": "authorized personnel",
      "entry_rus": "уполномоченный персонал",
      "category": "Actors",
      "framing": "Institutional / Bureaucratic Lingo"
    },
    {
      "entry_eng": "counterintelligence measures",
      "entry_rus": "контрразведывательные меры",
      "category": "Actions",
      "framing": "Institutional / Bureaucratic Lingo"
    }
  ]
}
```

---

## 5. Prompt Design (Detailed)

### System prompt

```
You are an expert linguist and historian specializing in Cold War Soviet and Western archival documents. Your task is to analyze terms extracted from declassified KGB and intelligence documents and produce:

1. **Definitions** — A brief, precise definition in English and Russian that reflects how the term is used in bureaucratic, institutional, and ideological contexts of the period.
2. **Synonyms** — 1–5 close substitutes per language. Synonyms must:
   - Fit the formal, bureaucratic, Cold War archival register
   - Be period-appropriate (late Soviet / early post-Soviet era)
   - Work as substitutes in the same document context
   - Prefer institutional and formal language over colloquial

You will receive a JSON array of terms. Each term has:
- entry_eng: English segment text
- entry_rus: Russian segment text (original)
- category: Content category (Actions, Actors, Places, Time, Documents, Context and Concepts, Legal Framework)
- framing: Framing strategy (Generic / Neutral Language, Institutional / Bureaucratic Lingo, Ideological Framing (Discrediting), Ideological Phrasing (Normalizing), Action-Focused Language)

Use category and framing to guide register and domain. For example:
- Institutional / Bureaucratic Lingo → formal, bureaucratic synonyms
- Ideological Framing (Discrediting) → language that carries negative connotation
- Actors + Institutional → terms for personnel, officials, bodies

Output ONLY valid JSON. No preamble, no markdown fences. Preserve entry_eng and entry_rus exactly for matching.
```

### User prompt template

```
Process the following terms. For each term, produce:
- definition_eng: one sentence definition in English (as used in this archival context)
- definition_rus: one sentence definition in Russian
- synonyms_eng: array of 1–5 English synonyms (formal, period-appropriate)
- synonyms_rus: array of 1–5 Russian synonyms

If a term is a proper noun, document title, statistic, or fragment that cannot be sensibly defined, use empty arrays for synonyms and a brief note in definition_eng (e.g. "Proper name; no definition").

Output a JSON object with this exact structure:
{
  "term_results": [
    {
      "entry_eng": "<exact copy>",
      "entry_rus": "<exact copy>",
      "definition_eng": "...",
      "definition_rus": "...",
      "synonyms_eng": ["...", "..."],
      "synonyms_rus": ["...", "..."]
    }
  ]
}

Terms to process:
{{CHUNK_JSON}}
```

---

## 6. Output Format

### Minimal (synonyms only, for current report)

```json
{
  "term_synonyms": [
    {
      "entry_eng": "authorized personnel",
      "entry_rus": "уполномоченный персонал",
      "synonyms_eng": ["cleared staff", "accredited personnel", "authorized staff"],
      "synonyms_rus": ["уполномоченные сотрудники", "аккредитованный персонал", "служебный персонал"]
    }
  ]
}
```

### Extended (with definitions, for future "click for definition")

```json
{
  "term_results": [
    {
      "entry_eng": "authorized personnel",
      "entry_rus": "уполномоченный персонал",
      "definition_eng": "Personnel cleared for access to classified or restricted materials or areas.",
      "definition_rus": "Персонал, допущенный к доступу к секретным или ограниченным материалам или помещениям.",
      "synonyms_eng": ["cleared staff", "accredited personnel", "authorized staff"],
      "synonyms_rus": ["уполномоченные сотрудники", "аккредитованный персонал", "служебный персонал"]
    }
  ]
}
```

---

## 7. Chunk Export and Merge Scripts

**Export chunks:**
```bash
python scripts/export_synonym_chunks.py [--chunk-size 20]
```
- Reads `data/output/terms_for_synonyms.json`
- Writes `data/output/synonym_chunks/chunk_001.json`, `chunk_002.json`, …

**Build ready-to-send file** (prompt + chunk combined):
```bash
python scripts/build_ready_to_send.py [chunk_number]
```
- Default chunk_number=1. Writes `ready_to_send_chunk_001.txt` (or _002, etc.) with the full prompt and chunk JSON. Copy-paste the whole file into your LLM.

**Merge chunk outputs:**
1. Create `data/output/synonym_chunks_output/`
2. For each chunk: run the LLM, save its raw JSON response as `chunk_001_out.json`, `chunk_002_out.json`, … (or any `*.json` names)
3. Run:
```bash
python scripts/merge_synonym_chunks.py [--input-dir data/output/synonym_chunks_output] [--output config/term_synonyms.json]
```
- Reads all JSON files from the input directory
- Extracts `term_results` or `term_synonyms` from each
- Deduplicates by (entry_eng, entry_rus)
- Writes merged `config/term_synonyms.json`

---

## 8. Quality Guidelines (for the agent)

- **Preserve exact strings:** `entry_eng` and `entry_rus` must match the input character-for-character.
- **Empty arrays for special cases:** Proper nouns, numbers, document titles in quotes, fragments with `[...]` → `synonyms_eng: []`, `synonyms_rus: []`, optional `notes`.
- **Bilingual consistency:** Definitions should describe the same concept; synonyms should be parallel across languages where possible.
- **Register:** Match the tone of KGB memos, intelligence reports, and Soviet bureaucratic prose.

---

## 9. Relation to Existing Workflows

| Workflow | Input | Process | Output |
|----------|-------|---------|--------|
| Framing assessment | segments_only_&lt;doc&gt;.json | Agent reads, assigns category + framing | agent_assessments.json |
| Synonym (current) | terms_for_synonyms.json | Curated map + NLTK + wiki-synonyms | term_synonyms.json |
| **Synonym (chunked chat)** | synonym_chunks/chunk_N.json | LLM prompt per chunk | merged term_synonyms.json |

The chunked chat workflow parallels the framing assessment: same "work in batches, merge at the end" pattern, but the agent is an LLM with a structured prompt instead of a human.

---

## 10. Checklist for Synonym Chat Agent

- [ ] Run `export_terms_for_synonyms.py` to get `terms_for_synonyms.json`
- [ ] Split into chunks (script or manual)
- [ ] For each chunk: paste terms into user prompt, send to LLM, save raw JSON output
- [ ] Merge chunk outputs into single `term_synonyms.json`
- [ ] Optionally add definitions to a future extended format for "click for definition"
- [ ] Save to `config/term_synonyms.json` or `data/output/term_synonyms.json`
