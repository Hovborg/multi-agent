"""Tests for framework-native route targets."""

import json
from pathlib import Path

from click.testing import CliRunner

from multiagent.catalog import Catalog
from multiagent.cli import main
from multiagent.framework_targets import build_framework_plan
from multiagent.router import AgentRouter

CATALOG_DIR = Path(__file__).resolve().parent.parent / "catalog"


def test_router_recommends_openai_agents_sdk_target():
    router = AgentRouter(Catalog(CATALOG_DIR))
    rec = router.recommend("Review this PR with OpenAI Agents SDK agent-as-tool routing.")

    assert rec.suggested_target == "openai-agents"
    assert "OpenAI Agents SDK" in rec.target_reason


def test_build_openai_agents_framework_plan_uses_agent_as_tool_by_default():
    catalog = Catalog(CATALOG_DIR)
    agents = catalog.load_team(["code/code-reviewer", "code/test-writer"])

    plan = build_framework_plan(agents, pattern="supervisor-worker", target="openai-agents")

    assert plan["target"] == "openai-agents"
    assert plan["format"] == "OpenAI Agents SDK plan"
    assert plan["config"]["pattern"] == "agent-as-tool"
    assert plan["config"]["manager"]["catalog_name"] == "code/code-reviewer"
    assert plan["config"]["tools"][0]["agent"] == "code/test-writer"


def test_route_json_outputs_framework_plan_for_framework_target():
    result = CliRunner().invoke(
        main,
        [
            "route",
            "Review this PR and write missing tests with OpenAI Agents SDK.",
            "--target",
            "openai-agents",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["target"] == "openai-agents"
    assert "exports" not in payload
    assert payload["framework_plan"]["format"] == "OpenAI Agents SDK plan"
    assert payload["framework_plan"]["config"]["pattern"] == "agent-as-tool"
