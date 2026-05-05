#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerate data/experiments/exp_b_free_segment/preliminary_results.html from agent_assessments.json."""

from __future__ import annotations

import html
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "data" / "experiments" / "exp_b_free_segment"
INDEX = EXP / "originals_index.json"
DATA = EXP / "agent_assessments.json"
OUT = EXP / "preliminary_results.html"

CSS_AND_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Experiment B — preliminary results</title>
<style>
  :root { --bg: #1a1814; --paper: #ede8df; --ink: #2c2419; --muted: #5c5346; --border: #c4baa8; }
  * { box-sizing: border-box; }
  body { font-family: "Segoe UI", system-ui, sans-serif; background: var(--bg); color: var(--ink); margin: 0; padding: 1.5rem 2rem 3rem; line-height: 1.45; }
  main { max-width: 1200px; margin: 0 auto; background: var(--paper); padding: 2rem 2.25rem; border: 1px solid var(--border); box-shadow: 0 4px 24px rgba(0,0,0,.35); }
  h1 { font-size: 1.35rem; font-weight: 600; margin: 0 0 0.35rem; }
  .sub { color: var(--muted); font-size: 0.9rem; margin-bottom: 1.5rem; }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; margin-bottom: 1.75rem; }
  @media (max-width: 800px) { .grid { grid-template-columns: 1fr; } }
  .card { border: 1px solid var(--border); padding: 1rem 1.1rem; background: #f7f4ec; }
  .card h2 { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); margin: 0 0 0.65rem; }
  table.summary { width: 100%; font-size: 0.88rem; border-collapse: collapse; }
  table.summary td { padding: 0.28rem 0.4rem; border-bottom: 1px solid #dcd5c8; }
  table.summary td.num { text-align: right; width: 3rem; }
  h3 { font-size: 0.95rem; margin: 2rem 0 0.75rem; border-bottom: 1px solid var(--border); padding-bottom: 0.35rem; }
  table.segments { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
  table.segments th { text-align: left; font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); padding: 0.5rem 0.45rem; border-bottom: 2px solid var(--border); background: #e8e2d6; }
  table.segments td { padding: 0.55rem 0.45rem; border-bottom: 1px solid #dcd5c8; vertical-align: top; }
  td.muted { color: var(--muted); white-space: nowrap; width: 4.5rem; }
  td.num { text-align: center; width: 2.5rem; }
  td.rus { font-family: Consolas, "Courier New", monospace; font-size: 0.78rem; max-width: 320px; }
  td.eng { color: #3d3528; max-width: 280px; }
  td.ctx { color: var(--muted); font-size: 0.78rem; max-width: 220px; }
  .pill { display: inline-block; padding: 0.12rem 0.45rem; border-radius: 3px; font-size: 0.72rem; line-height: 1.3; white-space: nowrap; }
  .pill.cc { background: #dbe7f0; border: 1px solid #9db8cc; }
  .pill.fr { background: #f0e8db; border: 1px solid #c4a574; }
  .pending { margin-top: 1.5rem; font-size: 0.85rem; color: var(--muted); }
</style>
</head>
<body>
<main>
  <h1>Experiment B — preliminary assessor results</h1>
  <p class="sub">Free segmentation · <code>data/experiments/exp_b_free_segment/agent_assessments.json</code> · open in browser · regenerated via <code>scripts/exp_b_preliminary_html.py</code>.</p>
"""


def main() -> None:
    idx = json.loads(INDEX.read_text(encoding="utf-8"))
    doc_ids = [d["document_id"] for d in idx["documents"]]
    assessments = json.loads(DATA.read_text(encoding="utf-8"))

    filled = [d for d in doc_ids if assessments.get(d)]
    total_docs = len(doc_ids)
    n_filled = len(filled)
    filled_label = ", ".join(filled) if filled else "(none)"

    rows_out: list[str] = []
    cc_ctr: Counter[str] = Counter()
    fr_ctr: Counter[str] = Counter()
    total_segments = 0

    for doc_id in doc_ids:
        segs = assessments.get(doc_id) or []
        if not segs:
            continue
        segs = sorted(segs, key=lambda r: r.get("section", 0))
        for i, row in enumerate(segs, start=1):
            total_segments += 1
            cc = row.get("content_category") or ""
            fr = row.get("framing") or ""
            if cc:
                cc_ctr[cc] += 1
            if fr:
                fr_ctr[fr] += 1
            rus_raw = row.get("entry_rus") or ""
            rus = html.escape(rus_raw).replace("\n", "<br>\n")
            eng = html.escape(row.get("entry_eng") or "")
            ctx = html.escape(row.get("context") or "")
            rows_out.append(
                f"""<tr>
<td class="muted">{html.escape(doc_id)}</td>
<td class="num">{i}</td>
<td><span class="pill cc">{html.escape(cc)}</span></td>
<td><span class="pill fr">{html.escape(fr)}</span></td>
<td class="rus">{rus}</td>
<td class="eng">{eng}</td>
<td class="ctx">{ctx}</td>
</tr>"""
            )

    cc_rows = "".join(
        f'<tr><td>{html.escape(k)}</td><td class="num">{v}</td></tr>'
        for k, v in sorted(cc_ctr.items(), key=lambda x: (-x[1], x[0]))
    )
    fr_rows = "".join(
        f'<tr><td>{html.escape(k)}</td><td class="num">{v}</td></tr>'
        for k, v in sorted(fr_ctr.items(), key=lambda x: (-x[1], x[0]))
    )

    pending = [d for d in doc_ids if d not in filled]
    pending_html = ""
    if pending:
        pending_html = (
            '<p class="pending">Pending (no segments yet): '
            + html.escape(", ".join(pending))
            + "</p>"
        )

    body = f"""  <div class="grid">
    <div class="card">
      <h2>Documents with segments</h2>
      <p style="margin:0;font-size:1.1rem"><strong>{n_filled}</strong> / {total_docs}</p>
      <p style="margin:0.5rem 0 0;font-size:0.85rem;color:var(--muted)">Filled: {html.escape(filled_label)}</p>
    </div>
    <div class="card">
      <h2>Total segment rows</h2>
      <p style="margin:0;font-size:1.1rem"><strong>{total_segments}</strong></p>
    </div>
    <div class="card">
      <h2>Content categories</h2>
      <table class="summary">{cc_rows}</table>
    </div>
    <div class="card">
      <h2>Framing</h2>
      <table class="summary">{fr_rows}</table>
    </div>
  </div>
  <h3>All segments</h3>
  <table class="segments">
    <thead><tr><th>Doc</th><th>#</th><th>Category</th><th>Framing</th><th>Russian</th><th>English</th><th>Context</th></tr></thead>
    <tbody>{"".join(rows_out)}</tbody>
  </table>
{pending_html}
</main>
</body>
</html>
"""
    OUT.write_text(CSS_AND_HEAD + body, encoding="utf-8")
    print(f"Wrote {OUT} ({n_filled} docs, {total_segments} segments)")


if __name__ == "__main__":
    main()
