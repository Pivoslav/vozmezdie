# Data

Default locations (config can override):

- **`input/`** — source document texts (e.g. `.txt`). One file per document; stem becomes `document_id` (spaces in stem become underscores in `document_id`). Populated from dev: English translations copied with names matching ground-truth HTML stems (e.g. `1128.txt`, `1262 28-32.txt`).
- **`ground_truth/html/`** — human-coded ground truth: one HTML file per document (Google Sheets export, `<table class="waffle">`). Filenames match input stems (e.g. `1128.html`, `1262 28-32.html`). `resources/sheet.css` is included for sheet styling.
- **`output/`** — generated report HTML and intermediate comparison JSON.

Config can override these paths.
