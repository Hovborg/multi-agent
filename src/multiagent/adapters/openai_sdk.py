"""OpenAI Agents SDK adapter: convert catalog agents to OpenAI Agent instances."""

from __future__ import annotations

from typing import Any

from multiagent.catalog import AgentDefinition, Catalog

try:
    from agents import Agent

    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


def _require_openai() -> None:
    if not HAS_OPENAI:
        raise ImportError(
            "OpenAI Agents SDK is not installed. Install with: pip install multi-agent[openai]"
        )


def to_agent(definition: AgentDefinition, **overrides: Any) -> Agent:
    """Convert a catalog AgentDefinition to an OpenAI Agent."""
    _require_openai()
    kwargs = {
        "name": definition.name.replace("-", " ").title(),
        "instructions": definition.system_prompt,
    }
    model = overrides.pop("model", None) or definition.cost_profile.recommended_models.get(
        "balanced"
    )
    if model:
        kwargs["model"] = model
    kwargs.update(overrides)
    return Agent(**kwargs)


def to_handoff_config(
    manager: AgentDefinition,
    handoffs: list[AgentDefinition],
) -> dict[str, Any]:
    """Build a framework-free OpenAI Agents SDK handoff plan.

    Handoffs transfer control to another agent. Use this when specialist agents
    should own follow-up turns rather than returning a single tool result.
    """
    return {
        "pattern": "handoff",
        "manager": _agent_template(manager),
        "handoffs": [_agent_template(agent) for agent in handoffs],
        "notes": [
            "Create OpenAI Agent objects from these fields.",
            "Pass the handoff agents through the manager Agent handoffs argument.",
        ],
    }


def to_agent_tool_config(
    manager: AgentDefinition,
    tools: list[AgentDefinition],
) -> dict[str, Any]:
    """Build a framework-free OpenAI Agents SDK agent-as-tool plan.

    Agent-as-tool keeps the manager in control and calls specialists for
    bounded work, which matches review, search, and write-assist workflows.
    """
    return {
        "pattern": "agent-as-tool",
        "manager": _agent_template(manager),
        "tools": [
            {
                **_agent_template(agent),
                "agent": agent.full_name,
                "tool_name": agent.name.replace("-", "_"),
            }
            for agent in tools
        ],
        "notes": [
            "Create each specialist as an OpenAI Agent.",
            "Expose specialists to the manager with the Agents SDK as_tool helper.",
        ],
    }


def _agent_template(definition: AgentDefinition) -> dict[str, Any]:
    return {
        "catalog_name": definition.full_name,
        "name": definition.name.replace("-", " ").title(),
        "description": definition.description,
        "instructions": definition.system_prompt,
        "model": definition.cost_profile.recommended_models.get("balanced", ""),
    }


def from_catalog(
    agent_name: str | list[str],
    catalog: Catalog | None = None,
    **kwargs: Any,
) -> Agent | list[Agent]:
    """Create OpenAI Agent(s) from catalog names.

    Example:
        agent = openai_sdk.from_catalog("code/code-reviewer")
        result = await Runner.run(agent, "Review this code")
    """
    cat = catalog or Catalog()

    if isinstance(agent_name, str):
        definition = cat.load(agent_name)
        return to_agent(definition, **kwargs)

    return [to_agent(cat.load(name), **kwargs) for name in agent_name]
