# 09 — Safe Delegation Policy

`multiagent route` selects agents and emits a dry-run policy. It does not call a
model, run a tool, or perform a side effect.

```bash
multiagent route "research and compare current agent frameworks" --json
```

The `policy` object provides:

- `control_mode`: `router`, `manager`, or `handoff`;
- `parallelizable`: whether independent workers may run concurrently;
- `max_delegates`: a hard fan-out bound between zero and five;
- `delegation_contract`: the objective, output, tool, source, and stop fields a
  downstream runtime must provide;
- `trust_boundary`: inputs and outputs that remain untrusted;
- `approval_required`: whether selected capabilities require human approval;
- `stop_conditions`: evidence, context, delegation-budget, and review gates.

## Runtime integration rules

1. Use a router for deterministic categories and a manager when one agent must
   synthesize specialist results.
2. Use a handoff only when the specialist should own the next interaction.
3. Parallelize only independent work and never exceed `max_delegates`.
4. Pass the smallest sufficient context. Return structured findings rather than
   full worker transcripts.
5. Treat delegated output like tool output: validate it before trusting or
   executing anything derived from it.
6. Pause before external side effects whenever `approval_required` is true.
7. Stop when evidence is sufficient, a budget is exhausted, or policy requires
   human review.

Validate the catalog and policy regression corpus in CI:

```bash
multiagent validate
multiagent eval-routing \
  --min-agent-score 1.0 \
  --min-pattern-score 1.0 \
  --min-target-score 0.95 \
  --min-forbidden-score 1.0 \
  --min-risk-score 1.0 \
  --min-context-score 1.0 \
  --min-policy-score 1.0
```
