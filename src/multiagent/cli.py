"""CLI for browsing and searching the agent catalog."""

from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

from multiagent.catalog import Catalog
from multiagent.cost import CostEstimator
from multiagent.router import AgentRouter

console = Console()


@click.group()
@click.version_option()
def main() -> None:
    """multi-agent: The definitive catalog of AI agent patterns."""


@main.command()
@click.argument("query")
def search(query: str) -> None:
    """Search the agent catalog."""
    catalog = Catalog()
    results = catalog.search(query)

    if not results:
        console.print(f"[yellow]No agents found matching '{query}'[/yellow]")
        return

    console.print(f"\nFound [bold green]{len(results)}[/bold green] agents matching \"{query}\":\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Agent", style="green")
    table.add_column("Description")
    table.add_column("Tags", style="dim")

    for agent in results:
        table.add_row(
            agent.full_name,
            agent.description,
            ", ".join(agent.tags[:3]),
        )

    console.print(table)

    # Show recommendation
    router = AgentRouter(catalog)
    rec = router.recommend(query)
    console.print(f"\n[bold]Recommended pattern:[/bold] {rec.pattern}")
    console.print(f"  {rec.pattern_reason}")


@main.command()
@click.argument("name")
def info(name: str) -> None:
    """Show detailed info about an agent."""
    catalog = Catalog()
    try:
        agent = catalog.load(name)
    except KeyError as e:
        console.print(f"[red]{e}[/red]")
        return

    console.print(f"\n[bold green]{agent.full_name}[/bold green] v{agent.version}")
    console.print(f"[dim]{agent.description}[/dim]\n")

    console.print("[bold]Tags:[/bold]", ", ".join(agent.tags))
    console.print(f"[bold]Temperature:[/bold] {agent.parameters.get('temperature', 'N/A')}")
    console.print(f"[bold]Max tokens:[/bold] {agent.parameters.get('max_tokens', 'N/A')}")

    # Cost
    estimate = CostEstimator.estimate_agent(agent)
    console.print("\n[bold]Cost estimates:[/bold]")
    for e in sorted(estimate.estimates, key=lambda x: x.cost_usd):
        cost = f"${e.cost_usd:.4f}" if e.cost_usd > 0 else "free (local)"
        console.print(f"  {e.model:<25} {cost}")

    # Companions
    if agent.works_with:
        console.print("\n[bold]Works with:[/bold]")
        for name in agent.works_with:
            console.print(f"  - {name}")

    # Patterns
    if agent.recommended_patterns:
        console.print("\n[bold]Recommended patterns:[/bold]")
        for p in agent.recommended_patterns:
            console.print(f"  - [cyan]{p['name']}[/cyan]: {p.get('description', '')}")


@main.command(name="list")
@click.option("--category", "-c", help="Filter by category")
def list_agents(category: str | None) -> None:
    """List all agents in the catalog."""
    catalog = Catalog()

    if category:
        agents = catalog.by_category(category)
        title = f"Agents in '{category}'"
    else:
        agents = catalog.list_all()
        title = "All agents"

    if not agents:
        console.print("[yellow]No agents found.[/yellow]")
        return

    console.print(f"\n[bold]{title}[/bold] ({len(agents)} agents)\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Agent", style="green")
    table.add_column("Description")
    table.add_column("Cost (Haiku)", justify="right", style="dim")

    for agent in agents:
        haiku_cost = agent.cost_profile.estimated_cost.get("claude-haiku-4-5", 0)
        cost_str = f"${haiku_cost:.3f}" if haiku_cost else "—"
        table.add_row(agent.full_name, agent.description, cost_str)

    console.print(table)


@main.command()
@click.argument("task")
def recommend(task: str) -> None:
    """Get agent and pattern recommendations for a task."""
    catalog = Catalog()
    router = AgentRouter(catalog)
    rec = router.recommend(task)

    console.print(f"\n[bold]Task:[/bold] {task}\n")
    console.print(rec.describe())

    if rec.agents:
        console.print("\n[bold]Cost estimate (team):[/bold]")
        estimate = CostEstimator.estimate_team(rec.agents)
        cheapest = estimate.cheapest()
        console.print(f"  Cheapest: {cheapest.model} — ${cheapest.cost_usd:.4f}/run")


@main.command()
def categories() -> None:
    """List all agent categories."""
    catalog = Catalog()
    cats = catalog.list_categories()
    console.print(f"\n[bold]Categories[/bold] ({len(cats)}):\n")
    for cat in cats:
        count = len(catalog.by_category(cat))
        console.print(f"  [green]{cat}[/green] ({count} agents)")


if __name__ == "__main__":
    main()
