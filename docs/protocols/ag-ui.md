# AG-UI (Agent-User Interaction Protocol)

## What is AG-UI?

AG-UI is CopilotKit's open protocol for streaming agent interactions to frontend UIs. It completes the protocol stack: MCP (tools), A2A (agents), AG-UI (users).

**Status (April 2026):** Growing adoption. Integrated with AWS and Google ADK.

## How AG-UI Works

```
┌──────────────┐     AG-UI Protocol    ┌──────────────┐
│   AI Agent   │ ──────────────────►   │   Frontend   │
│  (Backend)   │   Server-Sent Events  │   (React)    │
│              │   + JSON messages      │              │
└──────────────┘                       └──────────────┘
```

AG-UI streams:
- **Text deltas** — Token-by-token streaming to the UI
- **Tool calls** — Show which tools the agent is using
- **State updates** — Agent progress, intermediate results
- **Lifecycle events** — Start, pause, complete, error

## Integration with multi-agent

AG-UI support is on our roadmap. When available:

```python
from multiagent.adapters import ag_ui

# Stream a team's execution to a frontend
stream = ag_ui.stream_pattern(
    pattern=team,
    task="Review this PR",
    endpoint="/api/agent-stream",
)
```

## Resources

- [AG-UI Protocol](https://www.copilotkit.ai/ag-ui)
- [CopilotKit](https://www.copilotkit.ai/)
