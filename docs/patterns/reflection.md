# Reflection Pattern

**An iterative loop where an agent produces output, a critic reviews it, and the agent refines until a quality threshold is met.**

Like a writer and editor working in rounds. The writer drafts, the editor marks issues, the writer revises. This continues until the editor approves or a maximum number of rounds is reached.

## When to Use

- Output quality is critical and a single pass is rarely good enough
- You can define clear quality criteria that a critic can evaluate
- The task benefits from iterative refinement (writing, code generation, design)
- You want to catch and correct errors before delivering the final output
- The cost of a bad output exceeds the cost of extra LLM calls

## When NOT to Use

- The task is simple enough to get right in one pass (wasteful iteration)
- You cannot define measurable quality criteria for the critic
- Latency is critical -- each round adds a full LLM call cycle
- The generator and critic have identical blind spots (they will agree on wrong answers)
- Budget is tight -- reflection doubles or triples the cost of a single call

## Architecture Diagram

```
    ┌────────────────────────────────────────────┐
    │              Reflection Loop                │
    │                                            │
    │   ┌──────────┐    feedback    ┌──────────┐ │
    │   │          │◄──────────────│          │ │
    │   │ Generator │               │  Critic   │ │
    │   │          │──────────────▶│          │ │
    │   └──────────┘    output      └──────────┘ │
    │        │                           │       │
    │        │    Round 1, 2, 3...       │       │
    │        │                     ┌─────┘       │
    │        │                     │ approved?    │
    │        ▼                     ▼              │
    │   ┌─────────────────────────────┐          │
    │   │  Quality threshold met OR   │          │
    │   │  max rounds reached         │          │
    │   └─────────────────────────────┘          │
    └────────────────────────────────────────────┘
                       │
                       ▼
                  Final Output
```

## How It Works

1. **Initial Generation** -- The generator agent produces a first draft from the input task.
2. **Critique** -- The critic agent evaluates the output against defined quality criteria, producing structured feedback (pass/fail, issues list, score).
3. **Decision** -- If the critic approves (score above threshold) or max rounds are reached, the loop exits.
4. **Refinement** -- If not approved, the generator receives the critic's feedback and produces a revised version.
5. **Repeat** -- Steps 2-4 repeat until the exit condition is met.
6. **Output** -- The final approved version is returned, along with the full revision history.

## Configuration Example

```yaml
pattern: reflection
name: code-generator-with-review

generator:
  agent: code/code-generator
  model: claude-sonnet-4-6
  description: Generate implementation from requirements

critic:
  agent: code/code-reviewer
  model: claude-sonnet-4-6
  description: Review generated code for correctness and quality
  criteria:
    - "No bugs or logic errors"
    - "Handles edge cases"
    - "Follows project style guide"
    - "Has appropriate error handling"
  scoring: numeric       # 1-10 scale
  threshold: 8           # Minimum score to pass

max_rounds: 4
early_exit: true         # Stop as soon as threshold is met
include_history: true    # Pass full revision history to generator

cost_profile:
  estimated_per_run:
    best_case: 0.05      # 1 round (generator + critic)
    typical: 0.10        # 2 rounds
    worst_case: 0.20     # 4 rounds (max)
```

## Code Example

```python
from multiagent import Catalog, patterns

catalog = Catalog()

# Set up the reflection loop
loop = patterns.reflection(
    generator=catalog.load("code/code-generator"),
    critic=catalog.load("code/code-reviewer"),
    max_rounds=4,
    threshold=8,           # Score 1-10, exit when >= 8
    model="claude-sonnet-4-6",
)

# Run the reflection loop
result = loop.run(
    "Implement a thread-safe LRU cache with TTL support in Python",
    context={
        "language": "python",
        "style": "google",
        "requirements": [
            "Thread-safe with minimal lock contention",
            "TTL-based expiration",
            "O(1) get and put operations",
        ],
    },
)

# Inspect the refinement history
for round_info in result.rounds:
    print(f"Round {round_info.number}: score={round_info.score}/10")
    print(f"  Feedback: {round_info.feedback[:100]}...")

print(f"Final output accepted at round {result.accepted_round}")
print(f"Total cost: ${result.total_cost:.4f}")
print(result.final_output)
```

## Real-World Examples

- **Code Generation** -- A code generator writes an implementation, a reviewer checks for bugs, edge cases, and style. The generator fixes issues across 2-3 rounds until the reviewer scores it 8+/10.
- **Legal Document Drafting** -- A drafter produces contract language, a compliance critic checks for regulatory issues and ambiguity. Iterations continue until the document passes all compliance checks.
- **Creative Writing** -- A writer produces a story draft, a literary critic evaluates narrative structure, character consistency, and prose quality. Refinement focuses on the critic's specific feedback.
- **SQL Query Optimization** -- A query generator writes SQL, a performance critic analyzes the execution plan and flags full table scans or missing indexes. The generator rewrites until the query plan is acceptable.
- **API Design** -- A designer proposes an API schema, a critic evaluates for REST conventions, backward compatibility, and developer experience.

## Pros and Cons

| Pros | Cons |
|------|------|
| Significantly improves output quality | 2-4x cost of a single-pass approach |
| Catches errors before delivery | Adds latency proportional to number of rounds |
| Structured feedback drives targeted fixes | Generator and critic may share blind spots |
| Quality is measurable via critic scores | Diminishing returns after 2-3 rounds |
| Revision history is a useful audit trail | Critic must be well-calibrated to avoid false positives |
| Works with any generator/critic pair | Can loop indefinitely without good exit conditions |

## Cost Implications

- **Multiplicative cost**: Each round costs one generator call plus one critic call. A 3-round reflection costs 6 LLM calls vs. 1 for a single pass.
- **Early exit saves money**: Set `early_exit: true` so the loop stops as soon as quality is sufficient. Most tasks resolve in 2 rounds.
- **Model asymmetry**: Use the same model for both generator and critic, or use a cheaper model for the critic if it only needs to evaluate (not generate).
- **Max rounds as budget cap**: Setting `max_rounds` is effectively a cost ceiling. 4 rounds with Sonnet costs ~$0.20; set it based on your budget.
- **Diminishing returns**: Quality improvement per round drops sharply after round 2-3. Rarely worth going beyond 4 rounds.
- **Typical cost range**: $0.05-0.20 per run (2-4 rounds with Sonnet), $0.01-0.05 with Haiku.
