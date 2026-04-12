"""Cost estimation for agent runs across different models."""

from __future__ import annotations

from dataclasses import dataclass, field

from multiagent.catalog import AgentDefinition

# Pricing per 1M tokens (USD) as of April 2026
MODEL_PRICING: dict[str, dict[str, float]] = {
    # Anthropic
    "claude-opus-4-6": {"input": 15.00, "output": 75.00},
    "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
    "claude-haiku-4-5": {"input": 0.80, "output": 4.00},
    # OpenAI
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "o3": {"input": 10.00, "output": 40.00},
    "o4-mini": {"input": 1.10, "output": 4.40},
    # Google
    "gemini-2.5-pro": {"input": 1.25, "output": 10.00},
    "gemini-2.5-flash": {"input": 0.15, "output": 0.60},
    # Open / Local (API pricing where available)
    "llama-4-maverick": {"input": 0.20, "output": 0.60},
    "deepseek-v3": {"input": 0.14, "output": 0.28},
    "gemma4-27b": {"input": 0.00, "output": 0.00},  # Local
    "nemotron-cascade-2": {"input": 0.00, "output": 0.00},  # Local
}


@dataclass
class ModelEstimate:
    """Cost estimate for a specific model."""

    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    tier: str  # "quality", "balanced", "budget"


@dataclass
class CostEstimate:
    """Cost estimate for running an agent or team."""

    agents: list[str]
    estimates: list[ModelEstimate] = field(default_factory=list)

    def cheapest(self) -> ModelEstimate:
        """Get the cheapest non-zero estimate."""
        paid = [e for e in self.estimates if e.cost_usd > 0]
        return min(paid, key=lambda e: e.cost_usd) if paid else self.estimates[0]

    def by_model(self, model: str) -> ModelEstimate | None:
        """Get estimate for a specific model."""
        for e in self.estimates:
            if e.model == model:
                return e
        return None

    def __str__(self) -> str:
        lines = [f"Cost estimate for: {', '.join(self.agents)}"]
        lines.append(f"{'Model':<25} {'Tokens':>8} {'Cost':>10}")
        lines.append("-" * 45)
        for e in sorted(self.estimates, key=lambda x: x.cost_usd):
            cost_str = f"${e.cost_usd:.4f}" if e.cost_usd > 0 else "free (local)"
            lines.append(f"{e.model:<25} {e.total_tokens:>8} {cost_str:>10}")
        return "\n".join(lines)


class CostEstimator:
    """Estimate costs for running agents across different models."""

    @staticmethod
    def _calc_cost(model: str, input_tokens: int, output_tokens: int) -> float:
        pricing = MODEL_PRICING.get(model)
        if not pricing:
            return 0.0
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost

    @classmethod
    def estimate_agent(
        cls,
        agent: AgentDefinition,
        extra_input_tokens: int = 0,
        models: list[str] | None = None,
    ) -> CostEstimate:
        """Estimate cost for running a single agent."""
        input_tokens = agent.cost_profile.input_tokens_per_run + extra_input_tokens
        output_tokens = agent.cost_profile.output_tokens_per_run

        if models is None:
            models = list(agent.cost_profile.recommended_models.values())
            # Add some common models for comparison
            for m in ["claude-haiku-4-5", "gpt-4o-mini", "gemini-2.5-flash"]:
                if m not in models:
                    models.append(m)

        estimates = []
        rec_models = agent.cost_profile.recommended_models
        for model in models:
            tier = "custom"
            for t, m in rec_models.items():
                if m == model:
                    tier = t
                    break
            estimates.append(
                ModelEstimate(
                    model=model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=input_tokens + output_tokens,
                    cost_usd=cls._calc_cost(model, input_tokens, output_tokens),
                    tier=tier,
                )
            )

        return CostEstimate(agents=[agent.full_name], estimates=estimates)

    @classmethod
    def estimate_team(
        cls,
        agents: list[AgentDefinition],
        extra_input_tokens: int = 0,
        model: str | None = None,
    ) -> CostEstimate:
        """Estimate total cost for running a team of agents."""
        total_input = sum(a.cost_profile.input_tokens_per_run for a in agents) + extra_input_tokens
        total_output = sum(a.cost_profile.output_tokens_per_run for a in agents)

        models = [model] if model else list(MODEL_PRICING.keys())
        estimates = []
        for m in models:
            estimates.append(
                ModelEstimate(
                    model=m,
                    input_tokens=total_input,
                    output_tokens=total_output,
                    total_tokens=total_input + total_output,
                    cost_usd=cls._calc_cost(m, total_input, total_output),
                    tier="custom",
                )
            )

        return CostEstimate(
            agents=[a.full_name for a in agents],
            estimates=estimates,
        )

    # Shorthand
    estimate = estimate_agent
