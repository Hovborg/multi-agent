"""Tests for framework-specific adapter templates."""

from pathlib import Path

from multiagent.adapters import crewai, google_adk, openai_sdk, smolagents
from multiagent.catalog import Catalog

CATALOG_DIR = Path(__file__).resolve().parent.parent / "catalog"


def test_openai_handoff_config():
    catalog = Catalog(CATALOG_DIR)
    reviewer = catalog.load("code/code-reviewer")
    test_writer = catalog.load("code/test-writer")

    config = openai_sdk.to_handoff_config(reviewer, [test_writer])

    assert config["pattern"] == "handoff"
    assert config["manager"]["name"] == "Code Reviewer"
    assert config["handoffs"][0]["name"] == "Test Writer"
    assert config["handoffs"][0]["catalog_name"] == "code/test-writer"


def test_openai_agent_as_tool_config():
    catalog = Catalog(CATALOG_DIR)
    reviewer = catalog.load("code/code-reviewer")
    test_writer = catalog.load("code/test-writer")

    config = openai_sdk.to_agent_tool_config(reviewer, [test_writer])

    assert config["pattern"] == "agent-as-tool"
    assert config["tools"][0]["tool_name"] == "test_writer"
    assert config["tools"][0]["agent"] == "code/test-writer"


def test_google_adk_workflow_config():
    catalog = Catalog(CATALOG_DIR)
    agents = catalog.load_team(["code/code-reviewer", "code/test-writer"])

    config = google_adk.to_workflow_config(agents, workflow="parallel")

    assert config["agent_type"] == "ParallelAgent"
    assert config["name"] == "parallel_code_reviewer_test_writer"
    assert [agent["name"] for agent in config["sub_agents"]] == ["code_reviewer", "test_writer"]


def test_crewai_flow_config():
    catalog = Catalog(CATALOG_DIR)
    agents = catalog.load_team(["code/code-reviewer", "code/test-writer"])

    config = crewai.to_flow_config(agents, flow_name="CodeReviewFlow", human_feedback=True)

    assert config["flow_name"] == "CodeReviewFlow"
    assert config["uses"] == ["Flow", "start", "listen", "router", "human_feedback"]
    assert config["steps"][0]["decorator"] == "@start()"
    assert config["steps"][1]["decorator"] == "@listen(review)"
    assert config["human_feedback"]["default_outcome"] == "needs_revision"


def test_smolagents_manager_config():
    catalog = Catalog(CATALOG_DIR)
    reviewer = catalog.load("code/code-reviewer")
    workers = catalog.load_team(["code/test-writer", "code/security-auditor"])

    config = smolagents.to_manager_config(reviewer, workers)

    assert config["agent_type"] == "manager"
    assert config["manager"]["name"] == "code-reviewer"
    assert [agent["name"] for agent in config["managed_agents"]] == [
        "test-writer",
        "security-auditor",
    ]
