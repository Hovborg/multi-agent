# MCP (Model Context Protocol)

## What is MCP?

MCP is the open standard for connecting AI agents to tools and data sources. Think of it as "USB for AI" — a universal interface that lets any agent talk to any tool.

**Status (April 2026):** 97 million monthly SDK downloads. Governed by the Agentic AI Foundation under the Linux Foundation.

## How MCP Works

```
┌──────────────┐     MCP Protocol     ┌──────────────┐
│   AI Agent   │ ◄──────────────────► │  MCP Server  │
│  (MCP Host)  │   JSON-RPC over      │  (Tool/Data) │
│              │   stdio or HTTP      │              │
└──────────────┘                      └──────────────┘
```

An MCP server exposes:
- **Tools** — Functions the agent can call (e.g., read file, query database, send email)
- **Resources** — Data the agent can read (e.g., file contents, database schemas)
- **Prompts** — Pre-built prompt templates

## Using MCP in multi-agent

Every agent definition can reference MCP tools:

```yaml
# In a catalog agent definition
tools:
  - type: mcp
    server: filesystem          # Built-in MCP server
    description: Read and write files

  - type: mcp
    server: postgres            # Database MCP server
    config:
      connection_string: "${DATABASE_URL}"

  - type: mcp
    server: custom              # Your own MCP server
    url: "http://localhost:8080"
```

## MCP vs Other Approaches

| Approach | Scope | Standard? | When to use |
|----------|-------|:---------:|-------------|
| **MCP** | Agent ↔ Tool | Yes (Linux Foundation) | Always — it's the universal standard |
| **Function calling** | Agent ↔ Tool | Provider-specific | Simple single-model tools |
| **A2A** | Agent ↔ Agent | Yes (Linux Foundation) | Multi-agent coordination |
| **AG-UI** | Agent ↔ Frontend | Growing | Streaming UI updates |

## Popular MCP Servers

| Server | Purpose | Stars |
|--------|---------|------:|
| filesystem | Read/write local files | Built-in |
| postgres | Query PostgreSQL databases | 5K+ |
| github | GitHub API operations | 4K+ |
| slack | Slack messaging | 3K+ |
| browser | Web browsing and scraping | 3K+ |
| memory | Persistent memory storage | 2K+ |

## Resources

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [MCP Server Registry](https://github.com/modelcontextprotocol/servers)
- [Agentic AI Foundation](https://agenticaifoundation.org/)
