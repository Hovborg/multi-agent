"""Tests for the export module."""

import json
from pathlib import Path

import pytest
import tomllib

from multiagent.catalog import Catalog
from multiagent.export import (
    EXPORTERS,
    export_agent,
    to_a2a_agent_card,
    to_agentskill,
    to_chatgpt,
    to_claude_code,
    to_codex,
    to_codex_config,
    to_gemini,
    to_raw,
)

CATALOG_DIR = Path(__file__).resolve().parent.parent / "catalog"


@pytest.fixture
def catalog():
    return Catalog(CATALOG_DIR)


@pytest.fixture
def reviewer(catalog):
    return catalog.load("code/code-reviewer")


class TestClaudeCodeExport:
    def test_has_frontmatter(self, reviewer):
        output = to_claude_code(reviewer)
        assert output.startswith("---")
        assert "name: code-reviewer" in output
        assert "description: >" in output
        assert "Use when tasks involve:" in output

    def test_has_system_prompt(self, reviewer):
        output = to_claude_code(reviewer)
        assert "expert code reviewer" in output

    def test_has_tool_hints_section(self, reviewer):
        output = to_claude_code(reviewer)
        assert "## Catalog Tool Hints" in output
        assert "filesystem" in output

    def test_has_related_agents(self, reviewer):
        output = to_claude_code(reviewer)
        assert "## Related Agents" in output
        assert "code/test-writer" in output


class TestAgentSkillExport:
    def test_has_skill_frontmatter(self, reviewer):
        output = to_agentskill(reviewer)
        assert output.startswith("---")
        assert "name: code-reviewer" in output
        assert "TRIGGER THIS SKILL WHEN:" in output
        assert "metadata:" in output

    def test_has_system_prompt(self, reviewer):
        output = to_agentskill(reviewer)
        assert "expert code reviewer" in output


class TestCodexExport:
    def test_has_header(self, reviewer):
        output = to_codex(reviewer)
        assert "## Code Reviewer" in output

    def test_has_category_and_tags(self, reviewer):
        output = to_codex(reviewer)
        assert "**Category:** code" in output
        assert "code-review" in output

    def test_has_instructions(self, reviewer):
        output = to_codex(reviewer)
        assert "### Instructions" in output
        assert "expert code reviewer" in output

    def test_has_works_with(self, reviewer):
        output = to_codex(reviewer)
        assert "### Works With" in output
        assert "code/test-writer" in output

    def test_has_patterns(self, reviewer):
        output = to_codex(reviewer)
        assert "### Recommended Patterns" in output
        assert "supervisor-worker" in output


class TestCodexConfigExport:
    def test_is_valid_project_scoped_config(self, reviewer):
        output = to_codex_config(reviewer)
        parsed = tomllib.loads(output)

        assert parsed["features"]["multi_agent"] is True
        assert parsed["agents"]["max_threads"] == 6
        assert parsed["agents"]["max_depth"] == 1
        assert parsed["agents"]["job_max_runtime_seconds"] == 1800

    def test_has_agent_role_guidance(self, reviewer):
        output = to_codex_config(reviewer)
        parsed = tomllib.loads(output)

        role = parsed["agents"]["code_reviewer"]
        assert "expert code reviewer" in role["description"]
        assert "code-review" in role["description"]
        assert role["nickname_candidates"] == ["Code Reviewer"]

    def test_does_not_emit_dangling_config_file(self, reviewer):
        output = to_codex_config(reviewer)
        parsed = tomllib.loads(output)

        assert "config_file" not in parsed["agents"]["code_reviewer"]

    def test_all_catalog_configs_are_valid_toml(self, catalog):
        for agent in catalog.list_all():
            output = to_codex_config(agent)
            parsed = tomllib.loads(output)
            role_name = agent.name.replace("-", "_")
            assert role_name in parsed["agents"]


class TestA2AAgentCardExport:
    def test_has_required_agent_card_fields(self, reviewer):
        output = to_a2a_agent_card(reviewer)
        card = json.loads(output)

        assert card["name"] == "Code Reviewer"
        assert card["description"] == reviewer.description
        assert card["version"] == reviewer.version
        assert card["supportedInterfaces"][0]["protocolBinding"] == "JSONRPC"
        assert card["supportedInterfaces"][0]["protocolVersion"] == "1.0"
        assert card["defaultInputModes"] == ["text/plain", "application/json"]
        assert card["defaultOutputModes"] == ["text/plain", "application/json"]

    def test_maps_agent_to_a2a_skill(self, reviewer):
        output = to_a2a_agent_card(reviewer)
        card = json.loads(output)
        skill = card["skills"][0]

        assert skill["id"] == "code-reviewer"
        assert skill["name"] == "Code Reviewer"
        assert skill["description"] == reviewer.description
        assert "code-review" in skill["tags"]
        assert skill["inputModes"] == ["text/plain", "application/json"]
        assert skill["outputModes"] == ["text/plain", "application/json"]

    def test_declares_only_supported_capabilities(self, reviewer):
        output = to_a2a_agent_card(reviewer)
        card = json.loads(output)

        assert card["capabilities"] == {
            "streaming": False,
            "pushNotifications": False,
            "extendedAgentCard": False,
        }
        assert "securitySchemes" not in card
        assert "securityRequirements" not in card

    def test_all_catalog_agent_cards_are_valid_json(self, catalog):
        for agent in catalog.list_all():
            output = to_a2a_agent_card(agent)
            card = json.loads(output)
            assert card["skills"]


class TestGeminiExport:
    def test_has_agent_config(self, reviewer):
        output = to_gemini(reviewer)
        assert "name: code_reviewer" in output  # Hyphens become underscores
        assert "instruction:" in output

    def test_has_model(self, reviewer):
        output = to_gemini(reviewer)
        assert "model:" in output

    def test_has_generate_config(self, reviewer):
        output = to_gemini(reviewer)
        assert "temperature:" in output
        assert "max_output_tokens:" in output

    def test_has_tools(self, reviewer):
        output = to_gemini(reviewer)
        assert "tools:" in output
        assert "filesystem" in output


class TestChatGPTExport:
    def test_has_system_prompt(self, reviewer):
        output = to_chatgpt(reviewer)
        assert "expert code reviewer" in output

    def test_has_companion_note(self, reviewer):
        output = to_chatgpt(reviewer)
        assert "combine with:" in output

    def test_has_source_footer(self, reviewer):
        output = to_chatgpt(reviewer)
        assert "Source: multi-agent catalog" in output


class TestRawExport:
    def test_is_just_prompt(self, reviewer):
        output = to_raw(reviewer)
        assert output.startswith("You are an expert code reviewer")
        assert "Source:" not in output
        assert "---" not in output


class TestExportAgent:
    def test_all_targets_available(self):
        assert set(EXPORTERS) == {
            "agentskill",
            "a2a-agent-card",
            "claude-code",
            "codex",
            "codex-config",
            "gemini",
            "chatgpt",
            "raw",
        }

    def test_unknown_target_raises(self, reviewer):
        with pytest.raises(ValueError, match="Unknown target"):
            export_agent(reviewer, "unknown")

    def test_write_to_file(self, reviewer, tmp_path):
        export_agent(reviewer, "claude-code", output_dir=tmp_path)
        output_file = tmp_path / "code-reviewer.md"
        assert output_file.exists()
        assert "code-reviewer" in output_file.read_text()

    def test_write_gemini_yaml(self, reviewer, tmp_path):
        export_agent(reviewer, "gemini", output_dir=tmp_path)
        output_file = tmp_path / "code-reviewer.yaml"
        assert output_file.exists()

    def test_write_codex_config_toml(self, reviewer, tmp_path):
        export_agent(reviewer, "codex-config", output_dir=tmp_path)
        output_file = tmp_path / "code-reviewer.toml"
        assert output_file.exists()
        parsed = tomllib.loads(output_file.read_text())
        assert parsed["agents"]["code_reviewer"]["nickname_candidates"] == ["Code Reviewer"]

    def test_write_a2a_agent_card_json(self, reviewer, tmp_path):
        export_agent(reviewer, "a2a-agent-card", output_dir=tmp_path)
        output_file = tmp_path / "code-reviewer.agent-card.json"
        assert output_file.exists()
        assert json.loads(output_file.read_text())["skills"][0]["id"] == "code-reviewer"

    def test_all_catalog_agents_export(self, catalog):
        """Every agent in the catalog should export cleanly to all formats."""
        for agent in catalog.list_all():
            for target in EXPORTERS:
                output = export_agent(agent, target)
                assert len(output) > 50, f"{agent.full_name} → {target} produced empty output"
