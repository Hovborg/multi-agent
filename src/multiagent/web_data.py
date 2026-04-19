"""Generate the static browser catalog data bundle."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from multiagent.catalog import AgentDefinition, Catalog
from multiagent.cost import MODEL_PRICING
from multiagent.enhance import CATEGORY_PROFILES, ENHANCEMENTS_DIR


def build_web_catalog_data(catalog: Catalog | None = None) -> dict[str, Any]:
    """Build the JSON-serializable payload used by web/catalog-data.js."""
    cat = catalog or Catalog()
    enhancements = _list_web_enhancements()
    return {
        "agents": [_agent_to_web_dict(agent) for agent in cat.list_all()],
        "model_pricing": MODEL_PRICING,
        "category_profiles": CATEGORY_PROFILES,
        "enhancements": {
            item["name"]: item["prompt_block"]
            for item in enhancements
        },
        "enhancement_names": [item["name"] for item in enhancements],
    }


def render_catalog_data_js(catalog: Catalog | None = None) -> str:
    """Render the static JavaScript assignment for the browser playground."""
    payload = build_web_catalog_data(catalog)
    return f"const CATALOG_DATA = {json.dumps(payload, indent=2, sort_keys=False)};\n"


def write_catalog_data_js(
    output_path: Path | str = Path("web/catalog-data.js"),
    catalog: Catalog | None = None,
) -> Path:
    """Write a fresh web/catalog-data.js bundle and return its path."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_catalog_data_js(catalog), encoding="utf-8")
    return path


def _agent_to_web_dict(agent: AgentDefinition) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "name": agent.name,
        "version": agent.version,
        "full_name": agent.full_name,
        "category": agent.category,
        "description": agent.description,
        "tags": agent.tags,
        "system_prompt": agent.system_prompt,
        "tools": agent.tools,
        "parameters": agent.parameters,
        "works_with": agent.works_with,
        "recommended_patterns": agent.recommended_patterns,
        "cost_profile": {
            "input_tokens": agent.cost_profile.input_tokens_per_run,
            "output_tokens": agent.cost_profile.output_tokens_per_run,
            "recommended_models": agent.cost_profile.recommended_models,
            "estimated_cost": agent.cost_profile.estimated_cost,
        },
    }

    for field_name in (
        "orchestration",
        "safety",
        "observability",
        "outputs",
        "context",
        "protocols",
    ):
        value = getattr(agent, field_name)
        if value:
            payload[field_name] = value

    return payload


def _list_web_enhancements() -> list[dict[str, Any]]:
    enhancements = []
    for path in sorted(ENHANCEMENTS_DIR.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            continue
        enhancements.append({
            "name": data.get("name", path.stem),
            "prompt_block": data.get("prompt_block", "").strip(),
        })
    return enhancements
