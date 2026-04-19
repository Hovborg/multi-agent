"""Framework-native routing targets for dry-run route plans."""

from __future__ import annotations

from typing import Any

from multiagent.adapters import crewai, google_adk, openai_sdk, smolagents
from multiagent.catalog import AgentDefinition
from multiagent.export import EXPORTERS

FRAMEWORK_TARGETS: dict[str, str] = {
    "openai-agents": "OpenAI Agents SDK plan",
    "adk": "Google ADK workflow plan",
    "crewai-flow": "CrewAI Flow plan",
    "smolagents-manager": "smolagents manager plan",
}

ROUTE_TARGETS: tuple[str, ...] = tuple([*EXPORTERS, *FRAMEWORK_TARGETS])


def build_framework_plan(
    agents: list[AgentDefinition],
    pattern: str,
    target: str,
) -> dict[str, Any]:
    """Build a framework-native dry-run plan for a routed team."""
    if target not in FRAMEWORK_TARGETS:
        expected = ", ".join(FRAMEWORK_TARGETS)
        raise ValueError(f"Unknown framework target '{target}'. Expected: {expected}")

    if not agents:
        return {
            "target": target,
            "format": FRAMEWORK_TARGETS[target],
            "pattern": pattern,
            "config": {},
            "notes": ["No agents matched, so no framework plan was generated."],
        }

    if target == "openai-agents":
        return _openai_agents_plan(agents, pattern)
    if target == "adk":
        return _adk_plan(agents, pattern)
    if target == "crewai-flow":
        return _crewai_flow_plan(agents, pattern)
    if target == "smolagents-manager":
        return _smolagents_manager_plan(agents, pattern)

    raise AssertionError(f"Unhandled framework target: {target}")


def _openai_agents_plan(agents: list[AgentDefinition], pattern: str) -> dict[str, Any]:
    manager, workers = _split_manager_workers(agents)
    if pattern == "handoff":
        config = openai_sdk.to_handoff_config(manager, workers)
        helper = "openai_sdk.to_handoff_config"
    else:
        config = openai_sdk.to_agent_tool_config(manager, workers)
        helper = "openai_sdk.to_agent_tool_config"

    return {
        "target": "openai-agents",
        "format": FRAMEWORK_TARGETS["openai-agents"],
        "pattern": pattern,
        "helper": helper,
        "config": config,
        "notes": [
            "Use handoffs when specialists should own follow-up turns.",
            "Use agent-as-tool when the manager should keep control.",
        ],
    }


def _adk_plan(agents: list[AgentDefinition], pattern: str) -> dict[str, Any]:
    workflow = "parallel" if pattern in {"parallel", "split-and-merge"} else "sequential"
    return {
        "target": "adk",
        "format": FRAMEWORK_TARGETS["adk"],
        "pattern": pattern,
        "helper": "google_adk.to_workflow_config",
        "config": google_adk.to_workflow_config(agents, workflow=workflow),
        "notes": [
            "Use ParallelAgent for independent fan-out work.",
            "Use SequentialAgent when each step depends on previous output.",
        ],
    }


def _crewai_flow_plan(agents: list[AgentDefinition], pattern: str) -> dict[str, Any]:
    flow_name = "".join(part.title() for part in [agents[0].category, "flow"])
    human_feedback = pattern in {"reflection", "supervisor-worker"}
    return {
        "target": "crewai-flow",
        "format": FRAMEWORK_TARGETS["crewai-flow"],
        "pattern": pattern,
        "helper": "crewai.to_flow_config",
        "config": crewai.to_flow_config(
            agents,
            flow_name=flow_name,
            human_feedback=human_feedback,
        ),
        "notes": [
            "Use this as a deterministic Flow template.",
            "Run crewai flow plot after turning the template into code.",
        ],
    }


def _smolagents_manager_plan(agents: list[AgentDefinition], pattern: str) -> dict[str, Any]:
    manager, workers = _split_manager_workers(agents)
    return {
        "target": "smolagents-manager",
        "format": FRAMEWORK_TARGETS["smolagents-manager"],
        "pattern": pattern,
        "helper": "smolagents.to_manager_config",
        "config": smolagents.to_manager_config(manager, workers),
        "notes": [
            "Managed agents need stable names and descriptions so the manager can call them.",
            "Use a CodeAgent-style manager only where code execution is acceptable.",
        ],
    }


def _split_manager_workers(
    agents: list[AgentDefinition],
) -> tuple[AgentDefinition, list[AgentDefinition]]:
    manager = agents[0]
    return manager, agents[1:]
