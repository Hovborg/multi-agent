"""Content Factory: Sequential pattern for content creation pipeline.

This example demonstrates:
- Sequential pipeline: Writer → Editor → SEO Optimizer
- Each agent builds on the previous agent's output
- Cost-optimized model selection per step

Usage:
    pip install multi-agent[crewai]
    python content_factory.py
"""

from multiagent import Catalog, CostEstimator, patterns

# Load content agents
catalog = Catalog()
writer = catalog.load("content/writer")
editor = catalog.load("content/editor")
seo = catalog.load("content/seo-optimizer")

# Show the pipeline
pipeline_agents = [writer, editor, seo]
print("Content Factory Pipeline:")
for i, agent in enumerate(pipeline_agents, 1):
    print(f"  Step {i}: {agent.full_name} — {agent.description}")

# Cost-optimized approach: use different models per step
print("\nCost-optimized model routing:")
model_assignments = {
    "content/writer": "claude-sonnet-4-6",       # Quality matters most
    "content/editor": "claude-haiku-4-5",         # Fast and cheap
    "content/seo-optimizer": "gpt-4o-mini",       # Keyword analysis
}
total_cost = 0.0
for agent in pipeline_agents:
    model = model_assignments[agent.full_name]
    estimate = CostEstimator.estimate_agent(agent, models=[model])
    cost = estimate.estimates[0].cost_usd
    total_cost += cost
    print(f"  {agent.name:<20} → {model:<25} ${cost:.4f}")
print(f"  {'TOTAL':<20}   {'':25} ${total_cost:.4f}")

# vs. using the same model for everything
print("\nSingle model comparison:")
for model in ["claude-haiku-4-5", "claude-sonnet-4-6", "gpt-4o"]:
    estimate = CostEstimator.estimate_team(pipeline_agents, model=model)
    e = estimate.estimates[0]
    cost = f"${e.cost_usd:.4f}" if e.cost_usd > 0 else "free"
    print(f"  {model:<25} {cost}")

# Compose the pipeline
pipeline = patterns.sequential(
    steps=pipeline_agents,
    model="claude-sonnet-4-6",
)
print(f"\n{pipeline.describe()}")

print("\nPipeline ready! Use CrewAI adapter for execution.")
