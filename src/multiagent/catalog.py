"""Agent catalog: load, search, and compose agent definitions from YAML files."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from multiagent.validation import CatalogError, CatalogValidationError, load_agent_data

CATALOG_DIR = Path(__file__).resolve().parent / "catalog_data"


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
    orchestration: dict[str, Any] = field(default_factory=dict)
    safety: dict[str, Any] = field(default_factory=dict)
    observability: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)
    protocols: dict[str, Any] = field(default_factory=dict)
    _raw: dict[str, Any] = field(default=None, repr=False)

    @classmethod
    def from_yaml(cls, path: Path) -> AgentDefinition:
        """Load an agent definition from a YAML file."""
        data = load_agent_data(path)
        cost_data = data.get("cost_profile", {})
        cost_profile = CostProfile(
            input_tokens_per_run=cost_data.get("input_tokens_per_run", 2000),
            output_tokens_per_run=cost_data.get("output_tokens_per_run", 2000),
            recommended_models=cost_data.get("recommended_models", {}),
            estimated_cost=cost_data.get("estimated_cost", {}),
        )
        return cls(
            name=data["name"],
            version=str(data.get("version", "1.0")),
            description=data.get("description", ""),
            category=data.get("category", ""),
            tags=data.get("tags", []),
            system_prompt=data.get("system_prompt", ""),
            tools=data.get("tools", []),
            parameters=data.get("parameters", {}),
            cost_profile=cost_profile,
            works_with=data.get("works_with", []),
            recommended_patterns=data.get("recommended_patterns", []),
            orchestration=data.get("orchestration", {}),
            safety=data.get("safety", {}),
            observability=data.get("observability", {}),
            outputs=data.get("outputs", {}),
            context=data.get("context", {}),
            protocols=data.get("protocols", {}),
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
        if not self._dir.is_dir():
            raise CatalogValidationError(f"Catalog directory does not exist: {self._dir}")
        for yaml_file in sorted(self._dir.rglob("*.yaml")):
            # Skip internal directories (enhancements, templates, etc.)
            if any(part.startswith("_") for part in yaml_file.relative_to(self._dir).parts):
                continue
            agent = AgentDefinition.from_yaml(yaml_file)
            if agent.full_name in self._agents:
                raise CatalogValidationError(
                    f"Duplicate agent '{agent.full_name}' in {yaml_file}"
                )
            self._agents[agent.full_name] = agent
        self._loaded = True

    def load(self, name: str) -> AgentDefinition:
        """Load a single agent by name (e.g., 'code/code-reviewer')."""
        self._ensure_loaded()
        if name in self._agents:
            return self._agents[name]
        matches = [
            agent
            for key, agent in self._agents.items()
            if key.endswith(f"/{name}") or agent.name == name
        ]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            candidates = ", ".join(agent.full_name for agent in matches)
            raise CatalogValidationError(f"Ambiguous agent '{name}'. Matches: {candidates}")
        raise CatalogError(
            f"Agent '{name}' not found in catalog. Available: {list(self._agents)}"
        )

    def validate(self) -> list[str]:
        """Return cross-definition validation errors for the complete catalog."""
        self._ensure_loaded()
        known_agents = set(self._agents)
        errors: list[str] = []
        for agent in self.list_all():
            for reference in agent.works_with:
                if reference not in known_agents:
                    errors.append(
                        f"{agent.full_name}: unknown works_with reference '{reference}'"
                    )
        return errors

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
