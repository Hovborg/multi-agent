"""Claude Agent SDK adapter: convert catalog agents to Claude SDK configurations."""

from __future__ import annotations

from typing import Any

from multiagent.catalog import AgentDefinition, Catalog

try:
    import anthropic  # noqa: F401

    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


def _require_anthropic() -> None:
    if not HAS_ANTHROPIC:
        raise ImportError(
            "Anthropic SDK is not installed. Install with: pip install multi-agent[anthropic]"
        )


def to_message_params(
    definition: AgentDefinition,
    task: str,
    model: str | None = None,
) -> dict[str, Any]:
    """Convert a catalog AgentDefinition to Anthropic messages.create() params.

    Example:
        params = claude_sdk.to_message_params(agent_def, "Review this code")
        response = client.messages.create(**params)
    """
    _require_anthropic()
    return {
        "model": model
        or definition.cost_profile.recommended_models.get("balanced", "claude-haiku-4-5"),
        "max_tokens": definition.parameters.get("max_tokens", 4096),
        "system": definition.system_prompt,
        "messages": [{"role": "user", "content": task}],
    }


def to_agent_config(definition: AgentDefinition) -> dict[str, Any]:
    """Convert to a Claude Agent SDK agent configuration dict.

    Suitable for use with Claude Code sub-agents or Managed Agents.
    """
    return {
        "name": definition.name,
        "description": definition.description,
        "system_prompt": definition.system_prompt,
        "model": definition.cost_profile.recommended_models.get("balanced", "claude-haiku-4-5"),
        "max_tokens": definition.parameters.get("max_tokens", 4096),
        "tools": [
            {"type": t.get("type", "function"), "name": t.get("name", t.get("server", ""))}
            for t in definition.tools
        ],
    }


def from_catalog(
    agent_names: str | list[str],
    catalog: Catalog | None = None,
) -> dict[str, Any] | list[dict[str, Any]]:
    """Create Claude SDK configurations from catalog names.

    Example:
        config = claude_sdk.from_catalog("code/code-reviewer")
        # Use config with Claude Agent SDK or Managed Agents
    """
    cat = catalog or Catalog()

    if isinstance(agent_names, str):
        definition = cat.load(agent_names)
        return to_agent_config(definition)

    return [to_agent_config(cat.load(name)) for name in agent_names]
