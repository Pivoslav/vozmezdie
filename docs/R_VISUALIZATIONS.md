# R Visualizations

Optional R-based visualizations for the report. Requires R and packages: jsonlite, ggplot2, ggdendro.

## Setup

1. Install [R](https://www.r-project.org/) and ensure `Rscript` is on your PATH.

2. In R, install required packages:
   ```r
   install.packages(c("jsonlite", "ggplot2", "ggdendro"))
   ```

## Usage

**Generate R plots and include in report:**
```bash
python run_report_only.py --r-viz
```

**Generate R plots only (standalone):**
```bash
python scripts/run_r_visualizations.py [path/to/comparison_results.json] [output_dir]
```

**Or run R directly:**
```bash
Rscript scripts/generate_r_visualizations.R data/output/comparison_results.json data/output/r_plots
```

## Output

Plots are written to `data/output/r_plots/`:
- `alluvial_framing.png` – Heatmap: LLM framing x human framing (counts; diagonal = agreement)
- `alluvial_category.png` – Heatmap: LLM category x human category (counts; diagonal = agreement)
- `dendrogram_documents.png` – Hierarchical clustering of documents by framing profile (with labels)
- `segment_length_accuracy.png` – Bar chart: % correct by segment length bucket

When these files exist, the report shows an "R Visualizations" option in the Visualizations dropdown.
