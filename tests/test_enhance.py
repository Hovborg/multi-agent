"""Tests for the smart prompt enhancement system."""

from pathlib import Path

import pytest

from multiagent.catalog import Catalog
from multiagent.enhance import (
    ALL_ENHANCEMENTS,
    CATEGORY_PROFILES,
    enhance_agent,
    enhance_prompt,
    list_enhancements,
)

CATALOG_DIR = Path(__file__).resolve().parent.parent / "catalog"


@pytest.fixture
def catalog():
    return Catalog(CATALOG_DIR)


@pytest.fixture
def reviewer(catalog):
    return catalog.load("code/code-reviewer")


class TestEnhancePrompt:
    def test_adds_reasoning_block(self, reviewer):
        enhanced = enhance_prompt(reviewer.system_prompt, enhancements=["reasoning"])
        assert "<reasoning>" in enhanced
        assert "plan your approach" in enhanced
        assert reviewer.system_prompt in enhanced

    def test_adds_multiple_blocks(self, reviewer):
        enhanced = enhance_prompt(
            reviewer.system_prompt, enhancements=["reasoning", "verification"]
        )
        assert "<reasoning>" in enhanced
        assert "<verification>" in enhanced

    def test_profile_none_returns_original(self, reviewer):
        enhanced = enhance_prompt(reviewer.system_prompt, profile="none")
        assert enhanced == reviewer.system_prompt

    def test_profile_minimal(self, reviewer):
        enhanced = enhance_prompt(reviewer.system_prompt, profile="minimal")
        assert "<reasoning>" in enhanced
        assert "<verification>" in enhanced

    def test_profile_all(self, reviewer):
        enhanced = enhance_prompt(reviewer.system_prompt, profile="all")
        for name in ALL_ENHANCEMENTS:
            assert f"<{name}>" in enhanced or name.replace("_", "") in enhanced.lower()

    def test_category_profile_code(self, reviewer):
        enhanced = enhance_prompt(
            reviewer.system_prompt, category="code", profile="category"
        )
        assert "<reasoning>" in enhanced
        assert "<error_recovery>" in enhanced

    def test_category_profile_research(self):
        enhanced = enhance_prompt("Base prompt.", category="research", profile="category")
        assert "<confidence>" in enhanced
        assert "<information_priority>" in enhanced

    def test_unknown_enhancement_skipped(self, reviewer):
        enhanced = enhance_prompt(
            reviewer.system_prompt, enhancements=["reasoning", "nonexistent"]
        )
        assert "<reasoning>" in enhanced


class TestEnhanceAgent:
    def test_returns_new_agent(self, reviewer):
        enhanced = enhance_agent(reviewer, profile="all")
        assert enhanced is not reviewer
        assert enhanced.name == reviewer.name
        assert enhanced.category == reviewer.category

    def test_enhanced_prompt_differs(self, reviewer):
        enhanced = enhance_agent(reviewer, profile="all")
        assert len(enhanced.system_prompt) > len(reviewer.system_prompt)
        assert "<reasoning>" in enhanced.system_prompt

    def test_original_not_modified(self, reviewer):
        original_prompt = reviewer.system_prompt
        enhance_agent(reviewer, profile="all")
        assert reviewer.system_prompt == original_prompt

    def test_all_categories_have_profiles(self, catalog):
        for category in catalog.list_categories():
            assert category in CATEGORY_PROFILES, f"Missing profile for {category}"

    def test_enhance_every_agent(self, catalog):
        """Every agent should enhance cleanly with its category profile."""
        for agent in catalog.list_all():
            enhanced = enhance_agent(agent, profile="category")
            assert len(enhanced.system_prompt) > len(agent.system_prompt)


class TestListEnhancements:
    def test_lists_all(self):
        available = list_enhancements()
        assert len(available) >= 8
        names = [e["name"] for e in available]
        assert "reasoning" in names
        assert "verification" in names

    def test_has_descriptions(self):
        available = list_enhancements()
        for e in available:
            assert e["description"] != ""
