"""Tests for the evaluation/benchmark system."""

from pathlib import Path

import pytest

from multiagent.catalog import Catalog
from multiagent.eval import benchmark_report, evaluate_agent, evaluate_catalog

CATALOG_DIR = Path(__file__).resolve().parent.parent / "catalog"


@pytest.fixture
def catalog():
    return Catalog(CATALOG_DIR)


@pytest.fixture
def reviewer(catalog):
    return catalog.load("code/code-reviewer")


class TestEvaluateAgent:
    def test_returns_score(self, reviewer):
        score = evaluate_agent(reviewer)
        assert score.agent_name == "code/code-reviewer"
        assert 0 <= score.overall <= 100

    def test_has_all_dimensions(self, reviewer):
        score = evaluate_agent(reviewer)
        assert score.prompt_quality >= 0
        assert score.tool_coverage >= 0
        assert score.cost_efficiency >= 0
        assert score.enhancement_readiness >= 0
        assert score.collaboration >= 0

    def test_has_grade(self, reviewer):
        score = evaluate_agent(reviewer)
        assert score.grade in ["A", "B", "C", "D", "F"]

    def test_has_string_representation(self, reviewer):
        score = evaluate_agent(reviewer)
        text = str(score)
        assert "code/code-reviewer" in text
        assert "/100" in text

    def test_well_defined_agent_scores_high(self, reviewer):
        score = evaluate_agent(reviewer)
        assert score.overall >= 60, f"Well-defined agent scored too low: {score.overall}"


class TestEvaluateCatalog:
    def test_evaluates_all(self, catalog):
        scores = evaluate_catalog(catalog)
        assert len(scores) == len(catalog)

    def test_all_scores_valid(self, catalog):
        scores = evaluate_catalog(catalog)
        for s in scores:
            assert 0 <= s.overall <= 100, f"{s.agent_name}: {s.overall}"


class TestBenchmarkReport:
    def test_generates_report(self, catalog):
        report = benchmark_report(catalog)
        assert "Benchmark Report" in report
        assert "Average score" in report
        assert "Grade Distribution" in report

    def test_has_category_averages(self, catalog):
        report = benchmark_report(catalog)
        assert "Category Averages" in report
        assert "code" in report

    def test_has_common_issues(self, catalog):
        report = benchmark_report(catalog)
        assert "Most Common Issues" in report
