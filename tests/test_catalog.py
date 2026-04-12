"""Tests for the agent catalog."""

from pathlib import Path

import pytest

from multiagent.catalog import Catalog
from multiagent.cost import MODEL_PRICING, CostEstimator
from multiagent.router import AgentRouter

CATALOG_DIR = Path(__file__).resolve().parent.parent / "catalog"


class TestCatalog:
    def test_load_catalog(self):
        catalog = Catalog(CATALOG_DIR)
        assert len(catalog) > 0

    def test_list_categories(self):
        catalog = Catalog(CATALOG_DIR)
        categories = catalog.list_categories()
        assert "code" in categories

    def test_load_agent(self):
        catalog = Catalog(CATALOG_DIR)
        agent = catalog.load("code/code-reviewer")
        assert agent.name == "code-reviewer"
        assert agent.category == "code"
        assert agent.system_prompt != ""
        assert len(agent.tags) > 0

    def test_load_agent_short_name(self):
        catalog = Catalog(CATALOG_DIR)
        agent = catalog.load("code-reviewer")
        assert agent.name == "code-reviewer"

    def test_load_nonexistent_agent(self):
        catalog = Catalog(CATALOG_DIR)
        with pytest.raises(KeyError):
            catalog.load("nonexistent/agent")

    def test_search(self):
        catalog = Catalog(CATALOG_DIR)
        results = catalog.search("review")
        assert len(results) > 0
        names = [a.name for a in results]
        assert "code-reviewer" in names

    def test_search_by_tag(self):
        catalog = Catalog(CATALOG_DIR)
        results = catalog.search("security")
        assert len(results) > 0

    def test_by_category(self):
        catalog = Catalog(CATALOG_DIR)
        code_agents = catalog.by_category("code")
        assert len(code_agents) >= 3
        for agent in code_agents:
            assert agent.category == "code"

    def test_get_team(self):
        catalog = Catalog(CATALOG_DIR)
        team = catalog.get_team_for("code/code-reviewer")
        team_names = [a.full_name for a in team]
        assert "code/test-writer" in team_names

    def test_agent_has_cost_profile(self):
        catalog = Catalog(CATALOG_DIR)
        agent = catalog.load("code/code-reviewer")
        assert agent.cost_profile.input_tokens_per_run > 0
        assert agent.cost_profile.output_tokens_per_run > 0
        assert len(agent.cost_profile.recommended_models) > 0


class TestCostEstimator:
    def test_estimate_agent(self):
        catalog = Catalog(CATALOG_DIR)
        agent = catalog.load("code/code-reviewer")
        estimate = CostEstimator.estimate_agent(agent)
        assert len(estimate.estimates) > 0
        assert estimate.cheapest().cost_usd >= 0

    def test_estimate_team(self):
        catalog = Catalog(CATALOG_DIR)
        team = catalog.load_team(["code/code-reviewer", "code/test-writer"])
        estimate = CostEstimator.estimate_team(team, model="claude-haiku-4-5")
        assert len(estimate.estimates) == 1
        assert estimate.estimates[0].cost_usd > 0

    def test_model_pricing_has_entries(self):
        assert len(MODEL_PRICING) > 5
        assert "claude-haiku-4-5" in MODEL_PRICING
        assert "gpt-4o" in MODEL_PRICING

    def test_free_local_models(self):
        catalog = Catalog(CATALOG_DIR)
        agent = catalog.load("code/code-reviewer")
        estimate = CostEstimator.estimate_agent(agent, models=["gemma4-27b"])
        assert estimate.estimates[0].cost_usd == 0.0


class TestAgentRouter:
    def test_recommend_code_review(self):
        router = AgentRouter(Catalog(CATALOG_DIR))
        rec = router.recommend("review this PR for bugs and security issues")
        assert len(rec.agents) > 0
        agent_names = [a.name for a in rec.agents]
        assert "code-reviewer" in agent_names

    def test_recommend_research(self):
        router = AgentRouter(Catalog(CATALOG_DIR))
        rec = router.recommend("research the latest AI frameworks")
        assert len(rec.agents) > 0

    def test_recommend_returns_pattern(self):
        router = AgentRouter(Catalog(CATALOG_DIR))
        rec = router.recommend("write and edit a blog post")
        assert rec.pattern != ""
        assert rec.pattern_reason != ""

    def test_recommend_confidence(self):
        router = AgentRouter(Catalog(CATALOG_DIR))
        rec = router.recommend("review code for security vulnerabilities")
        assert 0.0 < rec.confidence <= 1.0
