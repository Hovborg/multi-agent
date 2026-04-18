"""Demo: Export agents to every AI platform.

Shows how to use multi-agent's export system to convert catalog agents
into platform-specific formats for Claude Code, Codex, Codex config,
Gemini, ChatGPT, A2A discovery, or any other LLM.

Usage:
    pip install multi-agent
    python demo_export.py
"""

from pathlib import Path

from multiagent import Catalog, export_agent

catalog = Catalog()

# Pick an agent
agent = catalog.load("code/code-reviewer")
print(f"Agent: {agent.full_name}")
print(f"Description: {agent.description}\n")

# Show all export formats
targets = {
    "a2a-agent-card": "A2A Agent Card JSON",
    "claude-code": "Claude Code (.claude/agents subagent file)",
    "agentskill": "Portable AgentSkills (SKILL.md-style)",
    "codex": "OpenAI Codex / OpenClaw (AGENTS.md)",
    "codex-config": "OpenAI Codex project config (.codex/config.toml)",
    "gemini": "Google Gemini / ADK (YAML config)",
    "chatgpt": "ChatGPT (Custom GPT instructions)",
    "raw": "Any LLM (plain system prompt)",
}

for target, description in targets.items():
    print(f"{'='*60}")
    print(f"Target: {target} — {description}")
    print(f"{'='*60}")
    output = export_agent(agent, target)
    # Show first 10 lines
    lines = output.strip().splitlines()
    for line in lines[:10]:
        print(f"  {line}")
    if len(lines) > 10:
        print(f"  ... ({len(lines) - 10} more lines)")
    print()

# Bulk export example
output_dir = Path("/tmp/multi-agent-export-demo")
print(f"\nBulk exporting all code agents to {output_dir}/")
for agent in catalog.by_category("code"):
    export_agent(agent, "a2a-agent-card", output_dir=output_dir / "a2a-agent-card" / "code")
    export_agent(agent, "claude-code", output_dir=output_dir / "claude-code" / "code")
    export_agent(agent, "agentskill", output_dir=output_dir / "agentskill" / "code")
    export_agent(agent, "codex-config", output_dir=output_dir / "codex-config" / "code")
    export_agent(agent, "raw", output_dir=output_dir / "raw" / "code")

print(f"Done! Check {output_dir}/ for exported files.")
