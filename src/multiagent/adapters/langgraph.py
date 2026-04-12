"""LangGraph adapter: convert catalog agents to LangGraph nodes and graphs."""

from __future__ import annotations

from typing import Any

from multiagent.catalog import AgentDefinition, Catalog

try:
    from langgraph.graph import StateGraph  # noqa: F401

    HAS_LANGGRAPH = True
except ImportError:
    HAS_LANGGRAPH = False


def _require_langgraph() -> None:
    if not HAS_LANGGRAPH:
        raise ImportError(
            "LangGraph is not installed. Install with: pip install multi-agent[langgraph]"
        )


def to_node(definition: AgentDefinition, model: str | None = None) -> dict[str, Any]:
    """Convert a catalog AgentDefinition to a LangGraph node configuration.

    Returns a dict with 'name', 'system_prompt', 'model', and 'tools' ready for
    use as a LangGraph node.
    """
    return {
        "name": definition.name,
        "system_prompt": definition.system_prompt,
        "model": model or definition.cost_profile.recommended_models.get("balanced", ""),
        "tools": definition.tools,
        "parameters": definition.parameters,
    }


def from_catalog(
    agent_names: list[str],
    flow: str = "sequential",
    catalog: Catalog | None = None,
) -> dict[str, Any]:
    """Create a LangGraph-ready configuration from catalog agents.

    Returns a configuration dict that can be used to build a StateGraph.

    Args:
        agent_names: List of catalog agent names
        flow: "sequential" or "parallel"
        catalog: Optional custom catalog instance

    Example:
        config = langgraph.from_catalog(
            ["research/deep-researcher", "research/fact-checker"],
            flow="sequential",
        )
        # Use config to build your StateGraph
    """
    cat = catalog or Catalog()

    nodes = []
    for name in agent_names:
        definition = cat.load(name)
        nodes.append(to_node(definition))

    return {
        "nodes": nodes,
        "flow": flow,
        "entry_point": nodes[0]["name"] if nodes else None,
    }
