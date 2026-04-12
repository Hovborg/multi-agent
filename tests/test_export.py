"""Tests for the export module."""

from pathlib import Path

import pytest

from multiagent.catalog import Catalog
from multiagent.export import (
    EXPORTERS,
    export_agent,
    to_chatgpt,
    to_claude_code,
    to_codex,
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
        assert "TRIGGER THIS SKILL WHEN:" in output

    def test_has_system_prompt(self, reviewer):
        output = to_claude_code(reviewer)
        assert "expert code reviewer" in output

    def test_has_tools_section(self, reviewer):
        output = to_claude_code(reviewer)
        assert "## Tools" in output
        assert "filesystem" in output

    def test_has_related_agents(self, reviewer):
        output = to_claude_code(reviewer)
        assert "## Related Agents" in output
        assert "code/test-writer" in output


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
        assert set(EXPORTERS) == {"claude-code", "codex", "gemini", "chatgpt", "raw"}

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

    def test_all_catalog_agents_export(self, catalog):
        """Every agent in the catalog should export cleanly to all formats."""
        for agent in catalog.list_all():
            for target in EXPORTERS:
                output = export_agent(agent, target)
                assert len(output) > 50, f"{agent.full_name} → {target} produced empty output"
