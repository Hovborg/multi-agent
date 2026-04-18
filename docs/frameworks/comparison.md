# Framework Comparison

## Overview

| Framework | Creator | Language | Model Lock-in | MCP | Best For |
|-----------|---------|----------|:-------------:|:---:|----------|
| **CrewAI** | Open source | Python | No | Yes | Role-based collaboration, flow orchestration |
| **LangGraph** | LangChain | Python | No | Adapter | Complex stateful workflows |
| **smolagents** | HuggingFace | Python | No | Yes | Minimal agent definitions, code-as-action |
| **OpenAI Agents SDK** | OpenAI | Python/TypeScript | OpenAI-first | Yes | Handoffs, guardrails, tracing |
| **Google ADK** | Google | Python/Go/TS/Java | No* | Yes | Multi-language workflow agents, Google Cloud integration |
| **Claude Code subagents** | Anthropic | Markdown/CLI | Claude | Native | Task-specific subagents with isolated context |
| **PydanticAI** | Pydantic | Python | No | Yes | Type safety and observability |
| **MS Agent Framework** | Microsoft | Python/.NET | No | Yes | Enterprise workflows and HITL orchestration |

*Google ADK is optimized for Gemini but supports other models.

## Catalog Template Helpers

These helpers return plain dictionaries. They are useful when `multi-agent`
should recommend or generate a framework plan without importing the optional
runtime package.

| Framework | Helper | Use When |
|-----------|--------|----------|
| OpenAI Agents SDK | `openai_sdk.to_handoff_config(manager, handoffs)` | A specialist should take over the next turn |
| OpenAI Agents SDK | `openai_sdk.to_agent_tool_config(manager, tools)` | A manager should call specialists for bounded subtasks |
| Google ADK | `google_adk.to_workflow_config(agents, workflow="parallel")` | Built-in ADK workflow agents match the task shape |
| CrewAI | `crewai.to_flow_config(agents, flow_name=..., human_feedback=True)` | A deterministic Flow with routing or review gates is needed |
| smolagents | `smolagents.to_manager_config(manager, managed_agents)` | A CodeAgent-style manager should coordinate managed agents |

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
- You want a lightweight agent framework
- Code-as-action approach (agent writes Python, not JSON)
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

### Use Claude Code subagents when...
- Safety and human oversight are top priorities
- Task-specific subagents with isolated context fit the workflow
- MCP-native tool integration

## Protocol Support

| Framework | MCP (Tools) | A2A (Agent-to-Agent) | AG-UI (Frontend) |
|-----------|:-----------:|:--------------------:|:----------------:|
| CrewAI | Native | Planned | No |
| LangGraph | Adapter | Planned | Via CopilotKit |
| smolagents | Yes | No | No |
| OpenAI SDK | Native | Planned | No |
| Google ADK | Native | Native | Via AG-UI |
| Claude Code subagents | Native | No | No |
| MS Agent Framework | Native | Native | No |
