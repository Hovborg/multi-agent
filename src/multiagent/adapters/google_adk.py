"""Google ADK adapter: convert catalog agents to Google ADK agent configurations."""

from __future__ import annotations

from typing import Any

from multiagent.catalog import AgentDefinition, Catalog

try:
    from google.adk import Agent  # noqa: F401

    HAS_GOOGLE_ADK = True
except ImportError:
    HAS_GOOGLE_ADK = False


def _require_google_adk() -> None:
    if not HAS_GOOGLE_ADK:
        raise ImportError(
            "Google ADK is not installed. Install with: pip install multi-agent[google-adk]"
        )


def to_agent_config(definition: AgentDefinition) -> dict[str, Any]:
    """Convert a catalog AgentDefinition to a Google ADK agent config dict."""
    return {
        "name": definition.name.replace("-", "_"),
        "model": definition.cost_profile.recommended_models.get("balanced", "gemini-2.5-flash"),
        "instruction": definition.system_prompt,
        "description": definition.description,
        "tools": definition.tools,
    }


def to_workflow_config(
    definitions: list[AgentDefinition],
    workflow: str = "sequential",
    name: str | None = None,
) -> dict[str, Any]:
    """Create a Google ADK workflow config for multiple catalog agents."""
    workflow_types = {
        "sequential": "SequentialAgent",
        "parallel": "ParallelAgent",
    }
    if workflow not in workflow_types:
        expected = ", ".join(sorted(workflow_types))
        raise ValueError(f"Unsupported Google ADK workflow '{workflow}'. Expected: {expected}")

    workflow_name = name or f"{workflow}_{'_'.join(_agent_name(agent) for agent in definitions)}"
    return {
        "workflow": workflow,
        "agent_type": workflow_types[workflow],
        "name": workflow_name,
        "sub_agents": [to_agent_config(definition) for definition in definitions],
    }


def _agent_name(definition: AgentDefinition) -> str:
    return definition.name.replace("-", "_")


def from_catalog(
    agent_names: str | list[str],
    catalog: Catalog | None = None,
) -> dict[str, Any] | list[dict[str, Any]]:
    """Create Google ADK configurations from catalog names.

    Example:
        config = google_adk.from_catalog("research/deep-researcher")
        agent = Agent(**config)
    """
    cat = catalog or Catalog()

    if isinstance(agent_names, str):
        definition = cat.load(agent_names)
        return to_agent_config(definition)

    return [to_agent_config(cat.load(name)) for name in agent_names]
