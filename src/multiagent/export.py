"""Export catalog agents to platform-specific formats.

Supported targets:
  - claude-code: .md subagent files for Claude Code's .claude/agents/ directory
  - agentskill: SKILL.md-style portable AgentSkills files
  - a2a-agent-card: A2A Agent Card JSON for agent discovery
  - codex: AGENTS.md format for OpenAI Codex / OpenClaw
  - codex-config: project-scoped .codex/config.toml role config
  - gemini: Google ADK agent config (YAML)
  - chatgpt: Custom GPT / system instruction format
  - raw: Just the system prompt (works with any LLM)
"""

from __future__ import annotations

import json
from pathlib import Path

from multiagent.catalog import AgentDefinition


def to_claude_code(agent: AgentDefinition) -> str:
    """Export agent as a Claude Code subagent file (.md format).

    Usage:
        Save output to .claude/agents/{agent.name}.md
        Claude Code can auto-delegate based on the frontmatter description.
    """
    trigger_hint = ", ".join(agent.tags) if agent.tags else agent.category
    tools_section = ""
    if agent.tools:
        tool_names = [t.get("name", t.get("server", "unknown")) for t in agent.tools]
        tools_section = (
            "\n## Catalog Tool Hints\n\n"
            + "\n".join(f"- {t}" for t in tool_names)
            + "\n"
        )

    companions = ""
    if agent.works_with:
        companions = (
            "\n## Related Agents\n\n"
            + "\n".join(f"- `{c}`" for c in agent.works_with)
            + "\n"
        )

    return f"""---
name: {agent.name}
description: >
  {agent.description}
  Use when tasks involve: {trigger_hint}.
---

# {agent.name.replace('-', ' ').title()}

{agent.system_prompt.strip()}
{tools_section}{companions}"""


def to_agentskill(agent: AgentDefinition) -> str:
    """Export agent as a portable AgentSkills-style SKILL.md file.

    Usage:
        Save output to .agents/skills/{agent.name}/SKILL.md or another
        AgentSkills-compatible directory.
    """
    tools_section = ""
    if agent.tools:
        tool_names = [t.get("name", t.get("server", "unknown")) for t in agent.tools]
        tools_section = "\n## Tools\n\n" + "\n".join(f"- {t}" for t in tool_names) + "\n"

    companions = ""
    if agent.works_with:
        companions = (
            "\n## Related Agents\n\n"
            + "\n".join(f"- `{c}`" for c in agent.works_with)
            + "\n"
        )

    return f"""---
name: {agent.name}
description: >
  {agent.description}

  TRIGGER THIS SKILL WHEN:
  - Tasks matching: {', '.join(agent.tags)}
metadata:
  version: {agent.version}
  category: {agent.category}
  source: multi-agent catalog
---

# {agent.name.replace('-', ' ').title()}

{agent.system_prompt.strip()}
{tools_section}{companions}"""


def to_a2a_agent_card(agent: AgentDefinition) -> str:
    """Export agent as an A2A Agent Card JSON document.

    Usage:
        Serve as /.well-known/agent-card.json for an A2A service, or use as a
        starting point for registry/discovery metadata.
    """
    display_name = _display_name(agent.name)
    modes = ["text/plain", "application/json"]
    card = {
        "name": display_name,
        "description": agent.description,
        "version": agent.version,
        "supportedInterfaces": [
            {
                "url": f"http://localhost:8000/a2a/{agent.name}",
                "protocolBinding": "JSONRPC",
                "protocolVersion": "1.0",
            }
        ],
        "capabilities": {
            "streaming": False,
            "pushNotifications": False,
            "extendedAgentCard": False,
        },
        "defaultInputModes": modes,
        "defaultOutputModes": modes,
        "skills": [
            {
                "id": agent.name,
                "name": display_name,
                "description": agent.description,
                "tags": agent.tags,
                "examples": [_example_prompt(agent)],
                "inputModes": modes,
                "outputModes": modes,
            }
        ],
    }
    return json.dumps(card, indent=2) + "\n"


def to_codex(agent: AgentDefinition) -> str:
    """Export agent as an AGENTS.md section for OpenAI Codex / OpenClaw.

    Usage:
        Append output to your project's AGENTS.md
    """
    tags_str = ", ".join(agent.tags)
    companions = ""
    if agent.works_with:
        companions = "\n### Works With\n\n" + "\n".join(f"- `{c}`" for c in agent.works_with)

    patterns = ""
    if agent.recommended_patterns:
        patterns = "\n### Recommended Patterns\n\n" + "\n".join(
            f"- **{p['name']}**: {p.get('description', '')}" for p in agent.recommended_patterns
        )

    return f"""## {agent.name.replace('-', ' ').title()}

**Category:** {agent.category} | **Tags:** {tags_str}

{agent.description}

### Instructions

{agent.system_prompt.strip()}
{companions}{patterns}

---
"""


def to_codex_config(agent: AgentDefinition) -> str:
    """Export agent as a Codex project-scoped config.toml snippet.

    Usage:
        Save output to .codex/config.toml for a single role, or merge the
        [agents.<name>] block into an existing project config.
    """
    name = agent.name.replace("-", "_")
    display_name = _display_name(agent.name)
    trigger_hint = ", ".join(agent.tags) if agent.tags else agent.category
    prompt_summary = agent.system_prompt.strip().split("\n\n", maxsplit=1)[0]
    description = "\n".join(
        [
            agent.description.strip(),
            "",
            prompt_summary,
            "",
            f"Use when tasks involve: {trigger_hint}.",
            f"Catalog source: {agent.full_name} v{agent.version}.",
        ]
    )

    return f"""#:schema https://developers.openai.com/codex/config-schema.json
# Codex project config generated from multi-agent catalog: {agent.full_name}
# Save as .codex/config.toml, or merge the [agents.{name}] block into an existing config.

[features]
multi_agent = true

[agents]
max_threads = 6
max_depth = 1
job_max_runtime_seconds = 1800

[agents.{name}]
description = {_toml_string(description)}
nickname_candidates = {_toml_array([display_name])}
"""


def to_gemini(agent: AgentDefinition) -> str:
    """Export agent as a Google ADK / Gemini agent config (YAML).

    Usage:
        Save as agent config for Google ADK or Vertex AI Agent Builder.
    """
    model = agent.cost_profile.recommended_models.get("balanced", "gemini-2.5-flash")
    tools_yaml = ""
    if agent.tools:
        tools_lines = []
        for t in agent.tools:
            if t.get("type") == "mcp":
                tools_lines.append(f"    - type: mcp\n      server: {t.get('server', '')}")
            else:
                tools_lines.append(
                    f"    - name: {t.get('name', '')}\n"
                    f"      description: {t.get('description', '')}"
                )
        tools_yaml = "\n  tools:\n" + "\n".join(tools_lines)

    return f"""# Google ADK Agent Config
# Generated from multi-agent catalog: {agent.full_name}

name: {agent.name.replace('-', '_')}
model: {model}
description: {agent.description}
instruction: |
{_indent(agent.system_prompt.strip(), 2)}
generate_content_config:
  temperature: {agent.parameters.get('temperature', 0.2)}
  max_output_tokens: {agent.parameters.get('max_tokens', 4096)}{tools_yaml}
"""


def to_chatgpt(agent: AgentDefinition) -> str:
    """Export agent as ChatGPT Custom GPT / system instructions.

    Usage:
        Paste into ChatGPT's "Instructions" field when creating a Custom GPT,
        or use as the system message in the API.
    """
    companions_note = ""
    if agent.works_with:
        companion_names = ", ".join(c.split("/")[-1].replace("-", " ") for c in agent.works_with)
        companions_note = f"\n\nFor best results, combine with: {companion_names}."

    return f"""{agent.system_prompt.strip()}
{companions_note}

---
Source: multi-agent catalog ({agent.full_name} v{agent.version})
"""


def to_raw(agent: AgentDefinition) -> str:
    """Export just the system prompt. Works with any LLM.

    Usage:
        Use as system prompt with any model via any API.
    """
    return agent.system_prompt.strip()


# All exporters
EXPORTERS = {
    "claude-code": to_claude_code,
    "agentskill": to_agentskill,
    "a2a-agent-card": to_a2a_agent_card,
    "codex": to_codex,
    "codex-config": to_codex_config,
    "gemini": to_gemini,
    "chatgpt": to_chatgpt,
    "raw": to_raw,
}


def export_agent(
    agent: AgentDefinition,
    target: str,
    output_dir: Path | None = None,
) -> str:
    """Export an agent definition to a platform-specific format.

    Args:
        agent: The agent definition to export
        target: Target platform (claude-code, agentskill, a2a-agent-card, codex, codex-config, gemini, chatgpt, raw)
        output_dir: Optional directory to write the file to

    Returns:
        The exported content as a string
    """
    if target not in EXPORTERS:
        raise ValueError(f"Unknown target '{target}'. Available: {list(EXPORTERS)}")

    content = EXPORTERS[target](agent)

    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        ext = {
            "claude-code": ".md",
            "agentskill": ".md",
            "a2a-agent-card": ".agent-card.json",
            "codex": ".md",
            "codex-config": ".toml",
            "gemini": ".yaml",
            "chatgpt": ".txt",
            "raw": ".txt",
        }[target]

        filename = f"{agent.name}{ext}"
        (output_dir / filename).write_text(content, encoding="utf-8")

    return content


def _indent(text: str, spaces: int) -> str:
    """Indent each line of text."""
    prefix = " " * spaces
    return "\n".join(prefix + line if line.strip() else line for line in text.splitlines())


def _display_name(name: str) -> str:
    """Create a human-readable display name from an agent slug."""
    return " ".join(part.capitalize() for part in name.split("-"))


def _example_prompt(agent: AgentDefinition) -> str:
    """Create a short A2A skill example prompt from catalog metadata."""
    trigger_hint = ", ".join(agent.tags[:3]) if agent.tags else agent.category
    return f"Use {agent.name} for {trigger_hint} tasks."


def _toml_array(values: list[str]) -> str:
    """Serialize a string list as a TOML array."""
    return "[" + ", ".join(_toml_string(value) for value in values) + "]"


def _toml_string(value: str) -> str:
    """Serialize a Python string as a TOML basic string."""
    escapes = {
        "\\": "\\\\",
        '"': '\\"',
        "\b": "\\b",
        "\t": "\\t",
        "\n": "\\n",
        "\f": "\\f",
        "\r": "\\r",
    }
    return '"' + "".join(escapes.get(char, char) for char in value) + '"'
