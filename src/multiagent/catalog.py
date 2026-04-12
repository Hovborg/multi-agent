"""Agent catalog: load, search, and compose agent definitions from YAML files."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

CATALOG_DIR = Path(__file__).resolve().parent.parent.parent / "catalog"


@dataclass
class CostProfile:
    """Cost estimation data for an agent."""

    input_tokens_per_run: int = 2000
    output_tokens_per_run: int = 2000
    recommended_models: dict[str, str] = field(default_factory=dict)
    estimated_cost: dict[str, float] = field(default_factory=dict)


@dataclass
class AgentDefinition:
    """A single agent loaded from the catalog."""

    name: str
    version: str
    description: str
    category: str
    tags: list[str]
    system_prompt: str
    tools: list[dict[str, Any]]
    parameters: dict[str, Any]
    cost_profile: CostProfile
    works_with: list[str]
    recommended_patterns: list[dict[str, str]]
    _raw: dict[str, Any] = field(default=None, repr=False)

    @classmethod
    def from_yaml(cls, path: Path) -> AgentDefinition:
        """Load an agent definition from a YAML file."""
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        cost_data = data.get("cost_profile", {})
        cost_profile = CostProfile(
            input_tokens_per_run=cost_data.get("input_tokens_per_run", 2000),
            output_tokens_per_run=cost_data.get("output_tokens_per_run", 2000),
            recommended_models=cost_data.get("recommended_models", {}),
            estimated_cost=cost_data.get("estimated_cost", {}),
        )
        return cls(
            name=data["name"],
            version=data.get("version", "1.0"),
            description=data.get("description", ""),
            category=data.get("category", ""),
            tags=data.get("tags", []),
            system_prompt=data.get("system_prompt", ""),
            tools=data.get("tools", []),
            parameters=data.get("parameters", {}),
            cost_profile=cost_profile,
            works_with=data.get("works_with", []),
            recommended_patterns=data.get("recommended_patterns", []),
            _raw=data,
        )

    @property
    def full_name(self) -> str:
        return f"{self.category}/{self.name}"


class Catalog:
    """Load and search the agent catalog."""

    def __init__(self, catalog_dir: Path | str | None = None):
        self._dir = Path(catalog_dir) if catalog_dir else CATALOG_DIR
        self._agents: dict[str, AgentDefinition] = {}
        self._loaded = False

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        for yaml_file in self._dir.rglob("*.yaml"):
            try:
                agent = AgentDefinition.from_yaml(yaml_file)
                self._agents[agent.full_name] = agent
            except (yaml.YAMLError, KeyError):
                continue
        self._loaded = True

    def load(self, name: str) -> AgentDefinition:
        """Load a single agent by name (e.g., 'code/code-reviewer')."""
        self._ensure_loaded()
        if name in self._agents:
            return self._agents[name]
        # Try partial match
        for key, agent in self._agents.items():
            if key.endswith(f"/{name}") or agent.name == name:
                return agent
        raise KeyError(f"Agent '{name}' not found in catalog. Available: {list(self._agents)}")

    def load_team(self, names: list[str]) -> list[AgentDefinition]:
        """Load multiple agents as a team."""
        return [self.load(name) for name in names]

    def search(self, query: str) -> list[AgentDefinition]:
        """Search agents by name, description, or tags. Matches all query words."""
        self._ensure_loaded()
        words = query.lower().split()
        results = []
        for agent in self._agents.values():
            searchable = f"{agent.name} {agent.description} {' '.join(agent.tags)}".lower()
            if all(w in searchable for w in words):
                results.append(agent)
        return sorted(results, key=lambda a: a.full_name)

    def list_all(self) -> list[AgentDefinition]:
        """List all agents in the catalog."""
        self._ensure_loaded()
        return sorted(self._agents.values(), key=lambda a: a.full_name)

    def list_categories(self) -> list[str]:
        """List all available categories."""
        self._ensure_loaded()
        return sorted({a.category for a in self._agents.values()})

    def by_category(self, category: str) -> list[AgentDefinition]:
        """Get all agents in a category."""
        self._ensure_loaded()
        return sorted(
            [a for a in self._agents.values() if a.category == category],
            key=lambda a: a.name,
        )

    def get_team_for(self, agent_name: str) -> list[AgentDefinition]:
        """Get all agents that work well with a given agent."""
        agent = self.load(agent_name)
        team = []
        for companion_name in agent.works_with:
            try:
                team.append(self.load(companion_name))
            except KeyError:
                continue
        return team

    def __len__(self) -> int:
        self._ensure_loaded()
        return len(self._agents)

    def __repr__(self) -> str:
        return f"Catalog({len(self)} agents, dir={self._dir})"
