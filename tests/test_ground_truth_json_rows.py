"""Ground truth loads JSON rows when json_rows_dir is set."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def test_gt_prefers_json_rows_dir(tmp_path):
    from ground_truth import run as gt_run

    rows = [
        {
            "section": 1,
            "entry_eng": "Hello",
            "entry_rus": "Привет",
            "content_category": "Actors",
            "framing": "Institutional / Bureaucratic Lingo",
            "context": "Hello",
        }
    ]
    jdir = tmp_path / "gtjson"
    jdir.mkdir()
    (jdir / "doc_json_only.json").write_text(json.dumps(rows), encoding="utf-8")

    config = {
        "ground_truth": {"json_rows_dir": str(jdir)},
        "taxonomy": {"path": str(ROOT / "config" / "taxonomy.json")},
    }
    out = gt_run(config, ["doc_json_only"])
    assert len(out["doc_json_only"]) == 1
    assert out["doc_json_only"][0]["content_category"] == "Actors"
