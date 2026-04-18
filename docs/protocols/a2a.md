# A2A (Agent-to-Agent Protocol)

## What is A2A?

A2A is an open standard for agent-to-agent communication. While MCP connects agents to tools, A2A connects agents to each other.

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

Export any catalog agent as an A2A Agent Card JSON document:

```bash
multiagent export code/code-reviewer a2a-agent-card -o ./agent-cards
```

The generated card uses the A2A 1.0 Agent Card shape:

```json
{
  "name": "Code Reviewer",
  "description": "Reviews code changes for bugs, security vulnerabilities, and style violations",
  "version": "1.0",
  "supportedInterfaces": [
    {
      "url": "http://localhost:8000/a2a/code-reviewer",
      "protocolBinding": "JSONRPC",
      "protocolVersion": "1.0"
    }
  ],
  "capabilities": {
    "streaming": false,
    "pushNotifications": false,
    "extendedAgentCard": false
  },
  "defaultInputModes": ["text/plain", "application/json"],
  "defaultOutputModes": ["text/plain", "application/json"],
  "skills": [
    {
      "id": "code-reviewer",
      "name": "Code Reviewer",
      "description": "Reviews code changes for bugs, security vulnerabilities, and style violations",
      "tags": ["code-review", "security", "quality", "pr-review"]
    }
  ]
}
```

For a real A2A service, serve the card at `.well-known/agent-card.json` and
replace the local `supportedInterfaces[0].url` with your service endpoint.

## When to Use A2A

- Agents built by different teams or organizations need to collaborate
- Agents run on different frameworks (CrewAI agent talks to LangGraph agent)
- Enterprise multi-agent systems with security boundaries
- Public agent registries where agents discover each other

## Resources

- [A2A Protocol Specification](https://a2a-protocol.org/latest/specification/)
- [A2A Agent Skills & Agent Card tutorial](https://a2a-protocol.org/latest/tutorials/python/3-agent-skills-and-card/)
- [Google A2A Announcement](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)
