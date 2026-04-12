"""Agent evaluation and benchmarking framework.

Evaluate agent quality across multiple dimensions:
- Prompt completeness: Does the system prompt cover all necessary aspects?
- Tool coverage: Are the right tools defined?
- Cost efficiency: Is the agent cost-effective for its task?
- Enhancement readiness: How well does the agent respond to enhancements?
- Collaboration score: How well does it integrate with other agents?

Usage:
    from multiagent import Catalog
    from multiagent.eval import evaluate_agent, evaluate_catalog, benchmark_report

    catalog = Catalog()
    agent = catalog.load("code/code-reviewer")
    score = evaluate_agent(agent)
    print(score)

    report = benchmark_report(catalog)
    print(report)
"""

from __future__ import annotations

from dataclasses import dataclass, field

from multiagent.catalog import AgentDefinition, Catalog


@dataclass
class EvalScore:
    """Evaluation score for a single agent."""

    agent_name: str
    prompt_quality: float = 0.0  # 0-100
    tool_coverage: float = 0.0
    cost_efficiency: float = 0.0
    enhancement_readiness: float = 0.0
    collaboration: float = 0.0
    details: dict[str, list[str]] = field(default_factory=dict)

    @property
    def overall(self) -> float:
        """Weighted overall score (0-100)."""
        weights = {
            "prompt_quality": 0.35,
            "tool_coverage": 0.15,
            "cost_efficiency": 0.15,
            "enhancement_readiness": 0.15,
            "collaboration": 0.20,
        }
        return sum(
            getattr(self, dim) * w for dim, w in weights.items()
        )

    @property
    def grade(self) -> str:
        """Letter grade."""
        s = self.overall
        if s >= 90:
            return "A"
        if s >= 80:
            return "B"
        if s >= 70:
            return "C"
        if s >= 60:
            return "D"
        return "F"

    def __str__(self) -> str:
        lines = [
            f"{self.agent_name}: {self.overall:.0f}/100 ({self.grade})",
            f"  Prompt Quality:        {self.prompt_quality:.0f}",
            f"  Tool Coverage:         {self.tool_coverage:.0f}",
            f"  Cost Efficiency:       {self.cost_efficiency:.0f}",
            f"  Enhancement Readiness: {self.enhancement_readiness:.0f}",
            f"  Collaboration:         {self.collaboration:.0f}",
        ]
        for category, issues in self.details.items():
            if issues:
                lines.append(f"  [{category}]:")
                for issue in issues:
                    lines.append(f"    - {issue}")
        return "\n".join(lines)


def _eval_prompt_quality(agent: AgentDefinition) -> tuple[float, list[str]]:
    """Evaluate the quality of the system prompt."""
    prompt = agent.system_prompt
    score = 100.0
    issues = []

    # Length check (800-2000 tokens ≈ 200-500 words)
    word_count = len(prompt.split())
    if word_count < 50:
        score -= 30
        issues.append(f"Prompt too short ({word_count} words, recommend 100-500)")
    elif word_count < 100:
        score -= 15
        issues.append(f"Prompt could be more detailed ({word_count} words)")

    # Structure checks
    if not any(c in prompt for c in ["1.", "1)", "-", "*"]):
        score -= 10
        issues.append("No structured list or numbered steps")

    # Has actionable instructions (not just description)
    action_words = ["analyze", "review", "generate", "create", "identify", "check",
                     "evaluate", "produce", "write", "search", "find", "extract"]
    action_count = sum(1 for w in action_words if w.lower() in prompt.lower())
    if action_count < 2:
        score -= 15
        issues.append("Few actionable instructions (add verbs like analyze, check, generate)")

    # Has specificity (not vague)
    if "best practices" in prompt.lower() and word_count < 100:
        score -= 5
        issues.append("Uses 'best practices' without specifying them")

    # Has output format guidance
    format_words = ["format", "structure", "output", "return", "respond", "report"]
    if not any(w in prompt.lower() for w in format_words):
        score -= 10
        issues.append("No output format guidance")

    # Has constraints/boundaries
    constraint_words = ["don't", "do not", "never", "avoid", "only", "must", "always"]
    constraint_count = sum(1 for w in constraint_words if w.lower() in prompt.lower())
    if constraint_count == 0:
        score -= 10
        issues.append("No explicit constraints or boundaries")

    return max(0, score), issues


def _eval_tool_coverage(agent: AgentDefinition) -> tuple[float, list[str]]:
    """Evaluate tool definitions."""
    tools = agent.tools
    score = 100.0
    issues = []

    if not tools:
        return 40.0, ["No tools defined"]

    if len(tools) < 2:
        score -= 20
        issues.append("Only 1 tool — most agents need 2-4")

    # Check for MCP tools
    has_mcp = any(t.get("type") == "mcp" for t in tools)
    if not has_mcp:
        score -= 10
        issues.append("No MCP tools (recommended for standard integrations)")

    # Check for descriptions
    for t in tools:
        if t.get("type") == "function" and not t.get("description"):
            score -= 10
            issues.append(f"Tool '{t.get('name', '?')}' missing description")

    return max(0, score), issues


def _eval_cost_efficiency(agent: AgentDefinition) -> tuple[float, list[str]]:
    """Evaluate cost profile completeness."""
    cp = agent.cost_profile
    score = 100.0
    issues = []

    if cp.input_tokens_per_run == 2000 and cp.output_tokens_per_run == 2000:
        score -= 15
        issues.append("Using default token estimates (2000/2000) — calibrate to actual usage")

    if not cp.recommended_models:
        score -= 25
        issues.append("No recommended models defined")
    elif len(cp.recommended_models) < 2:
        score -= 10
        issues.append("Only 1 recommended model — add quality/balanced/budget tiers")

    if not cp.estimated_cost:
        score -= 20
        issues.append("No cost estimates")

    # Check for budget option
    if cp.recommended_models:
        has_budget = "budget" in cp.recommended_models
        if not has_budget:
            score -= 5
            issues.append("No budget model option")

    return max(0, score), issues


def _eval_enhancement_readiness(agent: AgentDefinition) -> tuple[float, list[str]]:
    """Evaluate how well the agent can be enhanced."""
    prompt = agent.system_prompt
    score = 100.0
    issues = []

    # Already has XML-tagged sections? (good, means structured)
    if "<" in prompt and ">" in prompt:
        pass  # Already structured
    else:
        score -= 10
        issues.append("No XML-tagged sections (enhancements add them, but native is better)")

    # Has clear role definition?
    role_phrases = ["you are", "your role", "as a", "your task"]
    if not any(p in prompt.lower() for p in role_phrases):
        score -= 15
        issues.append("No clear role definition at prompt start")

    # Category set?
    if not agent.category:
        score -= 20
        issues.append("No category — enhancement profiles can't auto-select")

    # Tags?
    if len(agent.tags) < 2:
        score -= 10
        issues.append("Few tags — add more for better search and routing")

    return max(0, score), issues


def _eval_collaboration(agent: AgentDefinition) -> tuple[float, list[str]]:
    """Evaluate how well the agent integrates with others."""
    score = 100.0
    issues = []

    if not agent.works_with:
        score -= 40
        issues.append("No works_with references — agent is isolated")
    elif len(agent.works_with) < 2:
        score -= 15
        issues.append("Only 1 works_with reference — consider more team combinations")

    if not agent.recommended_patterns:
        score -= 30
        issues.append("No recommended patterns — add at least 1-2")
    elif len(agent.recommended_patterns) < 2:
        score -= 10
        issues.append("Only 1 recommended pattern")

    # Check if works_with agents exist in description
    if agent.works_with and not any(
        "team" in (p.get("description", "") or "").lower()
        for p in agent.recommended_patterns
    ):
        pass  # Fine, not all patterns mention "team"

    return max(0, score), issues


def evaluate_agent(agent: AgentDefinition) -> EvalScore:
    """Evaluate a single agent across all dimensions.

    Returns an EvalScore with 0-100 scores per dimension and an overall grade.
    """
    pq, pq_issues = _eval_prompt_quality(agent)
    tc, tc_issues = _eval_tool_coverage(agent)
    ce, ce_issues = _eval_cost_efficiency(agent)
    er, er_issues = _eval_enhancement_readiness(agent)
    co, co_issues = _eval_collaboration(agent)

    return EvalScore(
        agent_name=agent.full_name,
        prompt_quality=pq,
        tool_coverage=tc,
        cost_efficiency=ce,
        enhancement_readiness=er,
        collaboration=co,
        details={
            "prompt": pq_issues,
            "tools": tc_issues,
            "cost": ce_issues,
            "enhancement": er_issues,
            "collaboration": co_issues,
        },
    )


def evaluate_catalog(catalog: Catalog | None = None) -> list[EvalScore]:
    """Evaluate all agents in the catalog."""
    cat = catalog or Catalog()
    return [evaluate_agent(a) for a in cat.list_all()]


def benchmark_report(catalog: Catalog | None = None) -> str:
    """Generate a full benchmark report for the catalog.

    Returns a formatted string with scores, grades, and improvement suggestions.
    """
    scores = evaluate_catalog(catalog)

    if not scores:
        return "No agents to evaluate."

    # Sort by overall score
    scores.sort(key=lambda s: s.overall, reverse=True)

    lines = [
        "Agent Catalog Benchmark Report",
        "=" * 60,
        f"Total agents evaluated: {len(scores)}",
        f"Average score: {sum(s.overall for s in scores) / len(scores):.0f}/100",
        "",
        f"{'Agent':<35} {'Score':>6} {'Grade':>6}",
        "-" * 50,
    ]

    for s in scores:
        lines.append(f"{s.agent_name:<35} {s.overall:>5.0f} {s.grade:>6}")

    # Grade distribution
    grades = {}
    for s in scores:
        grades[s.grade] = grades.get(s.grade, 0) + 1
    lines.append("")
    lines.append("Grade Distribution:")
    for g in ["A", "B", "C", "D", "F"]:
        count = grades.get(g, 0)
        bar = "#" * count
        lines.append(f"  {g}: {bar} ({count})")

    # Category averages
    cat_scores: dict[str, list[float]] = {}
    for s in scores:
        cat = s.agent_name.split("/")[0]
        cat_scores.setdefault(cat, []).append(s.overall)
    lines.append("")
    lines.append("Category Averages:")
    for cat, vals in sorted(cat_scores.items(), key=lambda x: -sum(x[1]) / len(x[1])):
        avg = sum(vals) / len(vals)
        lines.append(f"  {cat:<20} {avg:.0f}/100")

    # Top issues
    all_issues: dict[str, int] = {}
    for s in scores:
        for issues in s.details.values():
            for issue in issues:
                all_issues[issue] = all_issues.get(issue, 0) + 1
    if all_issues:
        lines.append("")
        lines.append("Most Common Issues:")
        for issue, count in sorted(all_issues.items(), key=lambda x: -x[1])[:10]:
            lines.append(f"  [{count}x] {issue}")

    return "\n".join(lines)
