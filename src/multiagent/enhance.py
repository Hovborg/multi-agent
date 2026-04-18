"""Smart prompt enhancement system.

Applies research-backed prompt engineering techniques to agent definitions.
Based on findings from Anthropic, OpenAI, and academic research (2025-2026):
- Plan-and-reflect reasoning (+20% on SWE-bench)
- 5-level error recovery hierarchy
- Self-evaluation verification checklists
- Confidence calibration (reduces hallucination 40-60%)
- Tool selection heuristics
- Failure mode prevention
- Active context management
- Information priority hierarchies

Enhancements are composable YAML blocks in catalog/_enhancements/.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from multiagent.catalog import AgentDefinition

ENHANCEMENTS_DIR = Path(__file__).resolve().parent.parent.parent / "catalog" / "_enhancements"

# Default enhancement profiles per category
CATEGORY_PROFILES: dict[str, list[str]] = {
    "code": [
        "reasoning",
        "error_recovery",
        "verification",
        "tool_discipline",
        "failure_modes",
    ],
    "research": [
        "reasoning",
        "confidence",
        "information_priority",
        "verification",
        "context_management",
    ],
    "data": [
        "reasoning",
        "verification",
        "confidence",
        "tool_discipline",
    ],
    "devops": [
        "reasoning",
        "error_recovery",
        "verification",
        "tool_discipline",
    ],
    "content": [
        "reasoning",
        "verification",
        "failure_modes",
        "context_management",
    ],
    "finance": [
        "reasoning",
        "confidence",
        "verification",
        "information_priority",
        "failure_modes",
    ],
    "legal": [
        "reasoning",
        "confidence",
        "verification",
        "information_priority",
        "failure_modes",
    ],
    "support": [
        "reasoning",
        "error_recovery",
        "confidence",
        "context_management",
    ],
    "personal": [
        "reasoning",
        "verification",
        "context_management",
    ],
    "security": [
        "reasoning",
        "error_recovery",
        "verification",
        "information_priority",
        "confidence",
    ],
    "orchestration": [
        "reasoning",
        "error_recovery",
        "tool_discipline",
        "context_management",
    ],
}

# All available enhancements (applied when profile="all")
ALL_ENHANCEMENTS = [
    "reasoning",
    "error_recovery",
    "verification",
    "confidence",
    "tool_discipline",
    "failure_modes",
    "context_management",
    "information_priority",
]


def _load_enhancement(name: str, enhancements_dir: Path | None = None) -> str:
    """Load a single enhancement block from YAML."""
    d = enhancements_dir or ENHANCEMENTS_DIR
    path = d / f"{name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Enhancement '{name}' not found at {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data.get("prompt_block", "").strip()


def _load_all_enhancements(
    names: list[str],
    enhancements_dir: Path | None = None,
) -> list[str]:
    """Load multiple enhancement blocks."""
    blocks = []
    for name in names:
        try:
            block = _load_enhancement(name, enhancements_dir)
            if block:
                blocks.append(block)
        except FileNotFoundError:
            continue
    return blocks


def enhance_prompt(
    base_prompt: str,
    enhancements: list[str] | None = None,
    category: str = "",
    profile: str = "category",
    enhancements_dir: Path | None = None,
) -> str:
    """Enhance a system prompt with smart prompt blocks.

    Args:
        base_prompt: The original system prompt
        enhancements: Explicit list of enhancement names to apply
        category: Agent category (used for default profile selection)
        profile: "category" (default for category), "all", "minimal", or "none"
        enhancements_dir: Custom directory for enhancement YAML files

    Returns:
        Enhanced system prompt with blocks appended
    """
    if profile == "none":
        return base_prompt

    if enhancements:
        enhancement_names = enhancements
    elif profile == "all":
        enhancement_names = ALL_ENHANCEMENTS
    elif profile == "minimal":
        enhancement_names = ["reasoning", "verification"]
    else:
        enhancement_names = CATEGORY_PROFILES.get(category, ["reasoning", "verification"])

    blocks = _load_all_enhancements(enhancement_names, enhancements_dir)

    if not blocks:
        return base_prompt

    enhanced = base_prompt.rstrip() + "\n\n" + "\n\n".join(blocks)
    return enhanced


def enhance_agent(
    agent: AgentDefinition,
    enhancements: list[str] | None = None,
    profile: str = "category",
    enhancements_dir: Path | None = None,
) -> AgentDefinition:
    """Return a new AgentDefinition with an enhanced system prompt.

    The original agent is not modified.

    Args:
        agent: The agent definition to enhance
        enhancements: Explicit list of enhancement names
        profile: "category", "all", "minimal", or "none"
        enhancements_dir: Custom directory for enhancement files

    Example:
        from multiagent import Catalog
        from multiagent.enhance import enhance_agent

        catalog = Catalog()
        agent = catalog.load("code/code-reviewer")
        smart_agent = enhance_agent(agent, profile="all")
        print(smart_agent.system_prompt)  # Includes all enhancement blocks
    """
    enhanced_prompt = enhance_prompt(
        agent.system_prompt,
        enhancements=enhancements,
        category=agent.category,
        profile=profile,
        enhancements_dir=enhancements_dir,
    )

    # Create a copy with the enhanced prompt
    return AgentDefinition(
        name=agent.name,
        version=agent.version,
        description=agent.description,
        category=agent.category,
        tags=agent.tags,
        system_prompt=enhanced_prompt,
        tools=agent.tools,
        parameters=agent.parameters,
        cost_profile=agent.cost_profile,
        works_with=agent.works_with,
        recommended_patterns=agent.recommended_patterns,
        orchestration=agent.orchestration,
        safety=agent.safety,
        observability=agent.observability,
        outputs=agent.outputs,
        context=agent.context,
        protocols=agent.protocols,
        _raw=agent._raw,
    )


def list_enhancements(enhancements_dir: Path | None = None) -> list[dict[str, Any]]:
    """List all available enhancement blocks."""
    d = enhancements_dir or ENHANCEMENTS_DIR
    results = []
    for path in sorted(d.glob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue
        if not isinstance(data, dict):
            continue
        results.append({
            "name": data.get("name", path.stem),
            "description": data.get("description", ""),
            "category": data.get("category", ""),
        })
    return results
