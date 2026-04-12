"""Agent recommendation engine: describe your task, get the right agents and pattern."""

from __future__ import annotations

from dataclasses import dataclass, field

from multiagent.catalog import AgentDefinition, Catalog

# Keywords mapped to agent categories and specific agents
TASK_KEYWORDS: dict[str, list[str]] = {
    # Code tasks
    "review": ["code/code-reviewer"],
    "code review": ["code/code-reviewer", "code/security-auditor"],
    "pr review": ["code/code-reviewer", "code/pr-summarizer"],
    "generate code": ["code/code-generator"],
    "write code": ["code/code-generator"],
    "implement": ["code/code-generator"],
    "test": ["code/test-writer"],
    "write tests": ["code/test-writer"],
    "unit test": ["code/test-writer"],
    "refactor": ["code/refactorer"],
    "debug": ["code/debugger"],
    "fix bug": ["code/debugger"],
    "security": ["code/security-auditor"],
    "audit": ["code/security-auditor"],
    "documentation": ["code/documentation-writer"],
    "docs": ["code/documentation-writer"],
    "pr summary": ["code/pr-summarizer"],
    # Research tasks
    "research": ["research/deep-researcher"],
    "investigate": ["research/deep-researcher"],
    "scrape": ["research/web-scraper"],
    "extract data": ["research/web-scraper"],
    "fact check": ["research/fact-checker"],
    "verify": ["research/fact-checker"],
    "paper": ["research/paper-analyst"],
    "academic": ["research/paper-analyst"],
    "competitive": ["research/competitive-intel"],
    "market research": ["research/competitive-intel"],
    # Data tasks
    "analyze data": ["data/data-analyst"],
    "data analysis": ["data/data-analyst"],
    "sql": ["data/sql-generator"],
    "query": ["data/sql-generator"],
    "report": ["data/report-writer"],
    # DevOps tasks
    "ci/cd": ["devops/ci-cd-agent"],
    "pipeline": ["devops/ci-cd-agent"],
    "infrastructure": ["devops/infra-provisioner"],
    "terraform": ["devops/infra-provisioner"],
    "monitoring": ["devops/monitoring-agent"],
    "alert": ["devops/monitoring-agent"],
    "incident": ["devops/incident-responder"],
    # Content tasks
    "write": ["content/writer"],
    "article": ["content/writer"],
    "blog": ["content/writer"],
    "edit": ["content/editor"],
    "proofread": ["content/editor"],
    "translate": ["content/translator"],
    "seo": ["content/seo-optimizer"],
}

# Pattern recommendations based on task characteristics
PATTERN_RULES: list[tuple[list[str], str, str]] = [
    # (keywords, pattern, reason)
    (["review", "audit", "check"], "supervisor-worker", "Central reviewer coordinates specialists"),
    (["pipeline", "workflow", "process"], "sequential", "Step-by-step processing chain"),
    (["research", "multi-source", "compare"], "parallel", "Independent sources concurrently"),
    (["draft", "write", "generate"], "reflection", "Iterative refinement improves quality"),
    (["support", "route", "escalate"], "handoff", "Transfer control based on complexity"),
    (["brainstorm", "debate", "design"], "group-chat", "Multiple perspectives in discussion"),
    (["complex", "conditional", "branch"], "dag", "Conditional routing between steps"),
    (["refactor", "multi-file", "large"], "split-and-merge", "Isolated parallel work, merged"),
]


@dataclass
class Recommendation:
    """A recommended agent configuration for a task."""

    agents: list[AgentDefinition]
    pattern: str
    pattern_reason: str
    confidence: float  # 0.0 to 1.0
    alternatives: list[str] = field(default_factory=list)

    def describe(self) -> str:
        lines = [
            f"Recommended pattern: {self.pattern}",
            f"  Reason: {self.pattern_reason}",
            f"  Confidence: {self.confidence:.0%}",
            "  Agents:",
        ]
        for agent in self.agents:
            lines.append(f"    - {agent.full_name}: {agent.description}")
        if self.alternatives:
            lines.append(f"  Alternatives: {', '.join(self.alternatives)}")
        return "\n".join(lines)


class AgentRouter:
    """Recommend agents and patterns based on task description."""

    def __init__(self, catalog: Catalog | None = None):
        self.catalog = catalog or Catalog()

    def recommend(self, task: str) -> Recommendation:
        """Given a task description, recommend agents and an orchestration pattern."""
        task_lower = task.lower()

        # Find matching agents
        matched_agent_names: list[str] = []
        for keyword, agents in TASK_KEYWORDS.items():
            if keyword in task_lower:
                for agent_name in agents:
                    if agent_name not in matched_agent_names:
                        matched_agent_names.append(agent_name)

        # Fall back to catalog search if no keyword match
        if not matched_agent_names:
            search_results = self.catalog.search(task)
            matched_agent_names = [a.full_name for a in search_results[:3]]

        # Load agent definitions
        agents = []
        for name in matched_agent_names:
            try:
                agents.append(self.catalog.load(name))
            except KeyError:
                continue

        # Add companion agents
        if len(agents) == 1:
            companions = self.catalog.get_team_for(agents[0].full_name)
            for c in companions[:2]:
                if c.full_name not in matched_agent_names:
                    agents.append(c)

        # Recommend pattern
        pattern = "supervisor-worker"  # Default
        pattern_reason = "General-purpose coordination"
        best_score = 0

        for keywords, pat, reason in PATTERN_RULES:
            score = sum(1 for kw in keywords if kw in task_lower)
            if score > best_score:
                best_score = score
                pattern = pat
                pattern_reason = reason

        # Calculate confidence
        confidence = min(1.0, (len(agents) * 0.3) + (best_score * 0.2) + 0.1)

        # Find alternative patterns
        alternatives = []
        for keywords, pat, _ in PATTERN_RULES:
            if pat != pattern and any(kw in task_lower for kw in keywords):
                alternatives.append(pat)

        return Recommendation(
            agents=agents,
            pattern=pattern,
            pattern_reason=pattern_reason,
            confidence=confidence,
            alternatives=alternatives[:3],
        )
