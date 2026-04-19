"""Routing evaluation corpus and scoring helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from multiagent.catalog import Catalog
from multiagent.framework_targets import ROUTE_TARGETS
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
    forbidden_agents: tuple[str, ...] = ()
    expected_risk: dict[str, Any] | None = None
    expected_context: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RoutingEvalCase:
        expected_target = str(data["expected_target"])
        if expected_target not in ROUTE_TARGETS:
            raise ValueError(f"Unknown expected target: {expected_target}")
        return cls(
            id=str(data["id"]),
            task=str(data["task"]),
            expected_agents=tuple(str(agent) for agent in data["expected_agents"]),
            expected_pattern=str(data["expected_pattern"]),
            expected_target=expected_target,
            forbidden_agents=tuple(str(agent) for agent in data.get("forbidden_agents", [])),
            expected_risk=data.get("expected_risk"),
            expected_context=data.get("expected_context"),
        )


@dataclass(frozen=True)
class RoutingEvalResult:
    """Actual route compared with one expected corpus case."""

    case: RoutingEvalCase
    actual_agents: tuple[str, ...]
    actual_pattern: str
    actual_target: str
    actual_risk: dict[str, Any]
    actual_context: dict[str, Any]

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
    def forbidden_match(self) -> bool:
        return not set(self.case.forbidden_agents).intersection(self.actual_agents)

    @property
    def risk_match(self) -> bool:
        return _risk_matches(self.actual_risk, self.case.expected_risk)

    @property
    def context_match(self) -> bool:
        return _context_matches(self.actual_context, self.case.expected_context)

    @property
    def passed(self) -> bool:
        return (
            self.agent_match
            and self.pattern_match
            and self.target_match
            and self.forbidden_match
            and self.risk_match
            and self.context_match
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case.id,
            "task": self.case.task,
            "passed": self.passed,
            "expected_agents": list(self.case.expected_agents),
            "actual_agents": list(self.actual_agents),
            "agent_match": self.agent_match,
            "forbidden_agents": list(self.case.forbidden_agents),
            "forbidden_match": self.forbidden_match,
            "expected_pattern": self.case.expected_pattern,
            "actual_pattern": self.actual_pattern,
            "pattern_match": self.pattern_match,
            "expected_target": self.case.expected_target,
            "actual_target": self.actual_target,
            "target_match": self.target_match,
            "expected_risk": self.case.expected_risk or {},
            "actual_risk": self.actual_risk,
            "risk_match": self.risk_match,
            "expected_context": self.case.expected_context or {},
            "actual_context": self.actual_context,
            "context_match": self.context_match,
        }


@dataclass(frozen=True)
class RoutingThresholdFailure:
    """One routing metric that did not meet its configured threshold."""

    metric: str
    actual: float
    minimum: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric": self.metric,
            "actual": self.actual,
            "minimum": self.minimum,
        }


@dataclass(frozen=True)
class RoutingEvalThresholds:
    """Optional thresholds for aggregate routing scores."""

    pass_rate: float | None = None
    agent_match_rate: float | None = None
    pattern_match_rate: float | None = None
    target_match_rate: float | None = None
    forbidden_match_rate: float | None = None
    risk_match_rate: float | None = None
    context_match_rate: float | None = None

    def configured(self) -> dict[str, float]:
        """Return only thresholds that were explicitly configured."""
        return {
            metric: value
            for metric, value in {
                "pass_rate": self.pass_rate,
                "agent_match_rate": self.agent_match_rate,
                "pattern_match_rate": self.pattern_match_rate,
                "target_match_rate": self.target_match_rate,
                "forbidden_match_rate": self.forbidden_match_rate,
                "risk_match_rate": self.risk_match_rate,
                "context_match_rate": self.context_match_rate,
            }.items()
            if value is not None
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

    @property
    def scores(self) -> dict[str, float]:
        return {
            "agent_match_rate": self._match_rate("agent_match"),
            "pattern_match_rate": self._match_rate("pattern_match"),
            "target_match_rate": self._match_rate("target_match"),
            "forbidden_match_rate": self._match_rate("forbidden_match"),
            "risk_match_rate": self._match_rate("risk_match"),
            "context_match_rate": self._match_rate("context_match"),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "pass_rate": self.pass_rate,
            "scores": self.scores,
            "results": [result.to_dict() for result in self.results],
        }

    def threshold_failures(
        self,
        thresholds: RoutingEvalThresholds,
    ) -> tuple[RoutingThresholdFailure, ...]:
        """Return configured thresholds that the report does not satisfy."""
        actual_values = {"pass_rate": self.pass_rate, **self.scores}
        failures: list[RoutingThresholdFailure] = []
        for metric, minimum in thresholds.configured().items():
            actual = actual_values[metric]
            if actual < minimum:
                failures.append(
                    RoutingThresholdFailure(
                        metric=metric,
                        actual=actual,
                        minimum=minimum,
                    )
                )
        return tuple(failures)

    def _match_rate(self, field_name: str) -> float:
        if not self.total:
            return 0.0
        matches = sum(1 for result in self.results if getattr(result, field_name))
        return matches / self.total


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
                actual_risk=rec.risk,
                actual_context=rec.context,
            )
        )
    return RoutingEvalReport(results=tuple(results))


_RISK_RANK = {"none": 0, "low": 1, "medium": 2, "high": 3}
_CONTEXT_RANK = {"low": 0, "medium": 1, "high": 2}


def _risk_matches(actual: dict[str, Any], expected: dict[str, Any] | None) -> bool:
    if not expected:
        return True

    min_risk = expected.get("min_side_effect_risk")
    if min_risk is not None:
        actual_risk = str(actual.get("side_effect_risk", "none"))
        if _RISK_RANK.get(actual_risk, 0) < _RISK_RANK[str(min_risk)]:
            return False

    requires_review = expected.get("requires_human_review")
    if requires_review is not None and actual.get("requires_human_review") != requires_review:
        return False

    return True


def _context_matches(actual: dict[str, Any], expected: dict[str, Any] | None) -> bool:
    if not expected:
        return True

    min_context_risk = expected.get("min_context_size_risk")
    if min_context_risk is not None:
        actual_context_risk = str(actual.get("context_size_risk", "low"))
        if _CONTEXT_RANK.get(actual_context_risk, 0) < _CONTEXT_RANK[str(min_context_risk)]:
            return False

    loading = expected.get("loading")
    if loading is not None and actual.get("loading") != loading:
        return False

    return True
