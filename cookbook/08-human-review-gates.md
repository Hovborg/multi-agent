# Human Review Gates

Use this recipe when a route dry-run may lead to external side effects: calendar
events, email drafts, infrastructure changes, CI/CD deployments, or financial
decisions.

`multi-agent` does not execute agents from `route`. It returns a decision object
that you can inspect before handing work to Codex, OpenClaw, Claude Code, or a
framework runtime.

## Check the route first

```bash
multiagent route "Schedule a meeting with the project team next week" --json
```

The JSON includes:

```json
{
  "risk": {
    "side_effect_risk": "medium",
    "requires_human_review": true
  },
  "context": {
    "loading": "trigger",
    "estimated_context_tokens": 4096,
    "context_size_risk": "low"
  }
}
```

## Gate side effects

Treat these values as policy inputs:

| Field | Gate |
|-------|------|
| `risk.requires_human_review == true` | Show the plan to the user before execution |
| `risk.side_effect_risk in ["medium", "high"]` | Require explicit approval |
| `context.context_size_risk == "high"` | Prefer progressive loading or summarization |
| `context.loading == "always"` | Check whether the full context is really needed |

## Example policy

```python
from multiagent import Catalog
from multiagent.router import AgentRouter

router = AgentRouter(Catalog())
route = router.recommend("Provision Terraform infrastructure for production")

if route.risk["requires_human_review"]:
    raise RuntimeError("Human approval required before execution")

if route.context["context_size_risk"] == "high":
    raise RuntimeError("Summarize or load context progressively first")
```

## OpenClaw/Codex workflow

1. Run `multiagent route ... --json`.
2. If `requires_human_review` is true, present the plan and wait for approval.
3. If approved, export the agent or framework plan:

```bash
multiagent route "Provision Terraform infrastructure" --target openai-agents --json
multiagent export devops/infra-provisioner codex-config
```

4. Execute only after the owning runtime applies its own tool permission and
   approval gates.
