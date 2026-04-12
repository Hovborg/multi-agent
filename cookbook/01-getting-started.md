# Your First Agent in 5 Minutes

**Difficulty:** Easy

## What you'll build

A complete script that browses the agent catalog, loads an agent, gets a
recommendation for your task, and estimates the cost -- all in under 20 lines of
Python.

## Prerequisites

- Python 3.10+
- `pip install multi-agent`

## Step 1 -- Install multi-agent

```bash
pip install multi-agent
```

Verify the install:

```bash
multiagent --help
```

You should see the CLI with commands like `search`, `info`, `list`, and
`recommend`.

## Step 2 -- Browse the catalog from the CLI

```bash
multiagent search "code review"
```

Output:

```
Found 3 agents matching "code review":

  code/code-reviewer     Review PRs for bugs, style, and security
  code/test-writer       Generate tests for changed code
  code/refactorer        Suggest and apply refactoring improvements
```

You can also list everything:

```bash
multiagent list            # all agents
multiagent list -c code    # just the code category
```

## Step 3 -- Load and inspect an agent in Python

```python
from multiagent import Catalog

catalog = Catalog()
print(f"Catalog has {len(catalog)} agents in {len(catalog.list_categories())} categories")

# Load a specific agent
reviewer = catalog.load("code/code-reviewer")
print(f"Name:        {reviewer.full_name}")
print(f"Description: {reviewer.description}")
print(f"Tags:        {reviewer.tags}")
print(f"Prompt size: {len(reviewer.system_prompt)} chars")
```

## Step 4 -- Get a recommendation

Describe your task in plain English and let the router pick the right agents and
orchestration pattern:

```python
from multiagent import Catalog, AgentRouter

catalog = Catalog()
router = AgentRouter(catalog)

rec = router.recommend("I need to review a PR and write missing tests")
print(rec.describe())
```

Output:

```
Recommended pattern: supervisor-worker
  Reason: Central reviewer coordinates specialists
  Confidence: 70%
  Agents:
    - code/code-reviewer: Reviews code changes for bugs, security, and style
    - code/test-writer: Generate tests for changed code
```

## Step 5 -- Estimate costs

```python
from multiagent import CostEstimator

estimate = CostEstimator.estimate_team(rec.agents, extra_input_tokens=5000)
print(estimate)
```

Output:

```
Cost estimate for: code/code-reviewer, code/test-writer
Model                      Tokens       Cost
---------------------------------------------
gemma4-27b                   9000 free (local)
claude-haiku-4-5             9000     $0.0232
gpt-4o-mini                  9000     $0.0041
claude-sonnet-4-6            9000     $0.0870
```

## Complete runnable script

Save this as `my_first_agent.py` and run it with `python my_first_agent.py`:

```python
"""My first multi-agent experience."""

from multiagent import Catalog, AgentRouter, CostEstimator

# 1. Browse the catalog
catalog = Catalog()
print(f"Loaded {len(catalog)} agents across {len(catalog.list_categories())} categories\n")

# 2. Search for agents
results = catalog.search("code review")
for agent in results:
    print(f"  {agent.full_name}: {agent.description}")

# 3. Get a recommendation
router = AgentRouter(catalog)
rec = router.recommend("I need to review a PR and write missing tests")
print(f"\n{rec.describe()}")

# 4. Estimate costs
if rec.agents:
    estimate = CostEstimator.estimate_team(rec.agents, extra_input_tokens=5000)
    print(f"\n{estimate}")
```

## Next steps

Ready to compose agents into a working team? Continue with
[02 -- Build a Code Review Team](02-build-code-review-team.md).
