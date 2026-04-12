# Handoff Pattern

**An agent transfers full control and context to another agent, like customer support escalation.**

The first agent handles the request as far as it can, then explicitly hands off to a more specialized or higher-tier agent. Unlike Supervisor-Worker, there is no return path -- the receiving agent owns the task from that point forward.

## When to Use

- Requests need different expertise levels or domains at different stages
- You want tiered processing (L1 triage, L2 specialist, L3 expert)
- The initial agent can classify and route but should not attempt the full task
- Context must transfer cleanly between agents (no information loss)
- You need clear accountability -- one agent owns the task at any given time

## When NOT to Use

- The routing agent needs to see the results (use Supervisor-Worker instead)
- Multiple agents need to collaborate on the same task (use Group Chat)
- The task can be fully handled by a single agent (unnecessary complexity)
- You need bidirectional communication between agents (handoff is one-way)
- Control should return to the original agent after delegation

## Architecture Diagram

```
    ┌──────────────┐         ┌──────────────┐         ┌──────────────┐
    │   Agent A     │         │   Agent B     │         │   Agent C     │
    │   Triage      │────────▶│   Specialist  │────────▶│   Expert      │
    │   (L1)        │ handoff │   (L2)        │ handoff │   (L3)        │
    └──────────────┘ + ctx   └──────────────┘ + ctx   └──────────────┘
                                                              │
                                                              ▼
                                                        Final Response

    Context envelope:
    ┌─────────────────────────────────┐
    │ original_request: "..."         │
    │ triage_classification: "billing"│
    │ conversation_history: [...]     │
    │ attempted_solutions: [...]      │
    │ handoff_reason: "needs expert"  │
    └─────────────────────────────────┘
```

## How It Works

1. **Initial Processing** -- Agent A receives the task and processes it within its capabilities.
2. **Handoff Decision** -- Agent A determines it cannot fully resolve the task and identifies the appropriate next agent.
3. **Context Packaging** -- Agent A bundles all relevant context: original request, its own findings, attempted actions, and the reason for handoff.
4. **Transfer** -- Full control is transferred to Agent B. Agent A's job is done.
5. **Continuation** -- Agent B picks up from where Agent A left off, using the context envelope.
6. **Chain** -- Agent B may further hand off to Agent C if needed, extending the chain.
7. **Resolution** -- The final agent in the chain produces the output.

## Configuration Example

```yaml
pattern: handoff
name: tiered-support

agents:
  - agent: orchestration/task-router
    role: triage
    model: claude-haiku-4-5
    description: Classify and route incoming requests
    handoff_rules:
      - condition: "category == 'billing'"
        target: support/billing-specialist
      - condition: "category == 'technical'"
        target: support/tech-specialist
      - condition: "category == 'account'"
        target: support/account-manager
      - condition: "complexity == 'high'"
        target: support/senior-engineer

  - agent: support/billing-specialist
    role: specialist
    model: claude-sonnet-4-6
    handoff_rules:
      - condition: "requires_refund_approval"
        target: support/finance-manager

  - agent: support/tech-specialist
    role: specialist
    model: claude-sonnet-4-6
    handoff_rules:
      - condition: "infrastructure_issue"
        target: devops/incident-responder

context_transfer:
  include:
    - original_request
    - conversation_history
    - classification
    - attempted_solutions
  max_context_tokens: 4000
```

## Code Example

```python
from multiagent import Catalog, patterns

catalog = Catalog()

# Define the handoff chain
chain = patterns.handoff(
    agents={
        "triage": catalog.load("orchestration/task-router"),
        "billing": catalog.load("support/billing-specialist"),
        "technical": catalog.load("support/tech-specialist"),
        "escalation": catalog.load("support/senior-engineer"),
    },
    entry_point="triage",
    handoff_rules={
        "triage": {
            "billing": lambda ctx: ctx["category"] == "billing",
            "technical": lambda ctx: ctx["category"] == "technical",
            "escalation": lambda ctx: ctx["complexity"] == "high",
        },
        "technical": {
            "escalation": lambda ctx: ctx.get("needs_escalation", False),
        },
    },
    model="claude-sonnet-4-6",
)

# Run
result = chain.run(
    "I was charged twice for my subscription last month",
    context={"user_id": "usr_12345"},
)

print(result.final_agent)     # Which agent resolved it
print(result.handoff_chain)   # ["triage", "billing"]
print(result.response)        # Final resolution
print(result.total_cost)      # Cost across all agents in the chain
```

## Real-World Examples

- **Customer Support Tiers** -- L1 bot handles FAQs and simple requests. Complex issues are handed off to an L2 specialist agent with domain knowledge. Unresolvable issues escalate to L3 with full context.
- **Medical Triage** -- A symptom checker classifies severity and routes to the appropriate specialist agent (general, urgent care, emergency) with the patient's full history.
- **Sales Pipeline** -- Lead qualifier agent assesses fit, hands qualified leads to a demo scheduler agent, which hands closed deals to an onboarding agent.
- **Code Issue Routing** -- A bug classifier determines whether the issue is frontend, backend, or infrastructure, then hands off to the relevant specialist with reproduction steps.
- **Legal Intake** -- A paralegal agent gathers facts and classifies the legal area, then hands off to a specialist agent (contract, IP, employment) with the full case brief.

## Pros and Cons

| Pros | Cons |
|------|------|
| Clean separation of concerns | Context can be lost or degraded during transfer |
| Each agent is fully focused on its role | No return path -- original agent cannot see the outcome |
| Cheap triage with expensive specialists | Chain length increases latency linearly |
| Clear accountability at each stage | Handoff rules can become complex routing logic |
| Easy to add new specialist agents | Debugging requires tracing through multiple agents |
| Low per-request cost (only 1-2 agents run) | Misrouting at triage wastes the entire chain |

## Cost Implications

- **Pay-per-hop**: Only the agents that actually handle the request are invoked. A 3-tier system might only use 2 agents for most requests.
- **Cheap triage, expensive specialists**: Use Haiku ($0.001) for classification/routing and Sonnet ($0.025) for specialist work. Most of the cost is in the specialist.
- **Context transfer overhead**: The context envelope adds tokens to each handoff. Keep it concise -- summarize rather than passing raw conversation history.
- **Short chains are cheapest**: Most requests should resolve in 1-2 hops. If requests regularly hit 3+ agents, the routing logic needs improvement.
- **Misrouting cost**: A misrouted request wastes the specialist's call before being re-routed. Invest in triage accuracy.
- **Typical cost range**: $0.003-0.03 per request (Haiku triage + Sonnet specialist).
