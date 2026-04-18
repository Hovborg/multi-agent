"""Agent recommendation engine: describe your task, get the right agents and pattern."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from multiagent.catalog import AgentDefinition, Catalog


@dataclass(frozen=True)
class TaskRule:
    """Weighted phrase rule for routing a task to one or more catalog agents."""

    phrase: str
    agents: tuple[str, ...]
    weight: int
    reason: str


@dataclass(frozen=True)
class TargetRule:
    """Weighted phrase rule for selecting an export target."""

    phrase: str
    target: str
    weight: int
    reason: str


@dataclass(frozen=True)
class SuppressionRule:
    """Phrase rule for suppressing agents when a prompt explicitly excludes work."""

    phrase: str
    agents: tuple[str, ...]
    reason: str


TASK_RULES: tuple[TaskRule, ...] = (
    # Code tasks
    TaskRule("code review", ("code/code-reviewer", "code/security-auditor"), 8, "code review"),
    TaskRule("pr review", ("code/code-reviewer", "code/pr-summarizer"), 8, "PR review"),
    TaskRule("pull request", ("code/code-reviewer", "code/pr-summarizer"), 7, "pull request"),
    TaskRule("pr", ("code/code-reviewer",), 4, "PR shorthand"),
    TaskRule("review", ("code/code-reviewer",), 2, "review request"),
    TaskRule("gennemgå", ("code/code-reviewer",), 7, "Danish review request"),
    TaskRule("generate code", ("code/code-generator",), 8, "code generation"),
    TaskRule("write code", ("code/code-generator",), 8, "code generation"),
    TaskRule("implement", ("code/code-generator",), 6, "implementation"),
    TaskRule("missing tests", ("code/test-writer",), 8, "missing tests"),
    TaskRule("manglende tests", ("code/test-writer",), 8, "Danish missing tests"),
    TaskRule("write tests", ("code/test-writer",), 8, "test writing"),
    TaskRule("skriv tests", ("code/test-writer",), 8, "Danish test writing"),
    TaskRule("unit tests", ("code/test-writer",), 7, "unit tests"),
    TaskRule("unit test", ("code/test-writer",), 7, "unit test"),
    TaskRule("tests", ("code/test-writer",), 5, "tests"),
    TaskRule("test", ("code/test-writer",), 4, "test"),
    TaskRule("refactor", ("code/refactorer",), 7, "refactoring"),
    TaskRule("debug", ("code/debugger",), 7, "debugging"),
    TaskRule("fix bug", ("code/debugger",), 7, "bug fixing"),
    TaskRule("security audit", ("code/security-auditor",), 8, "security audit"),
    TaskRule("security", ("code/security-auditor",), 4, "security"),
    TaskRule("documentation", ("code/documentation-writer",), 6, "documentation"),
    TaskRule("docs", ("code/documentation-writer",), 5, "documentation"),
    TaskRule("pr summary", ("code/pr-summarizer",), 8, "PR summary"),
    # Research tasks
    TaskRule("research", ("research/deep-researcher",), 7, "research"),
    TaskRule("undersøg", ("research/deep-researcher",), 7, "Danish investigation"),
    TaskRule("investigate", ("research/deep-researcher",), 7, "investigation"),
    TaskRule("scrape", ("research/web-scraper",), 7, "web scraping"),
    TaskRule("extract data", ("research/web-scraper",), 7, "data extraction"),
    TaskRule("fact check", ("research/fact-checker",), 8, "fact checking"),
    TaskRule("faktatjek", ("research/fact-checker",), 8, "Danish fact checking"),
    TaskRule("kilderne", ("research/fact-checker",), 5, "Danish source checking"),
    TaskRule("verify", ("research/fact-checker",), 5, "verification"),
    TaskRule("paper", ("research/paper-analyst",), 6, "paper analysis"),
    TaskRule("academic", ("research/paper-analyst",), 6, "academic analysis"),
    TaskRule("competitive", ("research/competitive-intel",), 6, "competitive intelligence"),
    TaskRule("market research", ("research/competitive-intel",), 8, "market research"),
    TaskRule("markedet", ("research/competitive-intel",), 6, "Danish market research"),
    # Data tasks
    TaskRule("analyze data", ("data/data-analyst",), 8, "data analysis"),
    TaskRule("data analysis", ("data/data-analyst",), 8, "data analysis"),
    TaskRule("sql", ("data/sql-generator",), 7, "SQL"),
    TaskRule("query", ("data/sql-generator",), 5, "query generation"),
    TaskRule("report", ("data/report-writer",), 4, "reporting"),
    # DevOps tasks
    TaskRule("ci/cd", ("devops/ci-cd-agent",), 8, "CI/CD"),
    TaskRule("pipeline", ("devops/ci-cd-agent",), 5, "pipeline"),
    TaskRule("infrastructure", ("devops/infra-provisioner",), 6, "infrastructure"),
    TaskRule("terraform", ("devops/infra-provisioner",), 8, "Terraform"),
    TaskRule("monitoring", ("devops/monitoring-agent",), 7, "monitoring"),
    TaskRule("alert", ("devops/monitoring-agent",), 5, "alerting"),
    TaskRule("incident", ("devops/incident-responder",), 6, "incident response"),
    # Content tasks. Keep these contextual: bare "write" is too broad for code tasks.
    TaskRule("blog post", ("content/writer",), 8, "blog post"),
    TaskRule("write blog", ("content/writer",), 8, "blog writing"),
    TaskRule("skriv", ("content/writer",), 4, "Danish writing"),
    TaskRule("blogindlæg", ("content/writer",), 8, "Danish blog post"),
    TaskRule("write article", ("content/writer",), 8, "article writing"),
    TaskRule("draft article", ("content/writer",), 7, "article drafting"),
    TaskRule("article", ("content/writer",), 5, "article"),
    TaskRule("newsletter", ("content/writer",), 6, "newsletter"),
    TaskRule("content", ("content/writer",), 5, "content"),
    TaskRule("edit a blog post", ("content/editor",), 8, "blog editing"),
    TaskRule("edit existing blog", ("content/editor",), 8, "blog editing"),
    TaskRule("blog copy", ("content/editor",), 8, "blog copy editing"),
    TaskRule("rediger", ("content/editor",), 7, "Danish editing"),
    TaskRule("edit blog", ("content/editor",), 7, "blog editing"),
    TaskRule("edit article", ("content/editor",), 7, "article editing"),
    TaskRule("proofread", ("content/editor",), 7, "proofreading"),
    TaskRule("translate", ("content/translator",), 7, "translation"),
    TaskRule("oversæt", ("content/translator",), 7, "Danish translation"),
    TaskRule("nyhedsbrevet", ("content/writer",), 5, "Danish newsletter"),
    TaskRule("seo", ("content/seo-optimizer",), 7, "SEO"),
    # Finance tasks
    TaskRule("trading", ("finance/trading-analyst",), 7, "trading analysis"),
    TaskRule("portfolio", ("finance/portfolio-optimizer",), 7, "portfolio optimization"),
    TaskRule("financial", ("finance/financial-reporter",), 6, "financial reporting"),
    TaskRule("fraud", ("finance/fraud-detector",), 7, "fraud detection"),
    TaskRule("tax", ("finance/tax-advisor",), 7, "tax analysis"),
    TaskRule("investment", ("finance/portfolio-optimizer",), 6, "investment analysis"),
    # Support tasks
    TaskRule("customer support", ("support/customer-support",), 8, "customer support"),
    TaskRule("kundesupport", ("support/customer-support",), 8, "Danish customer support"),
    TaskRule("support ticket", ("support/ticket-router",), 8, "support ticket routing"),
    TaskRule("supportticket", ("support/ticket-router",), 8, "Danish support ticket"),
    TaskRule("helpdesk", ("support/customer-support",), 7, "helpdesk"),
    TaskRule("faq", ("support/knowledge-base-builder",), 6, "FAQ"),
    # Legal tasks
    TaskRule("contract", ("legal/contract-reviewer",), 8, "contract review"),
    TaskRule("kontrakt", ("legal/contract-reviewer",), 8, "Danish contract review"),
    TaskRule("legal", ("legal/legal-researcher",), 7, "legal research"),
    TaskRule("compliance", ("legal/compliance-checker",), 7, "compliance"),
    TaskRule("overholdelse", ("legal/compliance-checker",), 7, "Danish compliance"),
    TaskRule("nda", ("legal/document-drafter",), 7, "NDA drafting"),
    TaskRule("terms of service", ("legal/document-drafter",), 7, "terms drafting"),
    TaskRule("regulation", ("legal/compliance-checker",), 6, "regulation"),
    # Personal tasks
    TaskRule("email", ("personal/email-assistant",), 6, "email"),
    TaskRule("meeting", ("personal/meeting-scheduler",), 6, "meeting scheduling"),
    TaskRule("møde", ("personal/meeting-scheduler",), 6, "Danish meeting scheduling"),
    TaskRule("calendar", ("personal/meeting-scheduler",), 6, "calendar scheduling"),
    TaskRule("kalenderen", ("personal/meeting-scheduler",), 6, "Danish calendar scheduling"),
    TaskRule("notes", ("personal/note-taker",), 5, "notes"),
    TaskRule("meeting notes", ("personal/note-taker",), 9, "meeting notes"),
    TaskRule("todo", ("personal/task-manager",), 5, "task management"),
    TaskRule("schedule", ("personal/meeting-scheduler",), 5, "scheduling"),
    # Security tasks
    TaskRule("vulnerability", ("security/vulnerability-scanner",), 8, "vulnerability scanning"),
    TaskRule("sårbarhedsscanning", ("security/vulnerability-scanner",), 8, "Danish scanning"),
    TaskRule("log analysis", ("security/log-analyzer",), 8, "log analysis"),
    TaskRule("loganalyse", ("security/log-analyzer",), 8, "Danish log analysis"),
    TaskRule("access review", ("security/access-reviewer",), 8, "access review"),
    TaskRule("forensic", ("security/incident-analyst",), 7, "forensic analysis"),
    TaskRule("penetration", ("security/vulnerability-scanner",), 7, "penetration testing"),
)

SUPPRESSION_RULES: tuple[SuppressionRule, ...] = (
    SuppressionRule(
        "do not schedule",
        ("personal/meeting-scheduler",),
        "explicitly not scheduling",
    ),
    SuppressionRule("not schedule", ("personal/meeting-scheduler",), "explicitly not scheduling"),
    SuppressionRule("do not write", ("content/writer",), "explicitly not writing"),
    SuppressionRule("not write", ("content/writer",), "explicitly not writing"),
    SuppressionRule("do not scrape", ("research/web-scraper",), "explicitly not scraping"),
    SuppressionRule("not scrape", ("research/web-scraper",), "explicitly not scraping"),
)

TARGET_RULES: tuple[TargetRule, ...] = (
    TargetRule("a2a", "a2a-agent-card", 10, "A2A protocol"),
    TargetRule("agent card", "a2a-agent-card", 10, "A2A Agent Card"),
    TargetRule(".well-known", "a2a-agent-card", 8, "well-known discovery"),
    TargetRule("claude code", "claude-code", 10, "Claude Code subagent"),
    TargetRule("subagent", "claude-code", 6, "subagent format"),
    TargetRule("agentskill", "agentskill", 10, "AgentSkills format"),
    TargetRule("skill.md", "agentskill", 10, "SKILL.md format"),
    TargetRule("agent skill", "agentskill", 8, "AgentSkills format"),
    TargetRule("codex config", "codex-config", 10, "Codex project config"),
    TargetRule("openclaw", "codex-config", 10, "OpenClaw project config"),
    TargetRule("codex role", "codex-config", 8, "Codex role config"),
    TargetRule("codex cli", "codex-config", 7, "Codex CLI config"),
    TargetRule("agents.md", "codex", 10, "AGENTS.md instructions"),
    TargetRule("google adk", "gemini", 10, "Google ADK config"),
    TargetRule("gemini", "gemini", 9, "Gemini config"),
    TargetRule("vertex", "gemini", 8, "Vertex AI config"),
    TargetRule("chatgpt", "chatgpt", 10, "ChatGPT instructions"),
    TargetRule("custom gpt", "chatgpt", 10, "Custom GPT instructions"),
    TargetRule("raw prompt", "raw", 10, "raw system prompt"),
    TargetRule("system prompt", "raw", 7, "system prompt export"),
    TargetRule("rå prompt", "raw", 10, "Danish raw prompt"),
    TargetRule("rå system prompt", "raw", 10, "Danish raw system prompt"),
)

# Pattern recommendations based on task characteristics
PATTERN_RULES: list[tuple[list[str], str, str]] = [
    # (keywords, pattern, reason)
    (["review", "audit", "check"], "supervisor-worker", "Central reviewer coordinates specialists"),
    (["gennemgå", "tjek"], "supervisor-worker", "Danish review request"),
    (["pipeline", "workflow", "process"], "sequential", "Step-by-step processing chain"),
    (["workflow", "proces"], "sequential", "Danish process chain"),
    (["research", "multi-source", "compare"], "parallel", "Independent sources concurrently"),
    (["undersøg", "markedsresearch", "markedet"], "parallel", "Danish research task"),
    (["draft", "write", "generate"], "reflection", "Iterative refinement improves quality"),
    (["skriv", "udkast"], "reflection", "Danish drafting task"),
    (["support", "route", "escalate"], "handoff", "Transfer control based on complexity"),
    (["kundesupport", "videresend"], "handoff", "Danish support routing"),
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
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    suggested_target: str = "codex-config"
    target_reason: str = "Default local Codex/OpenClaw project config"

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

    def to_dict(self) -> dict[str, Any]:
        """Return a machine-readable recommendation payload."""
        return {
            "pattern": self.pattern,
            "pattern_reason": self.pattern_reason,
            "confidence": self.confidence,
            "agents": [
                {
                    "name": agent.full_name,
                    "description": agent.description,
                    "category": agent.category,
                    "tags": agent.tags,
                }
                for agent in self.agents
            ],
            "alternatives": self.alternatives,
            "reasons": self.reasons,
            "warnings": self.warnings,
            "suggested_target": self.suggested_target,
            "target_reason": self.target_reason,
        }


class AgentRouter:
    """Recommend agents and patterns based on task description."""

    def __init__(self, catalog: Catalog | None = None):
        self.catalog = catalog or Catalog()

    def recommend(self, task: str) -> Recommendation:
        """Given a task description, recommend agents and an orchestration pattern."""
        task_lower = task.lower()

        # Find matching agents with weighted phrase rules.
        agent_scores: dict[str, int] = {}
        agent_reasons: dict[str, list[str]] = {}
        first_seen: dict[str, int] = {}
        for index, rule in enumerate(TASK_RULES):
            if not _contains_phrase(task_lower, rule.phrase):
                continue
            for agent_name in rule.agents:
                agent_scores[agent_name] = agent_scores.get(agent_name, 0) + rule.weight
                agent_reasons.setdefault(agent_name, []).append(
                    f"{agent_name}: matched '{rule.phrase}' ({rule.reason}, +{rule.weight})"
                )
                first_seen.setdefault(agent_name, index)

        matched_agent_names = [
            name
            for name, _ in sorted(
                agent_scores.items(),
                key=lambda item: (-item[1], first_seen[item[0]]),
            )
        ]

        # Fall back to catalog search if no keyword match
        reasons: list[str] = []
        if not matched_agent_names:
            search_results = self.catalog.search(task)
            matched_agent_names = [a.full_name for a in search_results[:3]]
            if matched_agent_names:
                reasons.append("No routing rules matched; used catalog search fallback.")

        suppressed_agents: set[str] = set()
        for rule in SUPPRESSION_RULES:
            if not _contains_phrase(task_lower, rule.phrase):
                continue
            for agent_name in rule.agents:
                suppressed_agents.add(agent_name)
                if agent_name in matched_agent_names:
                    matched_agent_names.remove(agent_name)
                    reasons.append(f"{agent_name}: suppressed because {rule.reason}")

        # Load agent definitions
        agents = []
        for name in matched_agent_names:
            try:
                agents.append(self.catalog.load(name))
                reasons.extend(agent_reasons.get(name, []))
            except KeyError:
                continue

        # Add companion agents
        if len(agents) == 1:
            companions = self.catalog.get_team_for(agents[0].full_name)
            for c in companions[:2]:
                if c.full_name not in matched_agent_names and c.full_name not in suppressed_agents:
                    agents.append(c)
                    reasons.append(f"{c.full_name}: companion for {agents[0].full_name}")

        # Recommend pattern
        pattern = "supervisor-worker"  # Default
        pattern_reason = "General-purpose coordination"
        best_score = 0

        for keywords, pat, reason in PATTERN_RULES:
            score = sum(1 for kw in keywords if _contains_phrase(task_lower, kw))
            if score > best_score:
                best_score = score
                pattern = pat
                pattern_reason = reason

        # Calculate confidence
        best_agent_score = max(agent_scores.values(), default=0)
        confidence = min(
            1.0,
            0.25 + (best_agent_score * 0.08) + (len(agents) * 0.08) + (best_score * 0.1),
        )

        # Find alternative patterns
        alternatives = []
        for keywords, pat, _ in PATTERN_RULES:
            if pat != pattern and any(_contains_phrase(task_lower, kw) for kw in keywords):
                alternatives.append(pat)

        warnings = []
        categories = sorted({agent.category for agent in agents})
        if len(categories) > 1:
            warnings.append(f"Multiple categories matched: {', '.join(categories)}")
        if not agents:
            warnings.append("No agents matched the task.")

        suggested_target, target_reason = self.recommend_target(task)

        return Recommendation(
            agents=agents,
            pattern=pattern,
            pattern_reason=pattern_reason,
            confidence=confidence,
            alternatives=alternatives[:3],
            reasons=reasons,
            warnings=warnings,
            suggested_target=suggested_target,
            target_reason=target_reason,
        )

    def recommend_target(self, task: str) -> tuple[str, str]:
        """Recommend the export target that best matches task wording."""
        task_lower = task.lower()
        target_scores: dict[str, int] = {}
        target_reasons: dict[str, list[str]] = {}
        first_seen: dict[str, int] = {}

        for index, rule in enumerate(TARGET_RULES):
            if not _contains_phrase(task_lower, rule.phrase):
                continue
            target_scores[rule.target] = target_scores.get(rule.target, 0) + rule.weight
            target_reasons.setdefault(rule.target, []).append(rule.reason)
            first_seen.setdefault(rule.target, index)

        if not target_scores:
            return "codex-config", "Default local Codex/OpenClaw project config"

        target = min(
            target_scores,
            key=lambda item: (-target_scores[item], first_seen[item]),
        )
        return target, ", ".join(target_reasons[target])


def _contains_phrase(text: str, phrase: str) -> bool:
    """Match a phrase on word boundaries while allowing flexible whitespace."""
    escaped_words = [re.escape(word) for word in phrase.lower().split()]
    pattern = r"\s+".join(escaped_words)
    return re.search(rf"(?<![\w-]){pattern}(?![\w-])", text) is not None
