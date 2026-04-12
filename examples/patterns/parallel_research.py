"""Pattern Example: Parallel Fan-Out

Demonstrates the parallel pattern where multiple agents work simultaneously
on independent tasks, with results merged at the end.

Architecture:
    ┌──→ [Researcher A] ──┐
    │                     │
    ├──→ [Researcher B] ──┼──→ [Fact Checker]
    │                     │
    └──→ [Researcher C] ──┘

Usage:
    pip install multi-agent
    python parallel_research.py
"""

from multiagent import Catalog, CostEstimator, patterns

catalog = Catalog()

# Load research agents
researcher = catalog.load("research/deep-researcher")
fact_checker = catalog.load("research/fact-checker")

print("Parallel Research Pattern")
print("=" * 50)
print(f"\nPhase 1 — Parallel research (3 independent agents):")
print(f"  Each: {researcher.full_name} — {researcher.description}")
print(f"\nPhase 2 — Verification:")
print(f"  {fact_checker.full_name} — {fact_checker.description}")

# Compose: 3 researchers in parallel, fact-checker merges
research_team = patterns.parallel(
    agents=[researcher, researcher, researcher],
    merger=fact_checker,
    model="claude-haiku-4-5",
)

print(f"\n{research_team.describe()}")

# Show cost savings of parallel vs sequential
all_agents = [researcher, researcher, researcher, fact_checker]
print(f"\n{'=' * 50}")
print("Cost per research run:")
for model in ["claude-haiku-4-5", "gpt-4o-mini", "gemini-2.5-flash", "deepseek-v3"]:
    est = CostEstimator.estimate_team(all_agents, model=model)
    e = est.estimates[0]
    cost = f"${e.cost_usd:.4f}" if e.cost_usd > 0 else "free"
    print(f"  {model:<25} {cost:>10}")

print("\nKey advantage: Parallel execution means 3x faster than sequential,")
print("with the same total cost (tokens are the same, wall-clock time is lower).")
