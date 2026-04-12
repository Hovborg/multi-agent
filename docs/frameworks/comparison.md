# Framework Comparison (April 2026)

## Overview

| Framework | Creator | Stars | Language | Model Lock-in | MCP | Best For |
|-----------|---------|------:|----------|:-------------:|:---:|----------|
| **CrewAI** | Open source | 44K | Python | No | Yes | Role-based collaboration, easiest learning curve |
| **LangGraph** | LangChain | 25K | Python | No | Adapter | Complex workflows, production-grade (Uber, Klarna) |
| **smolagents** | HuggingFace | 26K | Python | No | Yes | Minimal footprint (~1000 lines), code-as-action |
| **OpenAI Agents SDK** | OpenAI | 21K | Python | OpenAI only | Yes | Fastest setup, handoff pattern |
| **Google ADK** | Google | 18K | Python/Go/TS | No* | Yes | Multi-language, Google Cloud integration |
| **Claude Agent SDK** | Anthropic | — | Python/CLI | Claude only | Native | Safety, sub-agents, computer use |
| **PydanticAI** | Pydantic | 16K | Python | No | Yes | Type safety, durable execution |
| **MS Agent Framework** | Microsoft | 9K | Python/.NET | No | Yes | Enterprise, merges SK + AutoGen |

*Google ADK is optimized for Gemini but supports other models.

## Decision Matrix

### Use CrewAI when...
- You want the fastest path to a working multi-agent system
- Role-based collaboration fits your use case (writer, editor, researcher)
- You need YAML-based agent definitions
- You want a large community and ecosystem

### Use LangGraph when...
- You need complex conditional workflows (DAG pattern)
- Production reliability is critical (checkpointing, observability)
- You're already using LangChain/LangSmith
- You need fine-grained control over state and flow

### Use smolagents when...
- You want minimal overhead (~1000 lines of core code)
- Code-as-action approach (agent writes Python, not JSON)
- You want 30% fewer LLM calls than JSON tool-calling
- HuggingFace model hub integration matters

### Use OpenAI Agents SDK when...
- You're committed to the OpenAI ecosystem
- Handoff pattern (agent-to-agent escalation) fits your use case
- You want the simplest possible API
- Built-in guardrails are important

### Use Google ADK when...
- You need multi-language support (Python, Go, TypeScript)
- Google Cloud / Vertex AI is your platform
- Built-in Sequential/Parallel/Loop agents match your patterns
- Multi-modal (vision, audio) agents are needed

### Use Claude Agent SDK when...
- Safety and human oversight are top priorities
- You need computer use (browser, desktop automation)
- Sub-agent architecture with isolated worktrees
- MCP-native tool integration

## Framework Size Comparison

```
CrewAI           ████████████████████░░░░░░░░░░░░░░░  18,000 lines
LangGraph        █████████████████████████░░░░░░░░░░░  25,000 lines
Claude SDK       ████████████░░░░░░░░░░░░░░░░░░░░░░░  12,000 lines
OpenAI SDK       ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░   8,000 lines
smolagents       █░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   1,000 lines
multi-agent      ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░     500 lines
```

## Protocol Support

| Framework | MCP (Tools) | A2A (Agent-to-Agent) | AG-UI (Frontend) |
|-----------|:-----------:|:--------------------:|:----------------:|
| CrewAI | Native | Planned | No |
| LangGraph | Adapter | Planned | Via CopilotKit |
| smolagents | Yes | No | No |
| OpenAI SDK | Native | Planned | No |
| Google ADK | Native | Native | Via AG-UI |
| Claude SDK | Native | No | No |
| MS Agent Framework | Native | Native | No |
