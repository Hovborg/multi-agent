"""Tests for task routing decisions."""

from multiagent.catalog import CATALOG_DIR, Catalog
from multiagent.router import AgentRouter


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


def test_research_route_has_bounded_parallel_delegation_policy():
    router = AgentRouter(Catalog(CATALOG_DIR))
    rec = router.recommend("Research and compare current multi-agent frameworks")

    assert rec.policy["control_mode"] == "router"
    assert rec.policy["parallelizable"] is True
    assert 2 <= rec.policy["max_delegates"] <= 5
    assert set(rec.policy["delegation_contract"]) == {
        "objective",
        "output_format",
        "allowed_tools",
        "source_requirements",
        "stop_conditions",
    }


def test_handoff_route_transfers_control_without_parallel_fanout():
    router = AgentRouter(Catalog(CATALOG_DIR))
    rec = router.recommend("Route a customer support ticket to the right tier")

    assert rec.policy["control_mode"] == "handoff"
    assert rec.policy["parallelizable"] is False
    assert rec.policy["max_delegates"] == 1


def test_side_effect_route_requires_policy_approval():
    router = AgentRouter(Catalog(CATALOG_DIR))
    rec = router.recommend("Schedule a meeting on the calendar")

    assert rec.policy["approval_required"] is True
    assert "external_side_effects" in rec.policy["trust_boundary"]


def test_no_match_route_disables_delegation():
    router = AgentRouter(Catalog(CATALOG_DIR))
    rec = router.recommend("flibbertigibbet")

    assert rec.agents == []
    assert rec.policy["max_delegates"] == 0
    assert rec.policy["stop_conditions"][0] == "no_agents_matched"
