"""Pattern Example: Supervisor/Worker

Demonstrates the most common multi-agent pattern where a central supervisor
decomposes tasks and delegates to specialist workers.

Architecture:
    ┌─────────────┐
    │  Supervisor  │ (code-reviewer)
    └──────┬──────┘
     ┌─────┼──────┐
     ▼     ▼      ▼
   [W1]  [W2]   [W3]
   test  security refactor

Usage:
    pip install multi-agent
    python supervisor_worker.py
"""

from multiagent import Catalog, CostEstimator, patterns

catalog = Catalog()

# Load the supervisor and workers
supervisor = catalog.load("code/code-reviewer")
workers = [
    catalog.load("code/test-writer"),
    catalog.load("code/security-auditor"),
    catalog.load("code/refactorer"),
]

print("Supervisor/Worker Pattern")
print("=" * 50)
print(f"\nSupervisor: {supervisor.full_name}")
print(f"  {supervisor.description}")
for w in workers:
    print(f"\nWorker: {w.full_name}")
    print(f"  {w.description}")

# Compose the team
team = patterns.supervisor_worker(
    supervisor=supervisor,
    workers=workers,
    model="claude-haiku-4-5",
)

print(f"\n{'=' * 50}")
print(team.describe())

# Cost estimate
all_agents = [supervisor, *workers]
print(f"\n{'=' * 50}")
print("Cost estimates per run:")
for model in ["claude-haiku-4-5", "claude-sonnet-4-6", "gpt-4o-mini", "gpt-4o"]:
    est = CostEstimator.estimate_team(all_agents, model=model)
    e = est.estimates[0]
    cost = f"${e.cost_usd:.4f}" if e.cost_usd > 0 else "free"
    print(f"  {model:<25} {cost:>10}  ({e.total_tokens:,} tokens)")

# How to execute with different frameworks
print(f"\n{'=' * 50}")
print("To execute this team, use a framework adapter:\n")
print("  # CrewAI")
print("  from multiagent.adapters import crewai")
print("  crew = crewai.from_catalog([")
print('      "code/code-reviewer", "code/test-writer",')
print('      "code/security-auditor", "code/refactorer",')
print("  ])")
print("  result = crew.kickoff()")
print()
print("  # Or export for Claude Code")
print("  multiagent export-all claude-code -o .claude/agents -c code")
