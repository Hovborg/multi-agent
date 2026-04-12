"""Orchestration patterns for composing multi-agent systems."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from multiagent.catalog import AgentDefinition


@dataclass
class PatternResult:
    """Result from running a pattern."""

    output: str
    agent_outputs: dict[str, str] = field(default_factory=dict)
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    pattern: str = ""


@dataclass
class PatternConfig:
    """Configuration for a pattern execution."""

    model: str = "claude-haiku-4-5"
    max_iterations: int = 5
    quality_threshold: float = 0.8
    timeout_seconds: int = 300
    verbose: bool = False


class Pattern:
    """Base class for orchestration patterns."""

    name: str = "base"
    description: str = ""

    def __init__(self, agents: list[AgentDefinition], config: PatternConfig | None = None):
        self.agents = agents
        self.config = config or PatternConfig()

    def run(self, task: str, context: dict[str, Any] | None = None) -> PatternResult:
        """Execute the pattern. Override in subclasses for framework-specific execution."""
        raise NotImplementedError(
            f"Pattern '{self.name}' requires a framework adapter. "
            f"Use: from multiagent.adapters import crewai; crewai.from_pattern(...)"
        )

    def describe(self) -> str:
        """Describe the pattern setup."""
        agent_names = [a.full_name for a in self.agents]
        return f"Pattern: {self.name}\nAgents: {', '.join(agent_names)}\nModel: {self.config.model}"


class SupervisorWorker(Pattern):
    """Central supervisor decomposes tasks and delegates to specialist workers."""

    name = "supervisor-worker"
    description = "A supervisor agent coordinates specialist workers for complex tasks."

    def __init__(
        self,
        supervisor: AgentDefinition,
        workers: list[AgentDefinition],
        config: PatternConfig | None = None,
    ):
        self.supervisor = supervisor
        self.workers = workers
        super().__init__([supervisor, *workers], config)


class Sequential(Pattern):
    """Linear pipeline: each agent processes and passes to the next."""

    name = "sequential"
    description = "Agents process in sequence, each building on the previous output."

    def __init__(self, steps: list[AgentDefinition], config: PatternConfig | None = None):
        self.steps = steps
        super().__init__(steps, config)


class Parallel(Pattern):
    """Fan-out: multiple agents work simultaneously, results merged."""

    name = "parallel"
    description = "Independent agents work concurrently, results are merged."

    def __init__(
        self,
        agents: list[AgentDefinition],
        merger: AgentDefinition | None = None,
        config: PatternConfig | None = None,
    ):
        self.merger = merger
        all_agents = list(agents)
        if merger:
            all_agents.append(merger)
        super().__init__(all_agents, config)


class Reflection(Pattern):
    """Iterative refinement: producer generates, critic reviews, repeat until quality threshold."""

    name = "reflection"
    description = "Iterative loop between producer and critic for quality-critical output."

    def __init__(
        self,
        producer: AgentDefinition,
        critic: AgentDefinition,
        config: PatternConfig | None = None,
    ):
        self.producer = producer
        self.critic = critic
        super().__init__([producer, critic], config)


class Handoff(Pattern):
    """Agent transfers full control to another agent with context."""

    name = "handoff"
    description = "Agents hand off control based on task requirements or escalation."

    def __init__(
        self,
        agents: list[AgentDefinition],
        routing_fn: Callable[[str], str] | None = None,
        config: PatternConfig | None = None,
    ):
        self.routing_fn = routing_fn
        super().__init__(agents, config)


class GroupChat(Pattern):
    """Multiple agents in shared conversation with dynamic speaker selection."""

    name = "group-chat"
    description = "Agents discuss in a shared conversation, selector picks next speaker."

    def __init__(
        self,
        agents: list[AgentDefinition],
        selector: Callable[[list[str]], str] | None = None,
        max_rounds: int = 10,
        config: PatternConfig | None = None,
    ):
        self.selector = selector
        self.max_rounds = max_rounds
        super().__init__(agents, config)


class DAG(Pattern):
    """Directed Acyclic Graph with conditional branching."""

    name = "dag"
    description = "Tasks flow through nodes with conditional edges."

    def __init__(
        self,
        nodes: dict[str, AgentDefinition],
        edges: list[tuple[str, str, Callable | None]],
        entry: str = "",
        config: PatternConfig | None = None,
    ):
        self.nodes = nodes
        self.edges = edges
        self.entry = entry or next(iter(nodes))
        super().__init__(list(nodes.values()), config)


class SplitAndMerge(Pattern):
    """Isolated parallel work merged at completion."""

    name = "split-and-merge"
    description = "Agents work in isolation (e.g., git worktrees), results merged at the end."

    def __init__(
        self,
        agents: list[AgentDefinition],
        merge_strategy: str = "concatenate",
        config: PatternConfig | None = None,
    ):
        self.merge_strategy = merge_strategy
        super().__init__(agents, config)


# Convenience constructors
class _PatternFactory:
    """Factory for creating pattern instances."""

    @staticmethod
    def supervisor_worker(
        supervisor: AgentDefinition,
        workers: list[AgentDefinition],
        **kwargs: Any,
    ) -> SupervisorWorker:
        config = PatternConfig(**kwargs) if kwargs else None
        return SupervisorWorker(supervisor, workers, config)

    @staticmethod
    def sequential(steps: list[AgentDefinition], **kwargs: Any) -> Sequential:
        config = PatternConfig(**kwargs) if kwargs else None
        return Sequential(steps, config)

    @staticmethod
    def parallel(
        agents: list[AgentDefinition],
        merger: AgentDefinition | None = None,
        **kwargs: Any,
    ) -> Parallel:
        config = PatternConfig(**kwargs) if kwargs else None
        return Parallel(agents, merger, config)

    @staticmethod
    def reflection(
        producer: AgentDefinition,
        critic: AgentDefinition,
        **kwargs: Any,
    ) -> Reflection:
        config = PatternConfig(**kwargs) if kwargs else None
        return Reflection(producer, critic, config)

    @staticmethod
    def handoff(agents: list[AgentDefinition], **kwargs: Any) -> Handoff:
        config = PatternConfig(**kwargs) if kwargs else None
        return Handoff(agents, config=config)

    @staticmethod
    def group_chat(
        agents: list[AgentDefinition],
        max_rounds: int = 10,
        **kwargs: Any,
    ) -> GroupChat:
        config = PatternConfig(**kwargs) if kwargs else None
        return GroupChat(agents, max_rounds=max_rounds, config=config)

    @staticmethod
    def dag(
        nodes: dict[str, AgentDefinition],
        edges: list[tuple[str, str, Callable | None]],
        entry: str = "",
        **kwargs: Any,
    ) -> DAG:
        config = PatternConfig(**kwargs) if kwargs else None
        return DAG(nodes, edges, entry, config)

    @staticmethod
    def split_and_merge(
        agents: list[AgentDefinition],
        merge_strategy: str = "concatenate",
        **kwargs: Any,
    ) -> SplitAndMerge:
        config = PatternConfig(**kwargs) if kwargs else None
        return SplitAndMerge(agents, merge_strategy, config)

    ALL_PATTERNS = {
        "supervisor-worker": SupervisorWorker,
        "sequential": Sequential,
        "parallel": Parallel,
        "reflection": Reflection,
        "handoff": Handoff,
        "group-chat": GroupChat,
        "dag": DAG,
        "split-and-merge": SplitAndMerge,
    }


patterns = _PatternFactory()
