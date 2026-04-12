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


@main.command(name="eval")
@click.argument("agent_name", required=False)
@click.option("--all-agents", "-a", is_flag=True, help="Evaluate entire catalog")
def eval_cmd(agent_name: str | None, all_agents: bool) -> None:
    """Evaluate agent quality with scores and improvement suggestions.

    Examples:
        multiagent eval code/code-reviewer
        multiagent eval --all-agents
    """
    from multiagent.eval import benchmark_report, evaluate_agent

    catalog = Catalog()

    if all_agents or not agent_name:
        report = benchmark_report(catalog)
        console.print(f"\n{report}")
    else:
        try:
            agent = catalog.load(agent_name)
        except KeyError as e:
            console.print(f"[red]{e}[/red]")
            return
        score = evaluate_agent(agent)
        console.print(f"\n{score}")


@main.command()
@click.option("--task", "-t", help="Task description (skips first prompt)")
def build(task: str | None) -> None:
    """Interactive team builder wizard.

    Guides you through composing a multi-agent team step by step.

    Example:
        multiagent build
        multiagent build -t "review PRs and write tests"
    """
    from multiagent.builder import (
        ENHANCEMENT_PROFILES,
        EXPORT_TARGETS,
        PATTERNS,
        TeamConfig,
        get_popular_models,
    )

    catalog = Catalog()
    router = AgentRouter(catalog)
    config = TeamConfig()

    console.print("\n[bold cyan]Multi-Agent Team Builder[/bold cyan]")
    console.print("[dim]Build your perfect agent team step by step\n[/dim]")

    # Step 1: Task description
    console.print("[bold]Step 1/6:[/bold] What's your task?")
    if task:
        config.task_description = task
        console.print(f"  → {task}\n")
    else:
        config.task_description = click.prompt("  Describe your task", type=str)
        console.print()

    # Get recommendations
    rec = router.recommend(config.task_description)
    if rec.agents:
        console.print(f"[green]Found {len(rec.agents)} recommended agents:[/green]")
        for i, a in enumerate(rec.agents, 1):
            console.print(f"  {i}. {a.full_name} — {a.description}")
        console.print()
        use_rec = click.confirm("  Use these agents?", default=True)
        if use_rec:
            config.agents = list(rec.agents)
        console.print()

    # Step 2: Select/add agents
    if not config.agents:
        console.print("[bold]Step 2/6:[/bold] Select agents")
        console.print("  Available categories:", ", ".join(catalog.list_categories()))
        while True:
            name = click.prompt(
                "  Agent name (or 'done')", type=str, default="done"
            )
            if name == "done":
                break
            try:
                agent = catalog.load(name)
                config.agents.append(agent)
                console.print(f"  [green]+ {agent.full_name}[/green]")
            except KeyError:
                results = catalog.search(name)
                if results:
                    console.print(f"  Did you mean: {', '.join(a.full_name for a in results[:5])}")
                else:
                    console.print(f"  [red]Not found: {name}[/red]")
        console.print()
    else:
        console.print("[bold]Step 2/6:[/bold] Agents selected from recommendations")
        console.print()

    if not config.agents:
        console.print("[red]No agents selected. Exiting.[/red]")
        return

    # Step 3: Pattern
    console.print("[bold]Step 3/6:[/bold] Choose orchestration pattern")
    for i, (name, desc) in enumerate(PATTERNS, 1):
        marker = " [cyan](recommended)[/cyan]" if name == rec.pattern else ""
        console.print(f"  {i}. {name} — {desc}{marker}")
    pattern_idx = click.prompt(
        "  Select pattern",
        type=click.IntRange(1, len(PATTERNS)),
        default=next(
            (i for i, (n, _) in enumerate(PATTERNS, 1) if n == rec.pattern), 1
        ),
    )
    config.pattern = PATTERNS[pattern_idx - 1][0]
    console.print()

    # Step 4: Enhancement
    console.print("[bold]Step 4/6:[/bold] Choose enhancement profile")
    for i, (name, desc) in enumerate(ENHANCEMENT_PROFILES, 1):
        console.print(f"  {i}. {name} — {desc}")
    enh_idx = click.prompt("  Select profile", type=click.IntRange(1, 4), default=3)
    config.enhancement_profile = ENHANCEMENT_PROFILES[enh_idx - 1][0]
    console.print()

    # Step 5: Model
    console.print("[bold]Step 5/6:[/bold] Choose model")
    models = get_popular_models()
    for i, (name, label) in enumerate(models, 1):
        console.print(f"  {i}. {label}")
    model_idx = click.prompt(
        "  Select model",
        type=click.IntRange(1, len(models)),
        default=next((i for i, (n, _) in enumerate(models, 1) if n == "claude-haiku-4-5"), 1),
    )
    config.model = models[model_idx - 1][0]
    console.print()

    # Step 6: Export
    console.print("[bold]Step 6/6:[/bold] Choose export format")
    for i, (name, desc) in enumerate(EXPORT_TARGETS, 1):
        console.print(f"  {i}. {name} — {desc}")
    exp_idx = click.prompt("  Select format", type=click.IntRange(1, 5), default=5)
    config.export_target = EXPORT_TARGETS[exp_idx - 1][0]
    console.print()

    # Summary
    console.print("[bold cyan]" + "=" * 50 + "[/bold cyan]")
    console.print(config.summary())

    # Diagram
    if len(config.agents) >= 2:
        console.print("\n[bold]Team Diagram:[/bold]")
        console.print("[dim]```mermaid[/dim]")
        console.print(config.get_diagram())
        console.print("[dim]```[/dim]")

    # Export
    console.print()
    do_export = click.confirm("Export enhanced agents to files?", default=False)
    if do_export:
        from pathlib import Path

        output = click.prompt("  Output directory", default="./agents-output")
        paths = config.export_all(Path(output))
        console.print(f"\n[green]Exported {len(paths)} agents to {output}/[/green]")
        for p in paths:
            console.print(f"  → {p}")

    console.print("\n[bold green]Team builder complete![/bold green]")


if __name__ == "__main__":
    main()
