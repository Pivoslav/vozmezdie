"""
Test ingest module: fixture when no input dir, and document shape.
"""
import sys
from pathlib import Path

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
