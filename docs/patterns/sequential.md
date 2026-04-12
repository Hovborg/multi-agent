# Sequential Pipeline Pattern

**A linear chain where each agent transforms the output and passes it to the next.**

Like an assembly line: Agent A writes, Agent B edits, Agent C publishes. Each step takes the previous output as input and produces a refined or transformed version. The output of the final agent is the result.

## When to Use

- The task has clear, ordered stages where each stage depends on the previous output
- Each stage requires different expertise (writer vs. editor vs. translator)
- You want predictable, reproducible execution flow
- Quality improves by applying specialized transformations in sequence
- You need an audit trail of how the output evolved through each stage

## When NOT to Use

- Stages are independent and could run in parallel (wasted latency)
- You need iteration or feedback loops between stages -- use Reflection instead
- The number or order of stages changes dynamically -- use Supervisor-Worker or DAG
- A single stage failure should not block the entire pipeline (no built-in retry)
- The task does not naturally decompose into ordered steps

## Architecture Diagram

```
    ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
    │  Agent A  │────▶│  Agent B  │────▶│  Agent C  │────▶│  Agent D  │
    │  Writer   │     │  Editor   │     │ Translator│     │ Publisher │
    └──────────┘     └──────────┘     └──────────┘     └──────────┘
         │                │                │                │
      Draft v1        Draft v2          Draft v3         Final Output
```

## How It Works

1. **Input** -- The initial task and context enter the pipeline at Stage 1.
2. **Stage Execution** -- Each agent receives the output of the previous stage (plus optional shared context).
3. **Transformation** -- The agent applies its specialized skill (writing, editing, translating, etc.).
4. **Handoff** -- The agent's output becomes the input for the next stage.
5. **Completion** -- The final agent's output is returned as the pipeline result.
6. **Metadata** -- Each stage's input/output is logged for debugging and cost tracking.

## Configuration Example

```yaml
pattern: sequential
name: content-pipeline

stages:
  - agent: content/writer
    model: claude-sonnet-4-6
    description: Write initial draft from brief
    output_key: draft

  - agent: content/editor
    model: claude-sonnet-4-6
    description: Edit for clarity, grammar, and tone
    output_key: edited_draft

  - agent: content/seo-optimizer
    model: claude-haiku-4-5
    description: Optimize headings, meta, and keywords
    output_key: seo_draft

  - agent: content/translator
    model: claude-sonnet-4-6
    description: Translate to target language
    output_key: final
    parameters:
      target_language: da

shared_context:
  brand_voice: "Professional but approachable"
  max_length: 2000

error_handling: stop_on_failure  # or skip_stage, retry_stage
```

## Code Example

```python
from multiagent import Catalog, patterns

catalog = Catalog()

# Define the pipeline stages
pipeline = patterns.sequential(
    stages=[
        catalog.load("content/writer"),
        catalog.load("content/editor"),
        catalog.load("content/seo-optimizer"),
        catalog.load("content/translator"),
    ],
    model="claude-sonnet-4-6",
)

# Run the pipeline
result = pipeline.run(
    "Write a blog post about AI agent orchestration patterns",
    context={
        "brand_voice": "Professional but approachable",
        "target_language": "da",
    },
)

# Access each stage's output
for stage in result.stages:
    print(f"{stage.agent_name}: {len(stage.output)} chars, ${stage.cost:.4f}")

print(result.final_output)   # The translator's output
print(result.total_cost)     # Sum of all stages
```

## Real-World Examples

- **Content Pipeline** -- Writer drafts an article, editor polishes it, SEO optimizer adds keywords and meta descriptions, translator localizes it for a target market.
- **ETL (Extract-Transform-Load)** -- Data extractor pulls raw data, cleaner normalizes and deduplicates, transformer applies business logic, loader writes to the destination.
- **Code Generation** -- Requirements analyst produces a spec, code generator writes the implementation, test writer adds unit tests, documentation writer produces API docs.
- **Legal Document Pipeline** -- Drafter produces initial contract, compliance checker flags regulatory issues, editor rewrites flagged sections, formatter applies legal citation style.
- **Email Processing** -- Classifier categorizes the email, summarizer extracts key points, responder drafts a reply, tone checker ensures appropriate language.

## Pros and Cons

| Pros | Cons |
|------|------|
| Simple to understand and debug | High latency (stages run sequentially) |
| Clear audit trail at every stage | Single stage failure blocks the pipeline |
| Each agent is focused and specialized | No feedback loops (output only flows forward) |
| Easy to add, remove, or reorder stages | Cannot adapt dynamically to task complexity |
| Predictable cost (sum of all stages) | Earlier stages cannot benefit from later insights |
| Stages are independently testable | Context window may grow large in later stages |

## Cost Implications

- **Additive cost**: Total cost is the sum of all stage costs. A 4-stage pipeline with Sonnet costs roughly 4x a single agent call.
- **Model tiering per stage**: Use expensive models for creative/complex stages (writing) and cheap models for mechanical stages (SEO optimization, formatting).
- **Context growth**: Each stage passes its full output forward, so later stages process larger inputs. Consider summarizing between stages to control token usage.
- **Short-circuit optimization**: Add early exit conditions (e.g., if the editor finds no issues, skip SEO optimization) to reduce unnecessary calls.
- **Typical cost range**: $0.02-0.15 per run for a 3-4 stage pipeline with mixed models.
