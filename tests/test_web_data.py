"""Tests for the static web catalog data bundle."""

from pathlib import Path

from multiagent.catalog import Catalog
from multiagent.web_data import build_web_catalog_data, render_catalog_data_js

CATALOG_DIR = Path(__file__).resolve().parent.parent / "catalog"
WEB_DATA_PATH = Path(__file__).resolve().parent.parent / "web" / "catalog-data.js"


def test_web_catalog_data_includes_schema_v2_metadata():
    payload = build_web_catalog_data(Catalog(CATALOG_DIR))
    agents = {agent["full_name"]: agent for agent in payload["agents"]}

    assert agents["personal/meeting-scheduler"]["safety"] == {
        "side_effect_risk": "medium",
        "requires_human_review": True,
    }
    assert agents["research/web-scraper"]["context"] == {
        "loading": "progressive",
        "max_context_tokens": 8192,
    }


def test_static_web_catalog_data_matches_generator():
    expected = render_catalog_data_js(Catalog(CATALOG_DIR))

    assert WEB_DATA_PATH.read_text(encoding="utf-8") == expected
