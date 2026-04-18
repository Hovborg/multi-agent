# Build an Automated Code Review Team

**Difficulty:** Medium

## What you'll build

A three-agent code review team using the supervisor-worker pattern. The code
reviewer supervises a test writer and a security auditor, all enhanced with smart
prompts and exported to Claude Code.

## Prerequisites

- Python 3.10+
- `pip install multi-agent`
- Completed [01 -- Getting Started](01-getting-started.md)

## Step 1 -- Load the agents

```python
from multiagent import Catalog

catalog = Catalog()
reviewer = catalog.load("code/code-reviewer")
test_writer = catalog.load("code/test-writer")
security_auditor = catalog.load("code/security-auditor")

print(f"Supervisor: {reviewer.full_name}")
print(f"Workers:    {test_writer.full_name}, {security_auditor.full_name}")
```

## Step 2 -- Compose with supervisor-worker pattern

The supervisor decomposes the task and delegates subtasks to workers:

```python
from multiagent import patterns

team = patterns.supervisor_worker(
    supervisor=reviewer,
    workers=[test_writer, security_auditor],
    model="claude-haiku-4-5",
)

print(team.describe())
```

## Step 3 -- Enhance with smart prompts

Make each agent smarter with research-backed prompt engineering:

```python
from multiagent import enhance_agent

smart_reviewer = enhance_agent(reviewer, profile="all")
smart_test_writer = enhance_agent(test_writer, profile="category")
smart_auditor = enhance_agent(security_auditor, profile="category")

print(f"Original prompt: {len(reviewer.system_prompt)} chars")
print(f"Enhanced prompt: {len(smart_reviewer.system_prompt)} chars")
```

## Step 4 -- Export to Claude Code

Generate Claude Code subagent files:

```python
from multiagent import export_agent

for agent in [smart_reviewer, smart_test_writer, smart_auditor]:
    output = export_agent(agent, target="claude-code", output_dir=".claude/agents")
    print(f"Exported: {agent.name}.md")
```

This creates files in `.claude/agents/` that Claude Code can use as project subagents.

## Step 5 -- Visualize the team

Auto-generate a Mermaid diagram for documentation or README files:

```python
from multiagent.visualize import visualize_team

diagram = visualize_team(
    [reviewer, test_writer, security_auditor],
    pattern="supervisor-worker",
)
print(diagram)
```

## Step 6 -- Cost comparison across models

```python
from multiagent import CostEstimator

agents = [reviewer, test_writer, security_auditor]

print(f"{'Model':<25} {'Cost':>10}  {'Tokens':>8}")
print("-" * 47)

for model in ["claude-haiku-4-5", "claude-sonnet-4-6", "gpt-4o", "gpt-4o-mini",
              "gemini-2.5-flash", "gemma4-27b"]:
    est = CostEstimator.estimate_team(agents, model=model, extra_input_tokens=5000)
    e = est.estimates[0]
    cost = f"${e.cost_usd:.4f}" if e.cost_usd > 0 else "free"
    print(f"{model:<25} {cost:>10}  {e.total_tokens:>8}")
```

## Complete runnable script

```python
"""Build a code review team with smart enhancements."""

from multiagent import Catalog, CostEstimator, enhance_agent, export_agent, patterns
from multiagent.visualize import visualize_team

catalog = Catalog()
reviewer = catalog.load("code/code-reviewer")
test_writer = catalog.load("code/test-writer")
security_auditor = catalog.load("code/security-auditor")

# Enhance, compose, export, visualize, estimate -- all in one script
smart_reviewer = enhance_agent(reviewer, profile="all")
smart_test_writer = enhance_agent(test_writer, profile="category")
smart_auditor = enhance_agent(security_auditor, profile="category")

team = patterns.supervisor_worker(
    supervisor=smart_reviewer, workers=[smart_test_writer, smart_auditor],
    model="claude-haiku-4-5",
)
print(team.describe())

for agent in [smart_reviewer, smart_test_writer, smart_auditor]:
    export_agent(agent, target="claude-code", output_dir=".claude/agents")

print("\n" + visualize_team([reviewer, test_writer, security_auditor], pattern="supervisor-worker"))
print("\n" + str(CostEstimator.estimate_team([reviewer, test_writer, security_auditor], extra_input_tokens=5000)))
```

## Next steps

Want to build a research pipeline with parallel agents? Continue with
[03 -- Research Pipeline](03-research-pipeline.md).
