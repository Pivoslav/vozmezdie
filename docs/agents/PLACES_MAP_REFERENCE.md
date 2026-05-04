# Places Map: Reference for Later

**Status:** Full integration complete. Places Map is a viz option in the main report Home tab. Opens in new window (`data/output/places_map.html`).

**Data fix (Feb 2025):** "By document" and main count use **segment count** (number of rows), not the sum of extracted numbers (e.g. "In Kyiv — 55" contributed 55 before; now each segment contributes 1). Segments popup section is closed by default.

---

## Summary

An interactive map using "places data" is **feasible**. Scripts extract place names from Places-tagged segments, normalize them, geocode via static coords + Nominatim, and a standalone demo renders a Leaflet map with markers sized by mention count.

---

## What We Have

1. **Places-tagged segments** (~364 segments with content_category "Places")
   - Phrases like: "In Kyiv", "In Odesa Oblast — 53", "In Kharkiv Oblast — 12", "From the U.S. — 32", "At the ports of Odesa, Zhdanov, and Kherson"
   - Source: `terms_in_cat("Places")` or aligned rows with `llm_category` / `human_category` = "Places"

2. **Place-like terms in word cloud**
   - kyiv, odesa, kharkiv, lviv, donetsk, canada, usa, oblast, republic, embassy
   - From `_collect_terms_from_comparison` or word cloud data

3. **Terms by category**
   - `terms_in_cat(cat)` gives unique (entry_eng, entry_rus) pairs from segments with that category

---

## What We Need for a Map

| Requirement | Status | Notes |
|-------------|--------|-------|
| Place names extracted from text | Done | `extract_places.py` parses "In Kyiv — 55", "From the U.S. — 32", etc. |
| Normalization (Kyiv/Kiev, Odesa/Odessa) | Done | Variants and oblast handled; Zhdanov → Mariupol |
| Coordinates (lat/lon) | Done | Static coords + Nominatim; cached in `places_geocoded.json` |
| Counts per place | Done | Segment count (rows), not sum of extracted numbers |
| Map rendering | Done | Leaflet; report generates `places_map.html` |

---

## Challenges

- **Historical names:** Soviet-era names (e.g. Zhdanov → Mariupol) may need a gazetteer
- **Ambiguity:** "Washington" = state or DC; "central" may not be a place
- **Phrase structure:** Numbers in "In Kyiv — 55" are counts, not coordinates
- **No geo in pipeline:** Framework does not store place-level or coordinate data

---

## Implemented

1. **scripts/extract_places.py** — Extracts place names from Places-tagged segments in comparison_results.json. Parses patterns like "In Kyiv — 55", "From the U.S. — 32", "At the ports of Odesa, Zhdanov, and Kherson". Normalizes variants (Kiev→Kyiv, Zhdanov→Mariupol). Output: `data/output/places_extracted.json`.

2. **scripts/geocode_places.py** — Geocodes via static coords (Ukrainian cities, countries) + Nominatim (1 req/sec). Caches in `data/output/places_geocoded.json`. Use `--refresh` to re-geocode.

3. **scripts/build_places_map_demo.py** — Embeds geocoded data into standalone HTML. Output: `presentations/demos/places_map_demo.html`.

4. **Demo** — Leaflet map, markers sized by count, archival/KGB styling (deep red markers, cream background).

---

## Relevant Paths

| What | Path |
|------|------|
| Extract script | `scripts/extract_places.py` |
| Geocode script | `scripts/geocode_places.py` |
| Extracted places | `data/output/places_extracted.json` |
| Geocoded places | `data/output/places_geocoded.json` |
| Report places map | `data/output/places_map.html` (generated with report) |
| Report module | `report/__init__.py` (`_load_places_map_data_enriched`, `_write_places_map_html`) |
| Comparison data | `data/output/comparison_results.json` |

## Workflow

```bash
python scripts/extract_places.py
python scripts/geocode_places.py          # or --refresh to re-geocode
python run_report_only.py                 # regenerates report + places_map.html
# Open data/output/manual_analysis_report.html; select "Places Map" viz, or open places_map.html directly
```

---

*Full report integration complete Feb 2025. Select "Places Map" from the visualization dropdown on the Home tab.*
