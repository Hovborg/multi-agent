# Use Your Agents on Any Platform

**Difficulty:** Medium

## What you'll build

You will export a single agent definition to eight different formats: A2A Agent
Card JSON, Claude Code, Codex/OpenClaw, Codex project config, Google Gemini/ADK,
ChatGPT Custom GPTs, raw system prompts for Ollama, and portable AgentSkills.
You will also learn bulk export for entire categories.

## Prerequisites

- Python 3.10+
- `pip install multi-agent`
- Completed [01 -- Getting Started](01-getting-started.md)

## The 8 export targets

| Target | Format | Works with |
|--------|--------|------------|
| `claude-code` | `.md` subagent files | Claude Code `.claude/agents/` |
| `agentskill` | `SKILL.md`-style Markdown | AgentSkills-compatible tools |
| `a2a-agent-card` | Agent Card JSON | A2A discovery via `.well-known/agent-card.json` |
| `codex` | AGENTS.md sections | OpenAI Codex, OpenClaw |
| `codex-config` | `.codex/config.toml` snippet | OpenAI Codex multi-agent roles |
| `gemini` | ADK YAML config | Google Gemini, Vertex AI |
| `chatgpt` | System instructions | ChatGPT, Custom GPTs |
| `raw` | Plain system prompt | Ollama, LM Studio, llama.cpp, vLLM, any LLM |

## Export to Claude Code

Claude Code discovers project subagents from `.claude/agents/`.

```python
from multiagent import Catalog, export_agent

catalog = Catalog()
agent = catalog.load("code/code-reviewer")

# Export to disk
export_agent(agent, target="claude-code", output_dir=".claude/agents")
```

From the CLI:

```bash
multiagent export code/code-reviewer claude-code -o .claude/agents
```

## Export as AgentSkills

Use `agentskill` when you want portable `SKILL.md`-style files:

```bash
multiagent export code/code-reviewer agentskill -o .agents/skills/code-reviewer
```

## Export as an A2A Agent Card

Use `a2a-agent-card` when an agent needs discovery metadata for an A2A service:

```bash
multiagent export code/code-reviewer a2a-agent-card -o ./agent-cards
```

## Export to Codex, Gemini, and ChatGPT

Each target uses the same `export_agent` call with a different target string:

```python
# Codex / OpenClaw -- appends to AGENTS.md
export_agent(agent, target="codex", output_dir="./exports")

# Codex project config -- merge into .codex/config.toml
export_agent(agent, target="codex-config", output_dir="./codex-configs")

# Google ADK / Gemini -- generates YAML config
export_agent(agent, target="gemini", output_dir="./adk-agents")

# ChatGPT Custom GPTs -- generates system instructions
export_agent(agent, target="chatgpt", output_dir="./gpt-exports")
```

CLI equivalents:

```bash
multiagent export code/code-reviewer a2a-agent-card -o ./agent-cards
multiagent export code/code-reviewer codex >> AGENTS.md
mkdir -p .codex
multiagent export code/code-reviewer codex-config > .codex/config.toml
multiagent export code/code-reviewer gemini -o ./adk-agents
multiagent export code/code-reviewer chatgpt
```

## Route before exporting

Use the router to choose agents first, then ask for a target-specific export
plan:

```bash
multiagent route "review this PR and write missing tests" --target a2a-agent-card
multiagent route "review this PR and write missing tests" --target codex-config --json
```

## Bulk export for a whole category

Export every agent in the `code` category to Claude Code in one command:

```bash
multiagent export-all claude-code -o .claude/agents -c code
```

In Python:

```python
from multiagent import Catalog, export_agent

catalog = Catalog()
for agent in catalog.by_category("code"):
    export_agent(agent, target="claude-code", output_dir=".claude/agents")
```

## Using raw export with Ollama

The `raw` target gives you just the system prompt, ready for any LLM:

```python
from multiagent import Catalog, export_agent

catalog = Catalog()
agent = catalog.load("code/code-reviewer")
prompt = export_agent(agent, target="raw")

# Use with Ollama via its Python client
import ollama
response = ollama.chat(
    model="gemma4:27b",
    messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": "Review this function:\n\ndef add(a, b): return a - b"},
    ],
)
print(response["message"]["content"])
```

## Enhance before exporting

Combine enhancements with export for the best results:

```python
from multiagent import Catalog, enhance_agent, export_agent

catalog = Catalog()
agent = catalog.load("code/code-reviewer")
smart = enhance_agent(agent, profile="all")
export_agent(smart, target="claude-code", output_dir=".claude/agents")
```

One-liner from the CLI:

```bash
multiagent enhance code/code-reviewer -p all -t claude-code -o .claude/agents
```

## Complete runnable script

```python
"""Export a code-reviewer agent to all supported targets."""

from multiagent import Catalog, export_agent, enhance_agent

catalog = Catalog()
agent = catalog.load("code/code-reviewer")
smart = enhance_agent(agent, profile="all")

targets = ["a2a-agent-card", "claude-code", "agentskill", "codex", "codex-config", "gemini", "chatgpt", "raw"]

for target in targets:
    content = export_agent(smart, target=target)
    lines = content.strip().splitlines()
    print(f"\n--- {target} ({len(content)} chars, {len(lines)} lines) ---")
    print("\n".join(lines[:5]) + "\n...")
```

## Next steps

Want to cut your agent costs by 80%? Continue with
[06 -- Cost Optimization](06-cost-optimization.md).
