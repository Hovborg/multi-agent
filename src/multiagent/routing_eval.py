"""Routing evaluation corpus and scoring helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from multiagent.catalog import Catalog
from multiagent.export import EXPORTERS
from multiagent.router import AgentRouter

DEFAULT_CORPUS_PATH = Path(__file__).with_name("routing_corpus.yaml")


@dataclass(frozen=True)
class RoutingEvalCase:
    """Expected route for one task prompt."""

    id: str
    task: str
    expected_agents: tuple[str, ...]
    expected_pattern: str
    expected_target: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RoutingEvalCase:
        expected_target = str(data["expected_target"])
        if expected_target not in EXPORTERS:
            raise ValueError(f"Unknown expected target: {expected_target}")
        return cls(
            id=str(data["id"]),
            task=str(data["task"]),
            expected_agents=tuple(str(agent) for agent in data["expected_agents"]),
            expected_pattern=str(data["expected_pattern"]),
            expected_target=expected_target,
        )


@dataclass(frozen=True)
class RoutingEvalResult:
    """Actual route compared with one expected corpus case."""

    case: RoutingEvalCase
    actual_agents: tuple[str, ...]
    actual_pattern: str
    actual_target: str

    @property
    def agent_match(self) -> bool:
        return set(self.case.expected_agents).issubset(self.actual_agents)

    @property
    def pattern_match(self) -> bool:
        return self.actual_pattern == self.case.expected_pattern

    @property
    def target_match(self) -> bool:
        return self.actual_target == self.case.expected_target

    @property
    def passed(self) -> bool:
        return self.agent_match and self.pattern_match and self.target_match

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case.id,
            "task": self.case.task,
            "passed": self.passed,
            "expected_agents": list(self.case.expected_agents),
            "actual_agents": list(self.actual_agents),
            "agent_match": self.agent_match,
            "expected_pattern": self.case.expected_pattern,
            "actual_pattern": self.actual_pattern,
            "pattern_match": self.pattern_match,
            "expected_target": self.case.expected_target,
            "actual_target": self.actual_target,
            "target_match": self.target_match,
        }


@dataclass(frozen=True)
class RoutingEvalReport:
    """Aggregate routing evaluation report."""

    results: tuple[RoutingEvalResult, ...]

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed(self) -> int:
        return sum(1 for result in self.results if result.passed)

    @property
    def failed(self) -> int:
        return self.total - self.passed

    @property
    def pass_rate(self) -> float:
        if not self.total:
            return 0.0
        return self.passed / self.total

    @property
    def failures(self) -> tuple[RoutingEvalResult, ...]:
        return tuple(result for result in self.results if not result.passed)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "pass_rate": self.pass_rate,
            "results": [result.to_dict() for result in self.results],
        }


def load_routing_corpus(path: Path | str | None = None) -> list[RoutingEvalCase]:
    """Load routing eval cases from YAML."""
    corpus_path = Path(path) if path else DEFAULT_CORPUS_PATH
    data = yaml.safe_load(corpus_path.read_text(encoding="utf-8")) or {}
    raw_cases = data.get("cases", [])
    return [RoutingEvalCase.from_dict(case) for case in raw_cases]


def evaluate_routing_corpus(
    catalog: Catalog | None = None,
    cases: list[RoutingEvalCase] | None = None,
) -> RoutingEvalReport:
    """Evaluate router output against the routing corpus."""
    router = AgentRouter(catalog or Catalog())
    eval_cases = cases or load_routing_corpus()
    results = []
    for case in eval_cases:
        rec = router.recommend(case.task)
        results.append(
            RoutingEvalResult(
                case=case,
                actual_agents=tuple(agent.full_name for agent in rec.agents),
                actual_pattern=rec.pattern,
                actual_target=rec.suggested_target,
            )
        )
    return RoutingEvalReport(results=tuple(results))
