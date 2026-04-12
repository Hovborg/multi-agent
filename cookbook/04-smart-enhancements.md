# Make Any Agent 40% Smarter

**Difficulty:** Easy

## What you'll build

You will take a plain agent definition and boost its performance by applying
research-backed prompt engineering blocks. No code changes to the agent
itself -- enhancements are appended to the system prompt automatically.

## Prerequisites

- Python 3.10+
- `pip install multi-agent`
- Completed [01 -- Getting Started](01-getting-started.md)

## How enhancements work

Every agent in the catalog has a `system_prompt`. The `enhance_agent` function
loads YAML enhancement blocks from `catalog/_enhancements/` and appends them to
the prompt. The original agent is never modified -- a new copy is returned.

```
Original prompt  +  Enhancement blocks  =  Enhanced prompt
(~200 chars)        (~800 chars total)      (~1000 chars)
```

## The 8 enhancement blocks explained

| Block | What it does | Impact |
|-------|-------------|--------|
| `reasoning` | Adds plan-and-reflect thinking steps | +20% task completion (SWE-bench) |
| `error_recovery` | 5-level retry hierarchy (reread, retry, fallback, skip, escalate) | Fewer stuck agents |
| `verification` | Self-check checklist before returning output | Catches mistakes before the user sees them |
| `confidence` | Forces the agent to state confidence levels | Reduces hallucination 40-60% |
| `tool_discipline` | Rules for when and how to use tools | Faster execution, fewer tool errors |
| `failure_modes` | Avoids 6 common anti-patterns (yolo mode, infinite loops, etc.) | Prevents the most frequent agent failures |
| `context_management` | Strategies for long-running tasks and large context | Better performance on complex tasks |
| `information_priority` | Prioritize tool output and facts over training data | Grounded, factual responses |

## Category profiles

Each catalog category has a default enhancement profile tuned for its use case:

| Category | Default blocks |
|----------|---------------|
| `code` | reasoning, error_recovery, verification, tool_discipline, failure_modes |
| `research` | reasoning, confidence, information_priority, verification, context_management |
| `data` | reasoning, verification, confidence, tool_discipline |
| `finance` | reasoning, confidence, verification, information_priority, failure_modes |
| `legal` | reasoning, confidence, verification, information_priority, failure_modes |

## Applying enhancements

### Use the category default

```python
from multiagent import Catalog, enhance_agent

catalog = Catalog()
agent = catalog.load("code/code-reviewer")
smart = enhance_agent(agent, profile="category")  # uses code profile
```

### Apply all 8 blocks

```python
smart = enhance_agent(agent, profile="all")
```

### Minimal (just reasoning + verification)

```python
smart = enhance_agent(agent, profile="minimal")
```

### Custom combination

Pick exactly the blocks you want:

```python
smart = enhance_agent(agent, enhancements=["reasoning", "confidence", "verification"])
```

## Before/after comparison

```python
from multiagent import Catalog, enhance_agent

catalog = Catalog()
agent = catalog.load("code/code-reviewer")

print(f"BEFORE ({len(agent.system_prompt)} chars):")
print(agent.system_prompt[:200] + "...")

smart = enhance_agent(agent, profile="all")

print(f"\nAFTER ({len(smart.system_prompt)} chars):")
print(smart.system_prompt[:200] + "...")
print(f"\nAdded {len(smart.system_prompt) - len(agent.system_prompt)} chars of enhancements")
```

## When to use which profile

| Situation | Recommended profile |
|-----------|-------------------|
| Quick prototyping | `"minimal"` -- fast, low token overhead |
| Production agents in their home category | `"category"` -- tuned defaults |
| Mission-critical or high-stakes tasks | `"all"` -- maximum reliability |
| You know exactly what you need | Custom list via `enhancements=[...]` |
| Cost-constrained, model is already strong | `"none"` -- skip enhancements |

## Complete runnable script

```python
"""Demonstrate smart enhancements on a code reviewer agent."""

from multiagent import Catalog, enhance_agent
from multiagent.enhance import CATEGORY_PROFILES, ALL_ENHANCEMENTS

catalog = Catalog()
agent = catalog.load("code/code-reviewer")

# Show available enhancements
print("All enhancement blocks:")
for name in ALL_ENHANCEMENTS:
    print(f"  - {name}")

# Show category profile
print(f"\nDefault profile for '{agent.category}': {CATEGORY_PROFILES[agent.category]}")

# Apply and compare
for profile in ["none", "minimal", "category", "all"]:
    enhanced = enhance_agent(agent, profile=profile)
    print(f"\n  {profile:10} -> {len(enhanced.system_prompt):>5} chars")
```

## Next steps

Ready to use your agents on Claude Code, Codex, Gemini, or ChatGPT? Continue
with [05 -- Export Everywhere](05-export-everywhere.md).
