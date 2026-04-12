# Parallel Fan-Out Pattern

**Multiple agents work simultaneously on independent tasks, and results are merged at the end.**

Like sending three researchers to different libraries at the same time. Each works independently, and you combine their findings when they all return. Latency equals the slowest agent, not the sum.

## When to Use

- Subtasks are independent and require no communication between agents
- Latency matters more than cost (all agents run concurrently)
- You want multiple perspectives on the same input (e.g., different review aspects)
- The merge step is straightforward (concatenation, voting, or simple aggregation)
- Each subtask is roughly similar in complexity and duration

## When NOT to Use

- Tasks depend on each other's outputs -- use Sequential or DAG instead
- You need agents to collaborate or debate -- use Group Chat
- A central coordinator should dynamically decide which tasks to run -- use Supervisor-Worker
- The merge logic is complex and requires intelligent synthesis -- add a supervisor for the merge step
- Cost is the primary concern (parallel runs all agents regardless of necessity)

## Architecture Diagram

```
                    ┌─────────────────┐
                    │   Input / Task   │
                    └────────┬────────┘
               ┌─────────────┼─────────────┐
               ▼             ▼             ▼
        ┌────────────┐ ┌────────────┐ ┌────────────┐
        │  Agent A    │ │  Agent B    │ │  Agent C    │
        │  Security   │ │Performance │ │  Style      │
        │  Review     │ │  Review    │ │  Review     │
        └──────┬─────┘ └─────┬──────┘ └──────┬─────┘
               │             │               │
               └─────────────┼───────────────┘
                             ▼
                    ┌─────────────────┐
                    │   Merge / Reduce │
                    └─────────────────┘
```

## How It Works

1. **Fan-Out** -- The input task is sent to all agents simultaneously.
2. **Parallel Execution** -- Each agent processes the task independently using `asyncio.gather` or thread pools.
3. **Collection** -- Results are collected as each agent finishes (with optional timeout).
4. **Merge** -- A merge strategy combines the results:
   - `concatenate` -- Join all outputs in order
   - `vote` -- Majority vote for classification tasks
   - `rank` -- Score and rank outputs
   - `agent` -- A dedicated merge agent synthesizes results
5. **Output** -- The merged result is returned.

## Configuration Example

```yaml
pattern: parallel
name: multi-aspect-review

agents:
  - agent: code/security-auditor
    model: claude-haiku-4-5
    focus: "Security vulnerabilities and OWASP Top 10"

  - agent: code/code-reviewer
    model: claude-haiku-4-5
    focus: "Logic errors, edge cases, and bugs"

  - agent: code/refactorer
    model: claude-haiku-4-5
    focus: "Code quality, DRY violations, and readability"

merge_strategy: agent          # Use a merge agent to synthesize
merge_agent: code/pr-summarizer
merge_model: claude-sonnet-4-6

timeout_seconds: 30            # Max wait per agent
fail_strategy: partial         # Return available results if some agents fail

cost_profile:
  estimated_per_run:
    claude-haiku-4-5: 0.009    # 3 agents at ~$0.003 each
    claude-sonnet-4-6: 0.075   # 3 agents at ~$0.025 each
```

## Code Example

```python
from multiagent import Catalog, patterns

catalog = Catalog()

# Define parallel agents
team = patterns.parallel(
    agents=[
        catalog.load("code/security-auditor"),
        catalog.load("code/code-reviewer"),
        catalog.load("code/refactorer"),
    ],
    merge_strategy="agent",
    merge_agent=catalog.load("code/pr-summarizer"),
    timeout=30,
    model="claude-haiku-4-5",
)

# Run -- all agents execute concurrently
result = team.run(
    "Review this pull request",
    context={"diff": open("changes.diff").read()},
)

# Access individual results
for agent_result in result.agent_outputs:
    print(f"{agent_result.agent_name}: {agent_result.findings_count} findings")

# Access merged output
print(result.merged_output)
print(f"Wall time: {result.wall_time:.1f}s (vs {result.sequential_time:.1f}s sequential)")
```

## Real-World Examples

- **Multi-Aspect Code Review** -- Security, performance, and style reviewers analyze the same diff simultaneously. A summarizer merges findings into a single PR comment.
- **Multi-Source Research** -- Three researchers query different sources (web, academic papers, internal docs) for the same question. Results are deduplicated and ranked.
- **Translation Comparison** -- Three translators produce independent translations of the same text. A quality agent selects the best or merges the strongest parts of each.
- **Competitive Analysis** -- Agents analyze competitor pricing, features, and reviews in parallel. An analyst merges findings into a competitive matrix.
- **Parallel Test Generation** -- Unit test, integration test, and edge-case test generators run simultaneously against new code.

## Pros and Cons

| Pros | Cons |
|------|------|
| Lowest latency (wall time = slowest agent) | Highest cost (all agents always run) |
| No dependencies between agents | No communication between agents during execution |
| Easy to add more parallel agents | Merge step can lose nuance from individual results |
| Partial results if some agents fail | Duplicate work if agents overlap in scope |
| Embarrassingly parallelizable | Requires careful task decomposition to avoid overlap |
| Simple to implement and reason about | Results quality depends heavily on merge strategy |

## Cost Implications

- **Cost = N x single agent**: Every agent runs every time, so cost scales linearly with the number of parallel agents. Three Haiku agents cost ~$0.009 vs $0.003 for one.
- **Merge agent adds overhead**: If using an agent-based merge strategy, add one more LLM call. Use a stronger model for merging (Sonnet) and cheaper models for workers (Haiku).
- **No dynamic routing**: Unlike Supervisor-Worker, you cannot skip unnecessary agents. Every fan-out agent always executes.
- **Timeout savings**: Setting aggressive timeouts prevents slow agents from dominating cost. Partial results are often acceptable.
- **Best for latency-critical paths**: When time-to-response matters more than per-request cost, parallel is optimal.
- **Typical cost range**: $0.005-0.03 per run with Haiku, $0.05-0.15 with Sonnet, plus merge agent cost.
