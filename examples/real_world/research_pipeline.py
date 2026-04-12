"""Research Pipeline: Parallel + Sequential pattern for multi-source research.

This example demonstrates:
- Parallel fan-out: multiple researchers work simultaneously
- Sequential follow-up: fact-checker verifies findings
- Cost comparison across models

Usage:
    pip install multi-agent[langgraph]
    python research_pipeline.py
"""

from multiagent import Catalog, CostEstimator, patterns

# Load research agents
catalog = Catalog()
researcher = catalog.load("research/deep-researcher")
fact_checker = catalog.load("research/fact-checker")

# Show the team
print("Research Pipeline:")
print(f"  Phase 1 (parallel): 3x {researcher.full_name}")
print(f"  Phase 2 (sequential): {fact_checker.full_name}")

# Cost comparison across models
print("\nCost comparison for full pipeline:")
for model in ["claude-haiku-4-5", "claude-sonnet-4-6", "gpt-4o", "gpt-4o-mini", "gemini-2.5-flash"]:
    # 3 parallel researchers + 1 fact checker
    all_agents = [researcher, researcher, researcher, fact_checker]
    estimate = CostEstimator.estimate_team(all_agents, model=model)
    e = estimate.estimates[0]
    cost_str = f"${e.cost_usd:.4f}" if e.cost_usd > 0 else "free"
    print(f"  {model:<25} {cost_str:>10}  ({e.total_tokens} tokens)")

# Compose the pipeline
# Phase 1: Parallel research from multiple angles
research_team = patterns.parallel(
    agents=[researcher, researcher, researcher],
    model="claude-haiku-4-5",
)

# Phase 2: Fact-checking
# In practice, you'd chain these:
# full_pipeline = patterns.sequential(
#     steps=[research_team, fact_checker],
# )

print(f"\nParallel research phase: {research_team.describe()}")

# To execute with LangGraph:
#
# from multiagent.adapters import langgraph
# config = langgraph.from_catalog(
#     ["research/deep-researcher", "research/fact-checker"],
#     flow="sequential",
# )
# # Build StateGraph from config

print("\nPipeline ready! Use LangGraph adapter for execution.")
