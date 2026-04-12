"""Auto-generate Mermaid diagrams for agent compositions."""

from __future__ import annotations

from multiagent.catalog import AgentDefinition


def _agent_id(agent: AgentDefinition) -> str:
    """Create a safe mermaid node ID from agent name."""
    return agent.name.replace("-", "_")


def _agent_label(agent: AgentDefinition) -> str:
    """Create a readable label."""
    return agent.name.replace("-", " ").title()


def supervisor_worker(
    supervisor: AgentDefinition,
    workers: list[AgentDefinition],
) -> str:
    """Generate mermaid diagram for supervisor/worker pattern."""
    sid = _agent_id(supervisor)
    lines = ["graph TD"]
    lines.append(f'    {sid}["{_agent_label(supervisor)}<br/><small>supervisor</small>"]')
    for w in workers:
        wid = _agent_id(w)
        lines.append(f'    {wid}["{_agent_label(w)}<br/><small>worker</small>"]')
        lines.append(f"    {sid} --> {wid}")

    lines.append(f"    style {sid} fill:#6366f1,stroke:#818cf8,color:#fff")
    for w in workers:
        lines.append(f"    style {_agent_id(w)} fill:#1e1b4b,stroke:#6366f1,color:#e0e7ff")
    return "\n".join(lines)


def sequential(agents: list[AgentDefinition]) -> str:
    """Generate mermaid diagram for sequential pipeline."""
    lines = ["graph LR"]
    for i, a in enumerate(agents):
        aid = _agent_id(a)
        lines.append(f'    {aid}["{_agent_label(a)}<br/><small>step {i+1}</small>"]')
        if i > 0:
            prev = _agent_id(agents[i - 1])
            lines.append(f"    {prev} --> {aid}")

    for i, a in enumerate(agents):
        color = "#6366f1" if i == 0 else "#1e1b4b"
        lines.append(f"    style {_agent_id(a)} fill:{color},stroke:#6366f1,color:#e0e7ff")
    return "\n".join(lines)


def parallel(
    agents: list[AgentDefinition],
    merger: AgentDefinition | None = None,
) -> str:
    """Generate mermaid diagram for parallel fan-out pattern."""
    lines = ["graph TD"]
    lines.append('    start(("Start"))')

    for a in agents:
        aid = _agent_id(a)
        lines.append(f'    {aid}["{_agent_label(a)}"]')
        lines.append(f"    start --> {aid}")

    if merger:
        mid = _agent_id(merger)
        lines.append(f'    {mid}["{_agent_label(merger)}<br/><small>merger</small>"]')
        for a in agents:
            lines.append(f"    {_agent_id(a)} --> {mid}")
        lines.append(f"    style {mid} fill:#6366f1,stroke:#818cf8,color:#fff")

    lines.append("    style start fill:#6366f1,stroke:#818cf8,color:#fff")
    for a in agents:
        lines.append(f"    style {_agent_id(a)} fill:#1e1b4b,stroke:#6366f1,color:#e0e7ff")
    return "\n".join(lines)


def reflection(
    producer: AgentDefinition,
    critic: AgentDefinition,
) -> str:
    """Generate mermaid diagram for reflection loop."""
    pid = _agent_id(producer)
    cid = _agent_id(critic)
    return f"""graph LR
    {pid}["{_agent_label(producer)}<br/><small>producer</small>"]
    {cid}["{_agent_label(critic)}<br/><small>critic</small>"]
    {pid} -->|"generate"| {cid}
    {cid} -->|"feedback"| {pid}
    {pid} -->|"quality met"| output(("Output"))
    style {pid} fill:#6366f1,stroke:#818cf8,color:#fff
    style {cid} fill:#1e1b4b,stroke:#6366f1,color:#e0e7ff
    style output fill:#10b981,stroke:#34d399,color:#fff"""


def handoff(agents: list[AgentDefinition]) -> str:
    """Generate mermaid diagram for handoff pattern."""
    lines = ["graph LR"]
    for i, a in enumerate(agents):
        aid = _agent_id(a)
        lines.append(f'    {aid}["{_agent_label(a)}"]')
        if i > 0:
            prev = _agent_id(agents[i - 1])
            lines.append(f'    {prev} -->|"handoff"| {aid}')

    for i, a in enumerate(agents):
        color = "#6366f1" if i == 0 else "#1e1b4b"
        lines.append(f"    style {_agent_id(a)} fill:{color},stroke:#6366f1,color:#e0e7ff")
    return "\n".join(lines)


def group_chat(agents: list[AgentDefinition]) -> str:
    """Generate mermaid diagram for group chat."""
    lines = ["graph TD"]
    lines.append('    selector(("Selector"))')
    for a in agents:
        aid = _agent_id(a)
        lines.append(f'    {aid}["{_agent_label(a)}"]')
        lines.append(f"    selector <--> {aid}")

    lines.append("    style selector fill:#6366f1,stroke:#818cf8,color:#fff")
    for a in agents:
        lines.append(f"    style {_agent_id(a)} fill:#1e1b4b,stroke:#6366f1,color:#e0e7ff")
    return "\n".join(lines)


# Pattern function registry
PATTERN_VISUALIZERS = {
    "supervisor-worker": lambda agents: supervisor_worker(agents[0], agents[1:]),
    "sequential": sequential,
    "parallel": lambda agents: parallel(agents),
    "reflection": lambda agents: reflection(agents[0], agents[1]) if len(agents) >= 2 else "",
    "handoff": handoff,
    "group-chat": group_chat,
}


def visualize_team(
    agents: list[AgentDefinition],
    pattern: str = "supervisor-worker",
) -> str:
    """Generate a mermaid diagram for a team of agents.

    Args:
        agents: List of agent definitions
        pattern: Orchestration pattern name

    Returns:
        Mermaid diagram source code
    """
    visualizer = PATTERN_VISUALIZERS.get(pattern)
    if not visualizer:
        return sequential(agents)
    return visualizer(agents)
