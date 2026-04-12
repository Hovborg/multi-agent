# Cut Agent Costs by 80%

**Difficulty:** Advanced

## What you'll build

A cost-optimized multi-agent pipeline that uses expensive models only where
quality matters and cheap or free models everywhere else. You will learn the
cost model, model routing strategies, and monthly budget planning.

## Prerequisites

- Python 3.10+
- `pip install multi-agent`
- Completed [01 -- Getting Started](01-getting-started.md) and
  [02 -- Build a Code Review Team](02-build-code-review-team.md)

## Understanding the cost model

Every agent has a `cost_profile` with estimated token counts per run. The
`CostEstimator` combines those with real pricing for 13 models. Local models
like `gemma4-27b` show as free.

```python
from multiagent import Catalog, CostEstimator

catalog = Catalog()
agent = catalog.load("code/code-reviewer")
print(CostEstimator.estimate_agent(agent, extra_input_tokens=5000))
```

## Model routing strategy

The key insight: **not every step in your pipeline needs the best model.**

| Task type | Recommended tier | Example models |
|-----------|-----------------|----------------|
| Final review, verification, legal | Quality | claude-sonnet-4-6, gpt-4o, o3 |
| General work, coding, analysis | Balanced | claude-haiku-4-5, gpt-4o-mini |
| Bulk research, drafts, summaries | Budget | gemini-2.5-flash, deepseek-v3 |
| Prototyping, local dev, unlimited | Free | gemma4-27b, nemotron-cascade-2 |

## Per-step model assignment in pipelines

Assign different models to different agents in the same pipeline:

```python
from multiagent import Catalog, patterns

catalog = Catalog()
researcher = catalog.load("research/deep-researcher")
fact_checker = catalog.load("research/fact-checker")

# Phase 1: Cheap parallel research
research = patterns.parallel(
    agents=[researcher, researcher, researcher],
    model="gemini-2.5-flash",  # $0.15/M input -- budget tier
)

# Phase 2: Quality verification
verify = patterns.sequential(
    steps=[fact_checker],
    model="claude-sonnet-4-6",  # $3.00/M input -- quality tier
)
```

## Using local models for free

With Ollama running locally, the `raw` export gives you a ready-to-use system
prompt at zero cost:

```python
from multiagent import Catalog, export_agent

catalog = Catalog()
agent = catalog.load("code/code-reviewer")
prompt = export_agent(agent, target="raw")

# Use with any local model
import ollama
response = ollama.chat(
    model="gemma4:27b",
    messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": "Review this diff:\n+ return a - b"},
    ],
)
```

## Monthly budget planning

Use the estimator to forecast monthly spend:

```python
from multiagent import Catalog, CostEstimator

catalog = Catalog()
team = catalog.load_team([
    "code/code-reviewer", "code/test-writer", "code/security-auditor"
])

runs_per_day = 20
days_per_month = 22  # working days

for model in ["claude-haiku-4-5", "claude-sonnet-4-6", "gpt-4o-mini"]:
    est = CostEstimator.estimate_team(team, model=model, extra_input_tokens=5000)
    cost_per_run = est.estimates[0].cost_usd
    monthly = cost_per_run * runs_per_day * days_per_month
    print(f"{model:<25} ${cost_per_run:.4f}/run  ${monthly:.2f}/month")
```

## The 80% savings recipe

1. **Identify quality-critical steps.** Usually the final review or verification.
   Run these on `claude-sonnet-4-6` or `gpt-4o`.

2. **Move bulk work to budget models.** Research, drafting, test generation run
   fine on `gpt-4o-mini` or `gemini-2.5-flash`.

3. **Use local models for iteration.** During development, run everything on
   `gemma4-27b`. Switch to paid models for production.

4. **Cache aggressively.** If an agent produces the same output for the same
   input, cache it. Re-running costs money.

5. **Right-size token budgets.** Lower `max_tokens` on agents that produce short
   outputs.

## Complete runnable script

```python
"""Compare costs: naive vs. optimized model routing."""

from multiagent import Catalog, CostEstimator

catalog = Catalog()
team = catalog.load_team(["code/code-reviewer", "code/test-writer", "code/security-auditor"])

for label, model in [("Sonnet", "claude-sonnet-4-6"), ("Haiku", "claude-haiku-4-5"),
                     ("GPT-4o-mini", "gpt-4o-mini"), ("Gemini Flash", "gemini-2.5-flash"),
                     ("Local Gemma4", "gemma4-27b")]:
    est = CostEstimator.estimate_team(team, model=model, extra_input_tokens=5000)
    per_run = est.estimates[0].cost_usd
    monthly = per_run * 20 * 22
    print(f"{label:<15} ${per_run:.4f}/run  ${monthly:.2f}/month")
```

## Next steps

You have completed the cookbook. Here are some directions to explore:

- Browse the full [Agent Catalog](../catalog/) for all 50+ agent definitions
- Read the [Pattern Documentation](../docs/patterns/) for advanced orchestration
- Check the [Framework Adapters](../docs/frameworks/) for CrewAI, LangGraph, and more
- Try the [Interactive Playground](../web/index.html) to build teams visually
- Contribute your own agents via [CONTRIBUTING.md](../CONTRIBUTING.md)
