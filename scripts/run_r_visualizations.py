#!/usr/bin/env python3
"""
Run R script to generate alluvial and other visualizations from comparison_results.json.
Requires R with packages: jsonlite, ggplot2, ggalluvial.
Install in R: install.packages(c("jsonlite", "ggplot2", "ggalluvial"))

Usage:
  python scripts/run_r_visualizations.py [path/to/comparison_results.json] [output_dir]
  Or from run_report_only.py when config has report.r_visualizations: true
"""
import subprocess
import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent


def run_r_visualizations(
    json_path: Optional[Path] = None,
    output_dir: Optional[Path] = None,
) -> bool:
    """Run R script to generate plots. Returns True if successful."""
    json_path = json_path or ROOT / "data" / "output" / "comparison_results.json"
    output_dir = output_dir or ROOT / "data" / "output" / "r_plots"

    if not json_path.exists():
        print(f"Comparison results not found: {json_path}", file=sys.stderr)
        return False

    r_script = ROOT / "scripts" / "generate_r_visualizations.R"
    if not r_script.exists():
        print(f"R script not found: {r_script}", file=sys.stderr)
        return False

    # Use paths relative to project root for R (run from ROOT)
    try:
        json_rel = json_path.relative_to(ROOT)
    except ValueError:
        json_rel = json_path
    try:
        out_rel = output_dir.relative_to(ROOT)
    except ValueError:
        out_rel = output_dir

    try:
        result = subprocess.run(
            ["Rscript", str(r_script), str(json_rel), str(out_rel)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            print(f"R script failed (exit {result.returncode}):", file=sys.stderr)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            return False
        if result.stdout:
            print(result.stdout.strip())
        return True
    except FileNotFoundError:
        print("R not found. Install R and ensure Rscript is on PATH.", file=sys.stderr)
        return False
    except subprocess.TimeoutExpired:
        print("R script timed out.", file=sys.stderr)
        return False


def main() -> int:
    json_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    if json_path and not json_path.is_absolute():
        json_path = ROOT / json_path
    if output_dir and not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    ok = run_r_visualizations(json_path, output_dir)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
