"""Hello Agents: Your first multi-agent experience in 10 lines.

Usage:
    pip install multi-agent
    python hello_agents.py
"""

from multiagent import AgentRouter, Catalog, CostEstimator

# 1. Browse the catalog
catalog = Catalog()
print(f"Loaded {len(catalog)} agents across {len(catalog.list_categories())} categories\n")

# 2. Search for agents
results = catalog.search("code review")
for agent in results:
    print(f"  {agent.full_name}: {agent.description}")

# 3. Get a recommendation
router = AgentRouter(catalog)
rec = router.recommend("I need to review a PR and write missing tests")
print(f"\n{rec.describe()}")

# 4. Estimate costs
if rec.agents:
    estimate = CostEstimator.estimate_team(rec.agents)
    print(f"\n{estimate}")
