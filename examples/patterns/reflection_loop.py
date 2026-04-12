"""Pattern Example: Reflection Loop

Demonstrates the reflection pattern where a producer generates output
and a critic reviews it, iterating until quality is sufficient.

Architecture:
    ┌──────────┐         ┌──────────┐
    │ Producer │ ──────► │  Critic  │
    │ (writer) │ ◄────── │ (editor) │
    └──────────┘  refine └──────────┘
         │
         ▼ (quality threshold met)
      [Final Output]

Research shows reflection improves code from 80% to 91% on HumanEval.

Usage:
    pip install multi-agent
    python reflection_loop.py
"""

from multiagent import Catalog, CostEstimator, patterns

catalog = Catalog()

# Load producer and critic
producer = catalog.load("content/writer")
critic = catalog.load("content/editor")

print("Reflection Loop Pattern")
print("=" * 50)
print(f"\nProducer: {producer.full_name}")
print(f"  {producer.description}")
print(f"\nCritic: {critic.full_name}")
print(f"  {critic.description}")

# Compose the reflection loop
loop = patterns.reflection(
    producer=producer,
    critic=critic,
    max_iterations=3,
    quality_threshold=0.9,
    model="claude-sonnet-4-6",
)

print(f"\n{loop.describe()}")

# Cost analysis: reflection costs 2-3x a single pass
print(f"\n{'=' * 50}")
print("Cost per iteration (producer + critic):")
team = [producer, critic]
for model in ["claude-haiku-4-5", "claude-sonnet-4-6", "gpt-4o"]:
    est = CostEstimator.estimate_team(team, model=model)
    e = est.estimates[0]
    single = e.cost_usd
    print(f"  {model:<25} 1 iter: ${single:.4f}  |  3 iters: ${single*3:.4f}")

print("\nTip: Use a cheap model for the critic (it just reviews,")
print("     doesn't generate). Save the expensive model for the producer.")
print("\nCost-optimized setup:")
print("  Producer: claude-sonnet-4-6  ($0.050/iter)")
print("  Critic:   claude-haiku-4-5   ($0.005/iter)")
print("  Total for 3 iterations:       $0.165")
