"""
Test ingest module: fixture when no input dir, and document shape.
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ingest import run as ingest_run


def test_ingest_returns_fixture_when_no_dir():
    config = {"documents": {"input_dir": "data/input", "extensions": [".txt"], "encoding": "utf-8"}}
    # data/input may not exist from repo root
    result = ingest_run(config)
    assert isinstance(result, list)
    assert len(result) >= 1
    for doc in result:
        assert "document_id" in doc
        assert "display_name" in doc
        assert "raw_text" in doc
        assert isinstance(doc["raw_text"], str)


def test_ingest_fixture_has_usable_text():
    config = {}
    result = ingest_run(config)
    texts = [d.get("raw_text", "") for d in result]
    assert any(len(t.strip()) > 0 for t in texts)


@pytest.mark.skipif(
    not (Path(__file__).resolve().parent.parent / "data" / "input" / "1127.txt").is_file(),
    reason="repo sample data/input/1127.txt not present",
)
def test_document_map_loads_english_from_doc_id_txt():
    """Russian-first map mode must find data/input/<document_id>.txt, not display_name-only paths."""
    root = Path(__file__).resolve().parent.parent
    cfg_path = root / "config" / "pipeline_config.example.json"
    if not cfg_path.is_file():
        pytest.skip("pipeline_config.example.json missing")
    config = json.loads(cfg_path.read_text(encoding="utf-8"))
    if not config.get("documents", {}).get("document_map_path"):
        pytest.skip("document_map_path not configured")
    docs = ingest_run(config, root)
    by_id = {d["document_id"]: d for d in docs}
    assert "1127" in by_id
    assert len((by_id["1127"].get("raw_text_en") or "").strip()) > 100
    assert len((by_id["1127"].get("raw_text") or "").strip()) > 100
    # Underscore doc id maps to spaced filename on disk
    if "1262_28-32" in by_id and (root / "data" / "input" / "1262 28-32.txt").is_file():
        assert len((by_id["1262_28-32"].get("raw_text_en") or "").strip()) > 100
