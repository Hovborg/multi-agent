"""multi-agent: The definitive catalog of AI agent patterns. One definition, any framework."""

__version__ = "0.1.0"

from multiagent.catalog import AgentDefinition, Catalog
from multiagent.cost import CostEstimator
from multiagent.enhance import enhance_agent
from multiagent.export import export_agent
from multiagent.patterns import patterns
from multiagent.router import AgentRouter

__all__ = [
    "AgentDefinition",
    "AgentRouter",
    "Catalog",
    "CostEstimator",
    "enhance_agent",
    "export_agent",
    "patterns",
]
