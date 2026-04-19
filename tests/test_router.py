"""Tests for task routing decisions."""

from pathlib import Path

from multiagent.catalog import Catalog
from multiagent.router import AgentRouter

CATALOG_DIR = Path(__file__).resolve().parent.parent / "catalog"


def agent_names_for(task: str) -> list[str]:
    router = AgentRouter(Catalog(CATALOG_DIR))
    return [agent.full_name for agent in router.recommend(task).agents]


def test_code_task_with_write_missing_tests_does_not_select_content_writer():
    names = agent_names_for("review this PR and write missing tests")

    assert "code/code-reviewer" in names
    assert "code/test-writer" in names
    assert "content/writer" not in names


def test_content_writing_task_still_selects_content_writer():
    names = agent_names_for("write and edit a blog post about agent orchestration")

    assert "content/writer" in names
    assert "content/editor" in names


def test_recommendation_exposes_reasons_and_warnings():
    router = AgentRouter(Catalog(CATALOG_DIR))
    rec = router.recommend("review this PR and write missing tests")

    assert rec.reasons
    assert any("code/code-reviewer" in reason for reason in rec.reasons)
    assert rec.to_dict()["pattern"] == rec.pattern
    assert rec.to_dict()["agents"][0]["name"]


def test_route_risk_marks_side_effect_agents_for_human_review():
    router = AgentRouter(Catalog(CATALOG_DIR))
    rec = router.recommend("Schedule a meeting on the calendar for next week")

    assert rec.risk["requires_human_review"] is True
    assert rec.risk["side_effect_risk"] in {"medium", "high"}
    assert any("personal/meeting-scheduler" in reason for reason in rec.risk["reasons"])


def test_route_context_scores_large_research_teams():
    router = AgentRouter(Catalog(CATALOG_DIR))
    rec = router.recommend("Scrape product listings and analyze the extracted data")

    assert rec.context["context_size_risk"] in {"medium", "high"}
    assert rec.context["estimated_context_tokens"] >= 8192
    assert rec.to_dict()["context"]["loading"] in {"trigger", "always", "progressive"}
