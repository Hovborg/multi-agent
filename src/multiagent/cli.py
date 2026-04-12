"""CLI for browsing and searching the agent catalog."""

from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

from multiagent.catalog import Catalog
from multiagent.cost import CostEstimator
from multiagent.enhance import enhance_agent, list_enhancements
from multiagent.export import EXPORTERS, export_agent
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


@main.command()
@click.argument("agent_name")
@click.argument("target", type=click.Choice(list(EXPORTERS)))
@click.option("--output", "-o", type=click.Path(), help="Output directory")
def export(agent_name: str, target: str, output: str | None) -> None:
    """Export an agent to a platform format.

    Targets: claude-code, codex, gemini, chatgpt, raw

    Examples:
        multiagent export code/code-reviewer claude-code
        multiagent export code/code-reviewer chatgpt -o ./output
        multiagent export code/code-reviewer raw
    """
    catalog = Catalog()
    try:
        agent = catalog.load(agent_name)
    except KeyError as e:
        console.print(f"[red]{e}[/red]")
        return

    from pathlib import Path

    output_dir = Path(output) if output else None
    content = export_agent(agent, target, output_dir)

    if output_dir:
        console.print(f"[green]Exported {agent.full_name} → {output_dir}/[/green]")
    else:
        console.print(content)


@main.command(name="export-all")
@click.argument("target", type=click.Choice(list(EXPORTERS)))
@click.option("--output", "-o", type=click.Path(), required=True, help="Output directory")
@click.option("--category", "-c", help="Filter by category")
def export_all(target: str, output: str, category: str | None) -> None:
    """Export all agents (or a category) to a platform format.

    Examples:
        multiagent export-all claude-code -o .agents/skills
        multiagent export-all codex -o ./agents -c code
        multiagent export-all gemini -o ./adk-agents
    """
    from pathlib import Path

    catalog = Catalog()
    agents = catalog.by_category(category) if category else catalog.list_all()

    output_dir = Path(output)
    for agent in agents:
        agent_dir = output_dir / agent.category
        export_agent(agent, target, agent_dir)

    console.print(
        f"[green]Exported {len(agents)} agents → {output_dir}/ (format: {target})[/green]"
    )


@main.command()
@click.argument("agent_name")
@click.option(
    "--profile",
    "-p",
    type=click.Choice(["category", "all", "minimal", "none"]),
    default="category",
    help="Enhancement profile",
)
@click.option("--target", "-t", type=click.Choice(list(EXPORTERS)), help="Also export")
@click.option("--output", "-o", type=click.Path(), help="Output directory (with --target)")
def enhance(agent_name: str, profile: str, target: str | None, output: str | None) -> None:
    """Enhance an agent with smart prompt techniques.

    Profiles:
      category  — Enhancements tuned for the agent's category (default)
      all       — All 8 enhancement blocks
      minimal   — Just reasoning + verification
      none      — Show base prompt without enhancements

    Examples:
        multiagent enhance code/code-reviewer
        multiagent enhance code/code-reviewer -p all
        multiagent enhance code/code-reviewer -p all -t claude-code -o .agents/
    """
    catalog = Catalog()
    try:
        agent = catalog.load(agent_name)
    except KeyError as e:
        console.print(f"[red]{e}[/red]")
        return

    enhanced = enhance_agent(agent, profile=profile)

    if target:
        from pathlib import Path

        output_dir = Path(output) if output else None
        content = export_agent(enhanced, target, output_dir)
        if output_dir:
            console.print(f"[green]Enhanced + exported {agent.full_name} → {output_dir}/[/green]")
        else:
            console.print(content)
    else:
        console.print(f"\n[bold green]{agent.full_name}[/bold green] (enhanced: {profile})\n")
        console.print(enhanced.system_prompt)


@main.command()
def enhancements() -> None:
    """List all available smart prompt enhancements."""
    available = list_enhancements()
    console.print(f"\n[bold]Smart Enhancements[/bold] ({len(available)}):\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Name", style="green")
    table.add_column("Category", style="dim")
    table.add_column("Description")

    for e in available:
        table.add_row(e["name"], e["category"], e["description"])

    console.print(table)


@main.command()
@click.argument("agent_names", nargs=-1, required=True)
@click.option(
    "--pattern",
    "-p",
    default="supervisor-worker",
    help="Orchestration pattern",
)
def visualize(agent_names: tuple[str, ...], pattern: str) -> None:
    """Generate a Mermaid diagram for an agent team.

    Examples:
        multiagent visualize code/code-reviewer code/test-writer
        multiagent visualize code/code-reviewer code/test-writer -p sequential
    """
    from multiagent.visualize import visualize_team

    catalog = Catalog()
    agents = []
    for name in agent_names:
        try:
            agents.append(catalog.load(name))
        except KeyError as e:
            console.print(f"[red]{e}[/red]")
            return

    diagram = visualize_team(agents, pattern)
    console.print(f"\n[bold]Pattern:[/bold] {pattern}")
    console.print(f"[bold]Agents:[/bold] {', '.join(a.full_name for a in agents)}\n")
    console.print("[dim]```mermaid[/dim]")
    console.print(diagram)
    console.print("[dim]```[/dim]")

    estimate = CostEstimator.estimate_team(agents, model="claude-haiku-4-5")
    e = estimate.estimates[0]
    console.print(f"\n[bold]Cost:[/bold] ${e.cost_usd:.4f}/run (claude-haiku-4-5)")


if __name__ == "__main__":
    main()
