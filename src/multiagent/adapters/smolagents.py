"""smolagents adapter: convert catalog agents to HuggingFace smolagents configurations."""

from __future__ import annotations

from typing import Any

from multiagent.catalog import AgentDefinition, Catalog

try:
    from smolagents import CodeAgent, ToolCallingAgent  # noqa: F401

    HAS_SMOLAGENTS = True
except ImportError:
    HAS_SMOLAGENTS = False


def _require_smolagents() -> None:
    if not HAS_SMOLAGENTS:
        raise ImportError(
            "smolagents is not installed. Install with: pip install multi-agent[smolagents]"
        )


def to_agent_config(
    definition: AgentDefinition,
    agent_type: str = "tool_calling",
) -> dict[str, Any]:
    """Convert a catalog AgentDefinition to smolagents configuration.

    Args:
        definition: The agent definition from catalog
        agent_type: "tool_calling" or "code" (CodeAgent writes Python instead of JSON)
    """
    return {
        "name": definition.name,
        "system_prompt": definition.system_prompt,
        "agent_type": agent_type,
        "model_id": definition.cost_profile.recommended_models.get("balanced", ""),
        "tools": definition.tools,
    }


def to_manager_config(
    manager: AgentDefinition,
    managed_agents: list[AgentDefinition],
    manager_type: str = "code",
) -> dict[str, Any]:
    """Create a smolagents manager config with managed specialist agents."""
    return {
        "agent_type": "manager",
        "manager": to_agent_config(manager, manager_type),
        "managed_agents": [
            to_agent_config(definition, agent_type="tool_calling")
            for definition in managed_agents
        ],
        "routing": [
            {
                "name": definition.name,
                "agent": definition.full_name,
                "description": definition.description,
            }
            for definition in managed_agents
        ],
    }


def from_catalog(
    agent_names: str | list[str],
    agent_type: str = "tool_calling",
    catalog: Catalog | None = None,
) -> dict[str, Any] | list[dict[str, Any]]:
    """Create smolagents configurations from catalog names.

    Example:
        config = smolagents.from_catalog("research/deep-researcher", agent_type="code")
        agent = CodeAgent(model=HfApiModel(config["model_id"]))
    """
    cat = catalog or Catalog()

    if isinstance(agent_names, str):
        definition = cat.load(agent_names)
        return to_agent_config(definition, agent_type)

    return [to_agent_config(cat.load(name), agent_type) for name in agent_names]
