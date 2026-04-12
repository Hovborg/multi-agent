"""Code Review Team: Supervisor/Worker pattern for automated PR review.

This example demonstrates:
- Loading multiple agents from the catalog
- Composing them with the supervisor-worker pattern
- Using the CrewAI adapter for execution
- Cost estimation before running

Usage:
    pip install multi-agent[crewai]
    python code_review_team.py
"""

from multiagent import Catalog, CostEstimator, patterns

# Load agents from catalog
catalog = Catalog()
reviewer = catalog.load("code/code-reviewer")
test_writer = catalog.load("code/test-writer")
security_auditor = catalog.load("code/security-auditor")

# Show what we're working with
print("Code Review Team:")
print(f"  Supervisor: {reviewer.full_name} — {reviewer.description}")
for worker in [test_writer, security_auditor]:
    print(f"  Worker:     {worker.full_name} — {worker.description}")

# Estimate costs before running
estimate = CostEstimator.estimate_team(
    [reviewer, test_writer, security_auditor],
    extra_input_tokens=5000,  # The PR diff
)
print(f"\n{estimate}")

# Compose the team with supervisor-worker pattern
team = patterns.supervisor_worker(
    supervisor=reviewer,
    workers=[test_writer, security_auditor],
    model="claude-haiku-4-5",
)
print(f"\n{team.describe()}")

# To actually run this, you need a framework adapter:
#
# Option A: CrewAI
# from multiagent.adapters import crewai
# crew = crewai.from_catalog(
#     ["code/code-reviewer", "code/test-writer", "code/security-auditor"],
#     task_description="Review this PR diff and identify issues",
# )
# result = crew.kickoff()
#
# Option B: Claude SDK
# from multiagent.adapters import claude_sdk
# configs = claude_sdk.from_catalog(
#     ["code/code-reviewer", "code/test-writer", "code/security-auditor"],
# )
# # Use configs with Anthropic API or Claude Managed Agents
#
# Option C: OpenAI Agents SDK
# from multiagent.adapters import openai_sdk
# agents = openai_sdk.from_catalog(
#     ["code/code-reviewer", "code/test-writer", "code/security-auditor"],
# )
# # Use agents with OpenAI Runner

print("\nTeam is ready! Use a framework adapter to execute.")
print("See the comments in this file for CrewAI, Claude SDK, and OpenAI SDK examples.")
