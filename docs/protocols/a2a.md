# A2A (Agent-to-Agent Protocol)

## What is A2A?

A2A is Google's open standard for agent-to-agent communication. While MCP connects agents to tools, A2A connects agents to each other.

**Status (April 2026):** Version 1.0 released. 150+ organizations. Governed by the Linux Foundation.

## How A2A Works

```
┌──────────────┐     A2A Protocol     ┌──────────────┐
│   Agent A    │ ◄──────────────────► │   Agent B    │
│  (Client)    │   Agent Cards +      │  (Server)    │
│              │   Task Exchange      │              │
└──────────────┘                      └──────────────┘
```

Key concepts:
- **Agent Card** — JSON metadata describing what an agent can do (like a business card)
- **Task** — A unit of work exchanged between agents
- **Artifact** — Output produced by a task (text, files, structured data)

## The Protocol Stack

```
┌────────────────────────────────────────┐
│           AG-UI (Agent ↔ User)         │  Frontend streaming
├────────────────────────────────────────┤
│           A2A (Agent ↔ Agent)          │  Agent communication
├────────────────────────────────────────┤
│           MCP (Agent ↔ Tool)           │  Tool/data access
└────────────────────────────────────────┘
```

## Using A2A in multi-agent

```yaml
# Agent card for a catalog agent
agent_card:
  name: code-reviewer
  description: Reviews code for bugs and security issues
  capabilities:
    - code-review
    - security-audit
  input_modes:
    - text/plain
    - application/diff
  output_modes:
    - text/markdown
```

## When to Use A2A

- Agents built by different teams or organizations need to collaborate
- Agents run on different frameworks (CrewAI agent talks to LangGraph agent)
- Enterprise multi-agent systems with security boundaries
- Public agent registries where agents discover each other

## Resources

- [A2A Protocol Specification](https://github.com/a2a-protocol/a2a)
- [Google A2A Announcement](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)
