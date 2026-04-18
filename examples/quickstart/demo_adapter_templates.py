"""Create framework template plans without installing optional frameworks."""

from pprint import pprint

from multiagent import Catalog
from multiagent.adapters import crewai, google_adk, openai_sdk, smolagents

catalog = Catalog()
reviewer = catalog.load("code/code-reviewer")
test_writer = catalog.load("code/test-writer")
security_auditor = catalog.load("code/security-auditor")

team = [reviewer, test_writer, security_auditor]
workers = [test_writer, security_auditor]

plans = {
    "openai_handoff": openai_sdk.to_handoff_config(reviewer, workers),
    "openai_agent_as_tool": openai_sdk.to_agent_tool_config(reviewer, workers),
    "google_adk_parallel": google_adk.to_workflow_config(team, workflow="parallel"),
    "crewai_flow": crewai.to_flow_config(
        team,
        flow_name="CodeReviewFlow",
        human_feedback=True,
    ),
    "smolagents_manager": smolagents.to_manager_config(reviewer, workers),
}

for name, plan in plans.items():
    print(f"\n{name}")
    pprint(plan, sort_dicts=False)
