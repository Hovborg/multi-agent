"""Tests for the routing evaluation corpus."""

import json
from pathlib import Path

from click.testing import CliRunner

from multiagent.catalog import Catalog
from multiagent.cli import main
from multiagent.routing_eval import (
    RoutingEvalCase,
    RoutingEvalThresholds,
    evaluate_routing_corpus,
    load_routing_corpus,
)

CATALOG_DIR = Path(__file__).resolve().parent.parent / "catalog"


def test_loads_default_routing_corpus_with_expected_fields():
    cases = load_routing_corpus()

    assert 40 <= len(cases) <= 50
    assert all(case.id for case in cases)
    assert all(case.task for case in cases)
    assert all(case.expected_agents for case in cases)
    assert all(case.expected_pattern for case in cases)
    assert all(case.expected_target for case in cases)


def test_default_corpus_covers_multilingual_and_ambiguous_target_cases():
    case_ids = {case.id for case in load_routing_corpus()}

    assert "da-pr-tests-openclaw" in case_ids
    assert "da-blog-chatgpt" in case_ids
    assert "da-security-raw" in case_ids
    assert "ambiguous-default-local" in case_ids


def test_default_corpus_contains_negative_routing_cases():
    negative_cases = [case for case in load_routing_corpus() if case.forbidden_agents]

    assert len(negative_cases) >= 3
    assert {case.id for case in negative_cases} >= {
        "negative-meeting-notes-no-scheduler",
        "negative-fact-check-no-scraper",
        "negative-edit-blog-no-writer",
    }


def test_default_corpus_contains_risk_and_context_expectations():
    cases_by_id = {case.id: case for case in load_routing_corpus()}

    assert cases_by_id["meeting-claude"].expected_risk == {
        "min_side_effect_risk": "medium",
        "requires_human_review": True,
    }
    assert cases_by_id["scrape-a2a"].expected_context == {
        "min_context_size_risk": "medium",
    }


def test_default_routing_corpus_passes_against_current_router():
    report = evaluate_routing_corpus(catalog=Catalog(CATALOG_DIR))

    assert report.total == len(load_routing_corpus())
    assert report.passed == report.total
    assert report.pass_rate == 1.0


def test_report_exposes_failures_as_machine_readable_data():
    report = evaluate_routing_corpus(catalog=Catalog(CATALOG_DIR))
    payload = report.to_dict()

    assert payload["total"] == report.total
    assert payload["passed"] == report.passed
    assert payload["failed"] == 0
    assert payload["scores"] == {
        "agent_match_rate": 1.0,
        "pattern_match_rate": 1.0,
        "target_match_rate": 1.0,
        "forbidden_match_rate": 1.0,
        "risk_match_rate": 1.0,
        "context_match_rate": 1.0,
    }
    assert payload["results"][0]["case_id"]
    assert payload["results"][0]["actual_agents"]


def test_report_checks_score_specific_thresholds_independently():
    report = evaluate_routing_corpus(
        catalog=Catalog(CATALOG_DIR),
        cases=[
            RoutingEvalCase(
                id="target-mismatch-only",
                task="Review this PR and write missing tests for Codex config.",
                expected_agents=("code/code-reviewer", "code/test-writer"),
                expected_pattern="supervisor-worker",
                expected_target="raw",
            )
        ],
    )

    assert report.scores["agent_match_rate"] == 1.0
    assert report.scores["pattern_match_rate"] == 1.0
    assert report.scores["target_match_rate"] == 0.0
    assert report.threshold_failures(
        RoutingEvalThresholds(
            pass_rate=0.0,
            agent_match_rate=1.0,
            pattern_match_rate=1.0,
            target_match_rate=0.0,
            forbidden_match_rate=1.0,
        )
    ) == ()
    assert [failure.metric for failure in report.threshold_failures(
        RoutingEvalThresholds(target_match_rate=1.0)
    )] == ["target_match_rate"]


def test_eval_routing_cli_outputs_json_report():
    result = CliRunner().invoke(main, ["eval-routing", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["total"] >= 30
    assert payload["passed"] == payload["total"]
    assert payload["pass_rate"] == 1.0


def test_eval_routing_cli_accepts_score_specific_thresholds():
    result = CliRunner().invoke(
        main,
        [
            "eval-routing",
            "--min-agent-score",
            "1.0",
            "--min-pattern-score",
            "1.0",
            "--min-target-score",
            "0.95",
            "--min-forbidden-score",
            "1.0",
            "--min-risk-score",
            "1.0",
            "--min-context-score",
            "1.0",
        ],
    )

    assert result.exit_code == 0
    assert "agents 100%" in result.output
