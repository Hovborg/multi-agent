"""Tests for the routing evaluation corpus."""

import json
from pathlib import Path

from click.testing import CliRunner

from multiagent.catalog import Catalog
from multiagent.cli import main
from multiagent.routing_eval import evaluate_routing_corpus, load_routing_corpus

CATALOG_DIR = Path(__file__).resolve().parent.parent / "catalog"


def test_loads_default_routing_corpus_with_expected_fields():
    cases = load_routing_corpus()

    assert 30 <= len(cases) <= 50
    assert all(case.id for case in cases)
    assert all(case.task for case in cases)
    assert all(case.expected_agents for case in cases)
    assert all(case.expected_pattern for case in cases)
    assert all(case.expected_target for case in cases)


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
    assert payload["results"][0]["case_id"]
    assert payload["results"][0]["actual_agents"]


def test_eval_routing_cli_outputs_json_report():
    result = CliRunner().invoke(main, ["eval-routing", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["total"] >= 30
    assert payload["passed"] == payload["total"]
    assert payload["pass_rate"] == 1.0
