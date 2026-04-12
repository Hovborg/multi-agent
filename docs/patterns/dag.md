# DAG (Directed Acyclic Graph) Pattern

**Tasks flow through a graph of nodes with conditional edges, enabling branching, merging, and complex workflows.**

Like a CI/CD pipeline: build runs first, then tests and linting run in parallel, then deployment -- but only if tests pass. Nodes are agents, edges are conditions. The graph has no cycles (acyclic), so execution always terminates.

## When to Use

- The workflow has conditional branching (if X then do A, else do B)
- Some tasks can run in parallel while others must wait for dependencies
- You need a complex workflow that combines sequential, parallel, and conditional logic
- The workflow is relatively stable and can be defined ahead of time
- You want fine-grained control over execution order and error handling

## When NOT to Use

- The workflow is a simple linear chain -- use Sequential (simpler)
- The workflow is purely parallel with no dependencies -- use Parallel (simpler)
- Routing decisions need to be made dynamically by an LLM -- use Supervisor-Worker
- The workflow needs cycles or iteration -- add a Reflection loop within a node
- The workflow changes frequently -- DAGs are rigid once defined

## Architecture Diagram

```
                    ┌───────────┐
                    │   Start    │
                    │  (Parse)   │
                    └─────┬─────┘
                          │
                    ┌─────▼─────┐
                    │ Classify   │
                    └──┬─────┬──┘
                       │     │
              ┌────────▼┐   ┌▼────────┐
              │ Branch A │   │ Branch B │
              │(Security)│   │(Feature) │
              └────┬─────┘   └──┬──────┘
                   │            │
              ┌────▼─────┐     │
              │ Deep Scan │     │
              │(if critical)   │
              └────┬─────┘     │
                   │            │
                   └──────┬─────┘
                          │
                    ┌─────▼─────┐
                    │   Merge    │
                    │ (Report)   │
                    └─────┬─────┘
                          │
                    ┌─────▼─────┐
                    │   Deploy?  │──── condition: tests_passed
                    └─────┬─────┘
                          │
                    ┌─────▼─────┐
                    │   Notify   │
                    └───────────┘
```

## How It Works

1. **Graph Definition** -- Define nodes (agents) and edges (dependencies + conditions) as a directed acyclic graph.
2. **Topological Sort** -- The execution engine determines the order based on dependencies.
3. **Entry Node** -- The first node (no incoming edges) executes with the initial input.
4. **Dependency Resolution** -- Each node waits for all its parent nodes to complete.
5. **Conditional Edges** -- Edges can have conditions. If a condition evaluates to false, that branch is skipped.
6. **Parallel Execution** -- Nodes at the same depth level with satisfied dependencies run concurrently.
7. **Merge Nodes** -- Nodes with multiple incoming edges receive combined results from all parent nodes.
8. **Completion** -- The terminal node (no outgoing edges) produces the final output.

## Configuration Example

```yaml
pattern: dag
name: ci-cd-pipeline

nodes:
  parse:
    agent: code/code-generator
    description: Parse and validate the incoming change
    model: claude-haiku-4-5

  classify:
    agent: orchestration/task-router
    description: Classify the change type
    model: claude-haiku-4-5
    depends_on: [parse]

  security_scan:
    agent: code/security-auditor
    description: Deep security analysis
    model: claude-sonnet-4-6
    depends_on: [classify]
    condition: "classification in ['security', 'auth', 'payments']"

  code_review:
    agent: code/code-reviewer
    description: General code quality review
    model: claude-haiku-4-5
    depends_on: [classify]

  test_generation:
    agent: code/test-writer
    description: Generate tests for changed code
    model: claude-sonnet-4-6
    depends_on: [classify]

  merge_report:
    agent: code/pr-summarizer
    description: Combine all findings into a report
    model: claude-sonnet-4-6
    depends_on: [security_scan, code_review, test_generation]
    merge_strategy: concatenate

  deploy_check:
    agent: devops/ci-cd-agent
    description: Decide if safe to deploy
    model: claude-haiku-4-5
    depends_on: [merge_report]
    condition: "all_checks_passed == true"

error_handling:
  node_failure: skip_dependents  # or fail_fast, retry
  max_retries: 1
```

## Code Example

```python
from multiagent import Catalog, patterns

catalog = Catalog()

# Define the DAG
dag = patterns.dag(
    nodes={
        "parse": {
            "agent": catalog.load("code/code-generator"),
            "model": "claude-haiku-4-5",
        },
        "classify": {
            "agent": catalog.load("orchestration/task-router"),
            "model": "claude-haiku-4-5",
            "depends_on": ["parse"],
        },
        "security": {
            "agent": catalog.load("code/security-auditor"),
            "model": "claude-sonnet-4-6",
            "depends_on": ["classify"],
            "condition": lambda ctx: ctx["classification"] in ["security", "auth"],
        },
        "review": {
            "agent": catalog.load("code/code-reviewer"),
            "model": "claude-haiku-4-5",
            "depends_on": ["classify"],
        },
        "tests": {
            "agent": catalog.load("code/test-writer"),
            "model": "claude-sonnet-4-6",
            "depends_on": ["classify"],
        },
        "report": {
            "agent": catalog.load("code/pr-summarizer"),
            "model": "claude-sonnet-4-6",
            "depends_on": ["security", "review", "tests"],
        },
    },
)

# Run the DAG
result = dag.run(
    "Analyze this pull request",
    context={"diff": open("changes.diff").read()},
)

# Inspect execution
for node_name, node_result in result.node_outputs.items():
    status = "SKIPPED" if node_result.skipped else "DONE"
    print(f"  {node_name}: {status} ({node_result.duration:.1f}s, ${node_result.cost:.4f})")

print(f"\nExecution path: {' -> '.join(result.execution_path)}")
print(f"Skipped nodes: {result.skipped_nodes}")
print(f"Total cost: ${result.total_cost:.4f}")
print(f"Wall time: {result.wall_time:.1f}s")
```

## Real-World Examples

- **CI/CD Pipeline** -- Parse change, classify type, run linting + tests + security scan in parallel, merge results, conditionally deploy if all checks pass.
- **Complex Decision Workflow** -- Intake form is parsed, risk is assessed, and the request branches to different approval chains based on risk level. All chains merge at a final approval node.
- **Data Pipeline** -- Extract from multiple sources (parallel), transform with different logic per source type (conditional), load into staging, validate, then load into production.
- **Incident Response** -- Detect anomaly, classify severity, branch to automated remediation (low) or human escalation (high), in both cases generate a post-incident report.
- **Document Processing** -- Parse document, extract entities and classify, branch to different validation workflows per document type, merge into a unified output schema.

## Pros and Cons

| Pros | Cons |
|------|------|
| Maximum flexibility for complex workflows | Most complex pattern to define and debug |
| Conditional branches skip unnecessary work | DAG definition is rigid -- changes require redefinition |
| Parallel execution where dependencies allow | Condition logic can become hard to maintain |
| Clear dependency tracking and execution order | Overkill for simple linear or parallel workflows |
| Fine-grained error handling per node | Merge nodes must handle variable inputs (some skipped) |
| Deterministic execution for same conditions | Testing requires covering all branch combinations |

## Cost Implications

- **Conditional branches save money**: Unlike Parallel, the DAG only executes branches whose conditions are met. A security scan that only runs for auth-related changes saves the cost of running it on every PR.
- **Parallel nodes reduce latency**: Nodes at the same depth level run concurrently, so wall time is less than the sum of all nodes.
- **Cheap classifiers, expensive specialists**: Use Haiku for routing/classification nodes and Sonnet for specialist nodes. The classifier decides which expensive nodes actually run.
- **Error handling affects cost**: `skip_dependents` on failure saves cost by not running downstream nodes. `retry` doubles the cost of the failed node.
- **Graph complexity**: More nodes means higher potential cost, but conditional edges keep actual cost below the theoretical maximum.
- **Typical cost range**: $0.01-0.15 per run depending on which branches execute. Best-case (simple path) can be very cheap; worst-case (all branches) approaches Parallel cost.
