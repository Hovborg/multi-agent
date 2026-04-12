# Group Chat Pattern

**Multiple agents participate in a shared conversation, with a selector determining who speaks next.**

Like a design review meeting where an architect, a security engineer, and a UX designer each contribute their perspective. A moderator (the selector) decides who should speak next based on the conversation state.

## When to Use

- The task benefits from multiple perspectives and dynamic interaction
- Agents need to react to each other's contributions (not just the original input)
- The conversation flow cannot be predetermined -- it depends on what emerges
- You want debate, consensus-building, or brainstorming between agents
- Cross-domain tasks where specialists need to negotiate trade-offs

## When NOT to Use

- Tasks have a clear, predetermined execution order -- use Sequential
- Agents work on independent subtasks -- use Parallel
- You need strict cost control (group chats are token-expensive)
- One agent should be in charge -- use Supervisor-Worker
- The conversation tends to go in circles without converging
- Latency is critical (each turn is a full LLM call)

## Architecture Diagram

```
    ┌─────────────────────────────────────────┐
    │            Shared Conversation           │
    │                                         │
    │  ┌───────┐  ┌───────┐  ┌───────┐       │
    │  │Agent A│  │Agent B│  │Agent C│       │
    │  │Arch.  │  │Sec.   │  │UX     │       │
    │  └───┬───┘  └───┬───┘  └───┬───┘       │
    │      │          │          │            │
    │      └──────────┼──────────┘            │
    │                 │                       │
    │          ┌──────▼──────┐                │
    │          │  Selector    │                │
    │          │  (Moderator) │                │
    │          └──────┬──────┘                │
    │                 │ "Agent B, your turn"   │
    │                 ▼                       │
    │         Shared Message Log              │
    │  ┌────────────────────────────────┐     │
    │  │ [A]: "I propose microservices" │     │
    │  │ [B]: "Security concern: ..."   │     │
    │  │ [C]: "UX impact: ..."          │     │
    │  │ [A]: "Revised proposal: ..."   │     │
    │  └────────────────────────────────┘     │
    └─────────────────────────────────────────┘
                       │
                       ▼ (max_turns or consensus)
                  Final Summary
```

## How It Works

1. **Initialization** -- All agents are introduced with their roles. The initial task is posted to the shared conversation.
2. **Speaker Selection** -- The selector (a lightweight LLM call or rule-based function) determines which agent should speak next based on the conversation history and agent roles.
3. **Turn Execution** -- The selected agent sees the full conversation history and contributes its response.
4. **Logging** -- The response is appended to the shared message log visible to all agents.
5. **Repeat** -- Steps 2-4 repeat until a termination condition is met:
   - Maximum turns reached
   - A designated agent signals consensus
   - All agents have contributed without new issues raised
6. **Summary** -- Optionally, a summarizer agent produces a final consolidated output from the conversation.

## Configuration Example

```yaml
pattern: group-chat
name: design-review

agents:
  - agent: code/code-reviewer
    role: architect
    description: "Software architecture and system design"
    model: claude-sonnet-4-6

  - agent: code/security-auditor
    role: security
    description: "Security review and threat modeling"
    model: claude-sonnet-4-6

  - agent: content/editor
    role: technical_writer
    description: "Documentation clarity and developer experience"
    model: claude-haiku-4-5

selector:
  strategy: llm            # llm, round-robin, or priority
  model: claude-haiku-4-5  # Cheap model for selection decisions
  prompt: |
    Based on the conversation so far, which agent should speak next?
    Consider who has relevant expertise for the current discussion point.

termination:
  max_turns: 12
  consensus_signal: "APPROVED"  # Any agent can signal consensus
  idle_rounds: 2               # Stop if 2 rounds pass with no new issues

summarizer:
  agent: orchestration/quality-gate
  model: claude-sonnet-4-6
  prompt: "Summarize the design review into actionable decisions and open items"
```

## Code Example

```python
from multiagent import Catalog, patterns

catalog = Catalog()

# Define the group chat
chat = patterns.group_chat(
    agents=[
        catalog.load("code/code-reviewer"),
        catalog.load("code/security-auditor"),
        catalog.load("content/editor"),
    ],
    selector="llm",           # LLM-based speaker selection
    selector_model="claude-haiku-4-5",
    max_turns=12,
    model="claude-sonnet-4-6",
)

# Run the group chat
result = chat.run(
    "Review this API design for a payment processing system",
    context={
        "api_spec": open("payment-api.yaml").read(),
        "requirements": open("requirements.md").read(),
    },
)

# Access the conversation
for turn in result.conversation:
    print(f"[{turn.agent_role}]: {turn.message[:80]}...")

print(f"Turns: {result.total_turns}")
print(f"Consensus reached: {result.consensus}")
print(f"Summary: {result.summary}")
print(f"Total cost: ${result.total_cost:.4f}")
```

## Real-World Examples

- **Design Review** -- An architect, security engineer, and UX designer review a proposed system design. Each raises concerns from their domain, and the group converges on a revised design.
- **Brainstorming** -- Product, engineering, and marketing agents generate and refine feature ideas. The selector ensures each perspective gets heard.
- **Multi-Perspective Analysis** -- A bull case agent, bear case agent, and neutral analyst debate an investment thesis. The conversation captures the strongest arguments from each side.
- **Code Architecture Decision** -- Frontend, backend, and DevOps agents discuss how to implement a new feature, negotiating API contracts and deployment concerns.
- **Legal Case Strategy** -- Plaintiff and defendant agents argue their positions while a judge agent moderates, revealing strengths and weaknesses of each argument.

## Pros and Cons

| Pros | Cons |
|------|------|
| Rich multi-perspective output | Most expensive pattern (many LLM calls) |
| Agents react to and build on each other | Conversations can go in circles |
| Emergent insights from interaction | High latency (sequential turns) |
| Natural for debate and review tasks | Context window fills up quickly |
| Flexible -- conversation adapts to needs | Selector logic is hard to get right |
| Closest to human collaboration dynamics | Difficult to debug or reproduce exactly |

## Cost Implications

- **Highest cost pattern**: Every turn is a full LLM call, and every agent sees the full conversation history. A 12-turn chat with Sonnet costs ~$0.30-0.60.
- **Context growth**: Each turn adds to the shared history. By turn 10, every agent is processing thousands of tokens of conversation. Token costs accelerate.
- **Selector overhead**: The selector adds a small LLM call per turn. Use Haiku for selection (~$0.001/turn) to minimize this.
- **Turn limits are critical**: Without `max_turns`, costs can spiral. Set conservative limits and increase based on observed quality.
- **Model tiering**: Use Sonnet for core agents and Haiku for the selector and summarizer. Consider Haiku for agents with simpler roles.
- **Summarizer amortizes value**: A $0.02 summary call makes a $0.40 group chat reusable and shareable.
- **Typical cost range**: $0.10-0.60 per run (8-12 turns with Sonnet), $0.02-0.10 with Haiku agents.
