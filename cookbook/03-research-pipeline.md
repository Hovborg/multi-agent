# Build a Research Pipeline with Fact-Checking

**Difficulty:** Medium

## What you'll build

A multi-source research pipeline where three researcher agents work in parallel,
and a fact-checker verifies the merged results. You will also export the pipeline
to LangGraph and learn cost optimization tips.

## Prerequisites

- Python 3.10+
- `pip install multi-agent`
- Completed [01 -- Getting Started](01-getting-started.md)
- Optional: `pip install multi-agent[langgraph]` for LangGraph export

## Step 1 -- Load research agents

```python
from multiagent import Catalog

catalog = Catalog()
researcher = catalog.load("research/deep-researcher")
fact_checker = catalog.load("research/fact-checker")

print(f"Researcher: {researcher.full_name} -- {researcher.description}")
print(f"Checker:    {fact_checker.full_name} -- {fact_checker.description}")
```

## Step 2 -- Use the parallel pattern for multi-source research

Fan out three copies of the researcher to investigate different angles at the
same time:

```python
from multiagent import patterns

# Phase 1: Three researchers work concurrently
research_phase = patterns.parallel(
    agents=[researcher, researcher, researcher],
    model="claude-haiku-4-5",
)

print(research_phase.describe())
```

## Step 3 -- Sequential pipeline for verification

Chain the parallel research phase into a sequential fact-checking step:

```python
verification_phase = patterns.sequential(
    steps=[researcher, fact_checker],
    model="claude-haiku-4-5",
)
print(verification_phase.describe())
```

The full data flow:

```
  [Researcher A] ──┐
  [Researcher B] ──┼──> [Merge] ──> [Fact Checker] ──> Final Report
  [Researcher C] ──┘
```

## Step 5 -- Export to LangGraph

```python
from multiagent.adapters import langgraph

config = langgraph.from_catalog(
    ["research/deep-researcher", "research/fact-checker"],
    flow="sequential",
)
# config contains node definitions, edges, and state schema
# ready to build a LangGraph StateGraph
```

Or export from the CLI:

```bash
multiagent export research/deep-researcher raw -o ./pipeline
multiagent export research/fact-checker raw -o ./pipeline
```

## Step 6 -- Cost comparison

```python
from multiagent import CostEstimator

# Full pipeline: 3 parallel researchers + 1 fact checker
all_agents = [researcher, researcher, researcher, fact_checker]

print(f"{'Model':<25} {'Cost':>10}  {'Tokens':>8}")
print("-" * 47)

for model in ["claude-haiku-4-5", "claude-sonnet-4-6", "gpt-4o-mini",
              "gemini-2.5-flash", "deepseek-v3", "gemma4-27b"]:
    est = CostEstimator.estimate_team(all_agents, model=model)
    e = est.estimates[0]
    cost = f"${e.cost_usd:.4f}" if e.cost_usd > 0 else "free"
    print(f"{model:<25} {cost:>10}  {e.total_tokens:>8}")
```

## Cost optimization tips

1. **Cheap models for research, expensive for verification.** Researchers on
   `gemini-2.5-flash`, fact-checker on `claude-sonnet-4-6`.
2. **Reduce redundant context.** Each researcher gets only its assigned angle.
3. **Cache intermediate results.** Same query daily? Cache research, re-run only
   the fact-checker.
4. **Local models for drafts.** `gemma4-27b` via Ollama costs nothing.

## Complete runnable script

```python
"""Research pipeline with parallel research and sequential fact-checking."""

from multiagent import Catalog, CostEstimator, patterns

catalog = Catalog()
researcher = catalog.load("research/deep-researcher")
fact_checker = catalog.load("research/fact-checker")

research_phase = patterns.parallel(agents=[researcher, researcher, researcher], model="gemini-2.5-flash")
verify_phase = patterns.sequential(steps=[researcher, fact_checker], model="claude-sonnet-4-6")

all_agents = [researcher, researcher, researcher, fact_checker]
print(CostEstimator.estimate_team(all_agents))
```

## Next steps

Want to make any agent significantly smarter with zero code changes? Continue
with [04 -- Smart Enhancements](04-smart-enhancements.md).
