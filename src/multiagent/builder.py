"""Interactive team builder wizard.

Guides users through composing multi-agent teams step by step:
1. Describe your task → get agent recommendations
2. Select/modify agents
3. Choose orchestration pattern
4. Pick enhancement profile
5. Choose model and see cost estimate
6. Export to your platform
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from multiagent.catalog import AgentDefinition
from multiagent.cost import MODEL_PRICING, CostEstimator
from multiagent.enhance import enhance_agent
from multiagent.export import export_agent
from multiagent.visualize import visualize_team


@dataclass
class TeamConfig:
    """Configuration produced by the team builder."""

    agents: list[AgentDefinition] = field(default_factory=list)
    pattern: str = "supervisor-worker"
    enhancement_profile: str = "category"
    model: str = "claude-haiku-4-5"
    export_target: str = "raw"
    task_description: str = ""

    @property
    def agent_names(self) -> list[str]:
        return [a.full_name for a in self.agents]

    def estimate_cost(self) -> float:
        """Get estimated cost per run."""
        if not self.agents:
            return 0.0
        est = CostEstimator.estimate_team(self.agents, model=self.model)
        return est.estimates[0].cost_usd if est.estimates else 0.0

    def get_diagram(self) -> str:
        """Get mermaid diagram for the team."""
        if len(self.agents) < 2:
            return ""
        return visualize_team(self.agents, self.pattern)

    def get_enhanced_agents(self) -> list[AgentDefinition]:
        """Get all agents with enhancements applied."""
        return [enhance_agent(a, profile=self.enhancement_profile) for a in self.agents]

    def export_all(self, output_dir: Path) -> list[Path]:
        """Export all enhanced agents to files."""
        output_dir.mkdir(parents=True, exist_ok=True)
        paths = []
        for agent in self.get_enhanced_agents():
            export_agent(agent, self.export_target, output_dir)
            ext = {"claude-code": ".md", "codex": ".md", "gemini": ".yaml"}.get(
                self.export_target, ".txt"
            )
            paths.append(output_dir / f"{agent.name}{ext}")
        return paths

    def summary(self) -> str:
        """Generate a human-readable summary of the team configuration."""
        lines = [
            "Team Configuration",
            f"{'='*50}",
            f"Task: {self.task_description or '(not specified)'}",
            f"Pattern: {self.pattern}",
            f"Enhancement: {self.enhancement_profile}",
            f"Model: {self.model}",
            f"Export: {self.export_target}",
            "",
            f"Agents ({len(self.agents)}):",
        ]
        for a in self.agents:
            lines.append(f"  - {a.full_name}: {a.description}")
        cost = self.estimate_cost()
        cost_str = f"${cost:.4f}" if cost > 0 else "free (local model)"
        lines.append(f"\nEstimated cost: {cost_str}/run")
        return "\n".join(lines)


PATTERNS = [
    ("supervisor-worker", "Central agent delegates to specialists"),
    ("sequential", "Linear pipeline: A → B → C"),
    ("parallel", "Fan-out: agents work simultaneously"),
    ("reflection", "Producer/critic loop for quality"),
    ("handoff", "Agent transfers control with context"),
    ("group-chat", "Shared conversation, dynamic speakers"),
]

ENHANCEMENT_PROFILES = [
    ("none", "No enhancements — base prompt only"),
    ("minimal", "Reasoning + verification"),
    ("category", "Tuned for agent category (recommended)"),
    ("all", "All 8 enhancement blocks"),
]

EXPORT_TARGETS = [
    ("claude-code", "Claude Code (.agents/ skills)"),
    ("codex", "OpenAI Codex / OpenClaw (AGENTS.md)"),
    ("gemini", "Google Gemini / ADK (YAML)"),
    ("chatgpt", "ChatGPT (Custom GPT instructions)"),
    ("raw", "Plain system prompt (any LLM)"),
]


def get_popular_models() -> list[tuple[str, str]]:
    """Get models sorted by price (cheapest first)."""
    models = []
    for name, pricing in MODEL_PRICING.items():
        if pricing["input"] == 0 and pricing["output"] == 0:
            label = f"{name} (free — local)"
        else:
            cost_1k = (1000 / 1_000_000 * pricing["input"]) + (
                1000 / 1_000_000 * pricing["output"]
            )
            label = f"{name} (${cost_1k:.4f}/1K tokens)"
        models.append((name, label))
    return sorted(models, key=lambda m: MODEL_PRICING[m[0]].get("input", 0))
