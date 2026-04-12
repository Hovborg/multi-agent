# Supervisor-Worker Pattern

**A central supervisor agent decomposes tasks and delegates to specialist worker agents.**

Think of a tech lead assigning Jira tickets to engineers. The supervisor understands the full picture, breaks work into pieces, routes each piece to the best-qualified worker, and synthesizes results.

## When to Use

- The task is complex and naturally decomposes into subtasks requiring different expertise
- You need dynamic routing -- the supervisor decides at runtime which workers to engage
- Quality control matters: the supervisor can validate worker outputs before aggregating
- Workers are specialized and interchangeable (you can add/remove workers without changing the flow)
- You want a single point of coordination and error handling

## When NOT to Use

- The task is simple enough for a single agent (over-engineering)
- All subtasks are identical -- use Parallel fan-out instead
- You need strict ordering between steps -- use Sequential pipeline instead
- The supervisor becomes a bottleneck because every decision must go through it
- You want fully autonomous agents that negotiate peer-to-peer -- use Group Chat

## Architecture Diagram

```
                     ┌─────────────────┐
                     │   Supervisor     │
                     │  (Tech Lead)     │
                     └────────┬────────┘
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
              ┌──────────┐ ┌──────┐ ┌──────────┐
              │ Worker A  │ │ W. B │ │ Worker C  │
              │(Reviewer) │ │(Test)│ │(Security) │
              └─────┬─────┘ └──┬───┘ └─────┬─────┘
                    │          │            │
                    └──────────┼────────────┘
                               ▼
                     ┌─────────────────┐
                     │   Supervisor     │
                     │ (Merge Results)  │
                     └─────────────────┘
```

## How It Works

1. **Task Intake** -- The supervisor receives the top-level task and full context.
2. **Decomposition** -- The supervisor analyzes the task and breaks it into discrete subtasks.
3. **Routing** -- Each subtask is assigned to the most appropriate worker based on its expertise tags.
4. **Execution** -- Workers execute their subtasks independently (may run in parallel or sequentially).
5. **Collection** -- The supervisor collects all worker outputs.
6. **Synthesis** -- The supervisor merges, deduplicates, and ranks the results into a coherent response.
7. **Quality Gate** -- Optionally, the supervisor reviews the merged result and may re-delegate if quality is insufficient.

## Configuration Example

```yaml
pattern: supervisor-worker
name: code-review-team

supervisor:
  agent: code/code-reviewer
  model: claude-sonnet-4-6
  strategy: dynamic          # supervisor decides which workers to invoke
  max_rounds: 3              # supervisor can re-delegate up to 3 times

workers:
  - agent: code/test-writer
    trigger: "missing_tests"
  - agent: code/security-auditor
    trigger: "security_concern"
  - agent: code/refactorer
    trigger: "code_smell"
  - agent: code/documentation-writer
    trigger: "missing_docs"

merge_strategy: supervisor   # supervisor synthesizes (vs. concatenate, vote)
parallel_workers: true       # workers run concurrently when possible

cost_profile:
  estimated_per_run:
    claude-haiku-4-5: 0.012
    claude-sonnet-4-6: 0.08
```

## Code Example

```python
from multiagent import Catalog, patterns

catalog = Catalog()

# Load agents from the catalog
supervisor = catalog.load("code/code-reviewer")
workers = [
    catalog.load("code/test-writer"),
    catalog.load("code/security-auditor"),
    catalog.load("code/refactorer"),
]

# Compose the team
team = patterns.supervisor_worker(
    supervisor=supervisor,
    workers=workers,
    model="claude-sonnet-4-6",
    parallel=True,
    max_rounds=3,
)

# Run
result = team.run(
    "Review this PR for bugs, security, and missing tests",
    context={"diff": open("changes.diff").read()},
)

print(result.summary)          # Supervisor's merged assessment
print(result.worker_outputs)   # Individual worker results
print(result.cost)             # Total cost breakdown
```

## Real-World Examples

- **Code Review Team** -- A senior reviewer delegates security auditing, test gap analysis, and style checks to specialist agents. The reviewer synthesizes a final PR comment.
- **Research with Specialists** -- A research coordinator sends sub-questions to a web researcher, a paper analyst, and a fact-checker. Results are merged into a comprehensive brief.
- **Customer Intake** -- A triage agent classifies incoming requests and routes them to billing, technical, or account specialists. Results flow back through the triage agent.
- **Data Pipeline QA** -- A data quality supervisor delegates schema validation, null-check analysis, and statistical outlier detection to purpose-built agents.

## Pros and Cons

| Pros | Cons |
|------|------|
| Central coordination prevents conflicting outputs | Supervisor is a single point of failure |
| Dynamic routing adapts to task complexity | Supervisor adds latency and cost (extra LLM call) |
| Easy to add/remove workers without changing flow | Supervisor quality caps the overall team quality |
| Built-in quality gate at the synthesis step | Complex tasks may overwhelm the supervisor's context |
| Workers are reusable across different teams | Workers cannot communicate directly with each other |

## Cost Implications

- **Supervisor overhead**: The supervisor makes at least 2 LLM calls (decompose + synthesize), adding 20-40% cost on top of worker costs.
- **Dynamic routing saves money**: Unlike parallel fan-out, the supervisor only invokes workers that are actually needed. A simple PR might only trigger the test-writer, skipping security and refactoring.
- **Model tiering**: Use a stronger model (Sonnet) for the supervisor and cheaper models (Haiku) for workers to optimize cost/quality.
- **Max rounds**: Setting `max_rounds` too high can cause cost spirals if the supervisor keeps re-delegating. Start with 2-3.
- **Typical cost range**: $0.01-0.10 per run with Haiku workers, $0.05-0.30 with Sonnet workers.
