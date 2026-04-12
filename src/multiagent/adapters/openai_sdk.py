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
