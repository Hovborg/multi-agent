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

    def test_existing_agents_default_schema_v2_metadata(self):
        catalog = Catalog(CATALOG_DIR)
        agent = catalog.load("code/code-reviewer")

        assert agent.orchestration == {}
        assert agent.safety == {}
        assert agent.observability == {}
        assert agent.outputs == {}
        assert agent.context == {}
        assert agent.protocols == {}

    def test_loads_schema_v2_metadata(self, tmp_path):
        agent_dir = tmp_path / "code"
        agent_dir.mkdir()
        (agent_dir / "schema-v2-agent.yaml").write_text(
            """
name: schema-v2-agent
version: "2.0"
description: Test agent with schema v2 metadata
category: code
tags: [test]
system_prompt: |
  You are a test agent.
tools: []
parameters: {}
cost_profile: {}
works_with: []
recommended_patterns: []
orchestration:
  control_mode: router
  execution_mode: dry_run
safety:
  side_effect_risk: low
  requires_human_review: true
observability:
  trace_tags: [catalog-test]
  eval_criteria: [returns-valid-json]
outputs:
  expected_artifacts: [agent-card]
context:
  loading: trigger
  max_context_tokens: 4096
protocols:
  a2a:
    expose: true
""",
            encoding="utf-8",
        )

        agent = Catalog(tmp_path).load("code/schema-v2-agent")

        assert agent.orchestration["control_mode"] == "router"
        assert agent.safety["requires_human_review"] is True
        assert agent.observability["trace_tags"] == ["catalog-test"]
        assert agent.outputs["expected_artifacts"] == ["agent-card"]
        assert agent.context["loading"] == "trigger"
        assert agent.protocols["a2a"]["expose"] is True

    def test_high_risk_agents_have_explicit_safety_metadata(self):
        catalog = Catalog(CATALOG_DIR)

        meeting = catalog.load("personal/meeting-scheduler")
        assert meeting.safety == {
            "side_effect_risk": "medium",
            "requires_human_review": True,
        }

        infra = catalog.load("devops/infra-provisioner")
        assert infra.safety == {
            "side_effect_risk": "high",
            "requires_human_review": True,
        }

        ci_cd = catalog.load("devops/ci-cd-agent")
        assert ci_cd.safety == {
            "side_effect_risk": "high",
            "requires_human_review": True,
        }

        email = catalog.load("personal/email-assistant")
        assert email.safety == {
            "side_effect_risk": "medium",
            "requires_human_review": True,
        }

        trading = catalog.load("finance/trading-analyst")
        assert trading.safety == {
            "side_effect_risk": "medium",
            "requires_human_review": True,
        }

    def test_large_context_agents_have_explicit_context_metadata(self):
        catalog = Catalog(CATALOG_DIR)

        scraper = catalog.load("research/web-scraper")
        assert scraper.context == {
            "loading": "progressive",
            "max_context_tokens": 8192,
        }


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
