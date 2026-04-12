"""CrewAI adapter: convert catalog agents to CrewAI Agents and Crews."""

from __future__ import annotations

from typing import Any

from multiagent.catalog import AgentDefinition, Catalog

try:
    from crewai import Agent, Crew, Task

    HAS_CREWAI = True
except ImportError:
    HAS_CREWAI = False


def _require_crewai() -> None:
    if not HAS_CREWAI:
        raise ImportError(
            "CrewAI is not installed. Install with: pip install multi-agent[crewai]"
        )


def to_agent(definition: AgentDefinition, **overrides: Any) -> Agent:
    """Convert a catalog AgentDefinition to a CrewAI Agent."""
    _require_crewai()
    kwargs = {
        "role": definition.name.replace("-", " ").title(),
        "goal": definition.description,
        "backstory": definition.system_prompt,
        "verbose": overrides.pop("verbose", False),
    }
    kwargs.update(overrides)
    return Agent(**kwargs)


def to_task(
    description: str,
    agent: Agent,
    expected_output: str = "Detailed analysis and recommendations",
    **overrides: Any,
) -> Task:
    """Create a CrewAI Task."""
    _require_crewai()
    kwargs = {
        "description": description,
        "agent": agent,
        "expected_output": expected_output,
    }
    kwargs.update(overrides)
    return Task(**kwargs)


def from_catalog(
    agent_names: list[str],
    task_description: str = "",
    catalog: Catalog | None = None,
    **crew_kwargs: Any,
) -> Crew:
    """Create a CrewAI Crew from catalog agent names.

    Example:
        crew = crewai.from_catalog(
            ["code/code-reviewer", "code/test-writer"],
            task_description="Review this PR and write missing tests",
        )
        result = crew.kickoff()
    """
    _require_crewai()
    cat = catalog or Catalog()

    agents = []
    tasks = []
    for name in agent_names:
        definition = cat.load(name)
        agent = to_agent(definition)
        agents.append(agent)

        if task_description:
            task = to_task(task_description, agent)
            tasks.append(task)

    return Crew(agents=agents, tasks=tasks, **crew_kwargs)
