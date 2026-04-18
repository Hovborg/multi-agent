# Framework Template Plans

Use this recipe when you want `multi-agent` to plan how catalog agents should
map into framework-native orchestration, without importing the optional runtime
packages yet.

## Load a small team

```python
from multiagent import Catalog
from multiagent.adapters import crewai, google_adk, openai_sdk, smolagents

catalog = Catalog()
reviewer = catalog.load("code/code-reviewer")
test_writer = catalog.load("code/test-writer")
security_auditor = catalog.load("code/security-auditor")
team = [reviewer, test_writer, security_auditor]
```

## OpenAI Agents SDK

Use handoffs when another agent should take over the conversation:

```python
handoff_plan = openai_sdk.to_handoff_config(
    manager=reviewer,
    handoffs=[test_writer, security_auditor],
)
```

Use agent-as-tool when a manager should stay in control and call specialists
for bounded work:

```python
tool_plan = openai_sdk.to_agent_tool_config(
    manager=reviewer,
    tools=[test_writer, security_auditor],
)
```

## Google ADK

Use sequential workflows when order matters, and parallel workflows when each
agent can work independently:

```python
sequential = google_adk.to_workflow_config(team, workflow="sequential")
parallel = google_adk.to_workflow_config(team, workflow="parallel")
```

## CrewAI Flow

Use a Flow template when the process needs deterministic steps, routing, or
human feedback:

```python
flow = crewai.to_flow_config(
    team,
    flow_name="CodeReviewFlow",
    human_feedback=True,
)
```

## smolagents Manager

Use a manager config when a CodeAgent-style manager should coordinate managed
agents:

```python
manager = smolagents.to_manager_config(
    manager=reviewer,
    managed_agents=[test_writer, security_auditor],
)
```

Each helper returns a plain dictionary. Convert that dictionary into framework
objects only at the integration boundary where dependencies, model providers,
credentials, and side effects are explicit.
