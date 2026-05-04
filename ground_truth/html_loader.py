"""
Load ground truth from a single HTML file (Google Sheets waffle table).
Maps columns by header text to contract: section, entry_eng, entry_rus, content_category, framing, context.
"""
from pathlib import Path
from typing import Any, Dict, List
from html.parser import HTMLParser


class _WaffleTableParser(HTMLParser):
    """Extract rows from the first table with class 'waffle'. Each row = list of cell texts."""

    def __init__(self) -> None:
        super().__init__()
        self.rows: List[List[str]] = []
        self._current_row: List[str] = []
        self._current_cell: List[str] = []
        self._in_cell = False
        self._in_table = False

    def handle_starttag(self, tag: str, attrs: list) -> None:
        d = dict(attrs)
        if tag == "table" and d.get("class", "").find("waffle") >= 0:
            self._in_table = True
        if self._in_table and tag == "tr":
            self._current_row = []
        if self._in_table and tag in ("td", "th"):
            self._in_cell = True
            self._current_cell = []

    def handle_endtag(self, tag: str) -> None:
        if self._in_table and tag in ("td", "th"):
            self._in_cell = False
            self._current_row.append("".join(self._current_cell).strip())
        if self._in_table and tag == "tr":
            self.rows.append(self._current_row)
        if tag == "table":
            self._in_table = False

    def handle_data(self, data: str) -> None:
        if self._in_cell:
            self._current_cell.append(data)


def _find_header_indices(rows: List[List[str]]) -> Dict[str, int]:
    """Find column index for each contract field by matching header text. First column often row number."""
    indices: Dict[str, int] = {}
    for row in rows:
        for i, cell in enumerate(row):
            c = (cell or "").strip().lower()
            if "entry (eng)" in c or "entry(eng)" in c:
                indices["entry_eng"] = i
            if "entry (rus)" in c or "entry (russian" in c or "russian original" in c:
                indices["entry_rus"] = i
            if "content (what" in c or "content category" in c or (c == "content" and "content_category" not in indices):
                indices["content_category"] = i
            if "category (what" in c or "(what? when? who? where?)" in c:
                indices["content_category"] = i
            if "framing" in c and "language" in c:
                indices["framing"] = i
            if "context" in c or "notes" in c:
                indices["context"] = i
            if "found on page" in c or "page(s)" in c or "section" in c:
                indices["section"] = i
        if len(indices) >= 4:  # at least entry_eng, content, framing, entry_rus
            break
    return indices


def load_ground_truth_from_html(html_path: Path) -> List[Dict[str, Any]]:
    """
    Parse one ground-truth HTML file; return list of rows with section, entry_eng, entry_rus,
    content_category, framing, context. Uses first table.waffle and detects header row.
    """
    if not html_path.exists():
        return []
    text = html_path.read_text(encoding="utf-8")
    parser = _WaffleTableParser()
    parser.feed(text)
    rows = parser.rows
    if not rows:
        return []

    idx = _find_header_indices(rows)
    if not idx:
        return []
    entry_eng_i = idx.get("entry_eng", 3)
    entry_rus_i = idx.get("entry_rus", 4)
    content_i = idx.get("content_category", 1)
    framing_i = idx.get("framing", 2)
    context_i = idx.get("context", -1)
    section_i = idx.get("section", -1)

    out: List[Dict[str, Any]] = []
    # Skip until we're past the header; header row often contains "Entry (ENG)" or "Content"
    data_start = 0
    for r in range(len(rows)):
        cells = rows[r]
        if entry_eng_i < len(cells) and "entry (eng)" in (cells[entry_eng_i] or "").lower():
            data_start = r + 1
            break
        if content_i < len(cells) and "content (what" in (cells[content_i] or "").lower():
            data_start = r + 1
            break

    for r in range(data_start, len(rows)):
        cells = rows[r]
        if entry_eng_i >= len(cells):
            continue
        entry_eng = (cells[entry_eng_i] or "").strip()
        if not entry_eng:
            continue
        entry_rus = (cells[entry_rus_i] if entry_rus_i < len(cells) else "").strip() if entry_rus_i >= 0 else ""
        content_category = (cells[content_i] if content_i < len(cells) else "").strip() if content_i >= 0 else ""
        framing = (cells[framing_i] if framing_i < len(cells) else "").strip() if framing_i >= 0 else ""
        context = (cells[context_i] if context_i >= 0 and context_i < len(cells) else "").strip() if context_i >= 0 else ""
        section_val = cells[section_i] if section_i >= 0 and section_i < len(cells) else ""
        try:
            section = int(section_val) if section_val else (r - data_start + 1)
        except ValueError:
            section = r - data_start + 1
        out.append({
            "section": section,
            "entry_eng": entry_eng,
            "entry_rus": entry_rus,
            "content_category": content_category,
            "framing": framing,
            "context": context or entry_eng[:200],
        })
    return out
