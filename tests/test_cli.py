"""Tests for CLI routing commands."""

import json

from click.testing import CliRunner

from multiagent.cli import main


def test_route_json_outputs_machine_readable_decision():
    result = CliRunner().invoke(
        main,
        ["route", "review this PR and write missing tests", "--json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    names = [agent["name"] for agent in payload["agents"]]
    assert "code/code-reviewer" in names
    assert "code/test-writer" in names
    assert "content/writer" not in names
    assert payload["dry_run"] is True
    assert payload["reasons"]
    assert payload["risk"]["side_effect_risk"] in {"none", "low", "medium", "high"}
    assert payload["context"]["context_size_risk"] in {"low", "medium", "high"}


def test_route_json_includes_target_export_plan():
    result = CliRunner().invoke(
        main,
        ["route", "review this PR and write missing tests", "--target", "a2a-agent-card", "--json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["target"] == "a2a-agent-card"
    assert payload["exports"]
    export_by_agent = {item["agent"]: item for item in payload["exports"]}
    reviewer_export = export_by_agent["code/code-reviewer"]
    assert reviewer_export["target"] == "a2a-agent-card"
    assert reviewer_export["format"] == "A2A Agent Card JSON"
    assert reviewer_export["output_file"].endswith("code-reviewer.agent-card.json")
    assert reviewer_export["command"] == "multiagent export code/code-reviewer a2a-agent-card"


def test_route_explain_outputs_reasons():
    result = CliRunner().invoke(
        main,
        ["route", "review this PR and write missing tests", "--explain"],
    )

    assert result.exit_code == 0
    assert "Dry run" in result.output
    assert "Why" in result.output
    assert "code/code-reviewer" in result.output


def test_route_target_outputs_export_commands():
    result = CliRunner().invoke(
        main,
        ["route", "review this PR and write missing tests", "--target", "codex-config"],
    )

    assert result.exit_code == 0
    assert "Target: codex-config" in result.output
    assert "multiagent export code/code-reviewer codex-config" in result.output


def test_auto_routes_prompt_then_exits():
    result = CliRunner().invoke(
        main,
        ["auto"],
        input="review this PR and write missing tests\nexit\n",
    )

    assert result.exit_code == 0
    assert "Multi-Agent Auto Router" in result.output
    assert "code/code-reviewer" in result.output
    assert "content/writer" not in result.output
