# Filter Dimming Investigation - Findings and Suggestions

## Summary

The document text view filter (category, framing, search) should dim non-matching segments and gaps while keeping matching segments highlighted. User reports "no noticeable change" when filtering.

## Architecture Review

### Data Flow
1. **Server**: `_spans_to_html` builds HTML with `<span class="doc-entry">` for segments and `<span class="doc-entry doc-gap">` for gaps (text between/around segments)
2. **Client**: `buildDocumentTextView` populates dropdowns; when `hasPreFilled` is false, it builds content from the comparison table
3. **Filtering**: `applyDocumentSearchAndFilter(tid)` runs on change/input; it adds `filter-active` to containers and applies dimming via CSS

### Event Flow
- `document.body.addEventListener('change', ...)` captures filter changes via delegation
- `e.target.getAttribute('data-tab')` yields `tid` (e.g. "1127")
- `applyDocumentSearchAndFilter(tid)` finds `doc-text-eng-{tid}` and `doc-text-rus-{tid}`

### CSS Strategy (Current)
- `.document-text-content.filter-active .doc-entry` → dim all (color: #999, opacity: 0.4)
- `.document-text-content.filter-active .doc-entry.filter-match` → un-dim (opacity: 1, color inline)

## Potential Issues Identified

### 1. Event Not Reaching Handler
**Hypothesis**: The change event might not bubble correctly, or `e.target` might not have `data-tab` in some edge cases (e.g. when the event originates from an option rather than the select in some browsers).

**Suggestion**: Add direct `change` listeners to each filter select when `buildDocumentTextView` runs, so we don't rely solely on delegation.

### 2. Details Element / Lazy Rendering
**Hypothesis**: The document text view is inside `<details class="collapsible-section">`. When closed, some browsers may not fully render or style the content. If the user changes a filter before expanding, or if there's a timing issue, styles might not apply correctly.

**Suggestion**: Ensure `applyDocumentSearchAndFilter` runs when the details is opened (e.g. via `details` toggle listener) to re-apply filters to newly visible content.

### 3. Dimming Too Subtle
**Hypothesis**: `#999` with `opacity: 0.4` might be too subtle on some displays or with the document's background (#fffef9, #f5f0e6).

**Suggestion**: Use more dramatic dimming: e.g. `color: #bbb`, `opacity: 0.25`, or `filter: grayscale(1) brightness(0.6)`.

### 4. Wrong Container or Missing Elements
**Hypothesis**: `getElementById('doc-text-eng-' + tid)` might fail if `tid` has unexpected format (e.g. spaces, special chars). Document IDs use underscores (e.g. `1262_28-32`), so this is likely fine.

**Suggestion**: Add a fallback to derive `tid` from the select's `id` (e.g. `doc-fram-1127` → `1127`) when `data-tab` is missing.

### 5. CSS Specificity / Override
**Hypothesis**: Another rule might override our dimming. The `.document-text-content .doc-entry` has `cursor: pointer` and other rules. The `!important` on our dimming rule should win, but worth verifying.

**Suggestion**: Use a more specific selector or ensure our dimming rules come last in the stylesheet.

### 6. Script Error Preventing Execution
**Hypothesis**: A JavaScript error earlier in the script could prevent `applyDocumentSearchAndFilter` or the event handlers from running.

**Suggestion**: Add a minimal `try/catch` and `console.log` in development to verify the handler runs and has correct values.

## Recommended Fixes (in order)

1. **Direct event listeners**: In `buildDocumentTextView`, after populating the dropdowns, attach `change` and `input` listeners directly to the filter elements for that tab, calling `applyDocumentSearchAndFilter(tid)`.

2. **Details toggle handler**: Add a listener for the "Document text view" details `toggle` event; when it opens, call `applyDocumentSearchAndFilter` for the visible document tab to re-apply filters.

3. **Stronger dimming**: Change dimming to `color: #aaa; opacity: 0.3` or use `filter: grayscale(1) brightness(0.5)` for a more obvious effect.

4. **Fallback tid extraction**: If `data-tab` is empty, parse `tid` from `e.target.id` (e.g. `doc-fram-1127` → `1127`).

5. **Debug mode**: Add an optional `?debug=1` query param that logs when `applyDocumentSearchAndFilter` runs and the values of `hasFilter`, `catFilter`, `framFilter`, and element counts.
