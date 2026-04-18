"""CLI for browsing and searching the agent catalog."""

from __future__ import annotations

import json

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
@click.argument("task")
@click.option("--json", "json_output", is_flag=True, help="Output the route decision as JSON")
@click.option("--explain", is_flag=True, help="Show match reasons and routing warnings")
@click.option(
    "--target",
    type=click.Choice(list(EXPORTERS)),
    help="Include export plan for a target",
)
def route(task: str, json_output: bool, explain: bool, target: str | None) -> None:
    """Dry-run route a task to agents without executing them."""
    catalog = Catalog()
    router = AgentRouter(catalog)
    rec = router.recommend(task)

    if json_output:
        payload = rec.to_dict()
        payload.update(
            {
                "task": task,
                "dry_run": True,
                "execution": "not_started",
            }
        )
        if target:
            payload["target"] = target
            payload["exports"] = _target_export_plan(rec.agents, target)
        click.echo(json.dumps(payload, indent=2))
        return

    _print_route_decision(task, rec, explain=explain, target=target)


@main.command()
@click.option("--task", "-t", help="Route one task and exit instead of starting the loop")
@click.option("--explain", is_flag=True, help="Show match reasons after each route")
def auto(task: str | None, explain: bool) -> None:
    """Interactive dry-run router that continuously recommends agents."""
    catalog = Catalog()
    router = AgentRouter(catalog)

    console.print("\n[bold cyan]Multi-Agent Auto Router[/bold cyan]")
    console.print("[dim]Dry-run only. No agents are executed. Type 'exit' to stop.[/dim]\n")

    if task:
        _print_route_decision(task, router.recommend(task), explain=explain)
        return

    while True:
        try:
            user_task = click.prompt("task", default="", show_default=False)
        except (EOFError, KeyboardInterrupt):
            console.print()
            break

        user_task = user_task.strip()
        if user_task.lower() in {"exit", "quit", "q", ":q"}:
            break
        if not user_task:
            continue

        _print_route_decision(user_task, router.recommend(user_task), explain=explain)
        console.print()


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

    Targets: a2a-agent-card, claude-code, agentskill, codex, codex-config, gemini, chatgpt, raw

    Examples:
        multiagent export code/code-reviewer a2a-agent-card -o ./agent-cards
        multiagent export code/code-reviewer claude-code
        multiagent export code/code-reviewer agentskill -o .agents/skills/code-reviewer
        mkdir -p .codex
        multiagent export code/code-reviewer codex-config > .codex/config.toml
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
        multiagent export-all claude-code -o .claude/agents
        multiagent export-all a2a-agent-card -o ./agent-cards
        multiagent export-all agentskill -o .agents/skills
        multiagent export-all codex -o ./agents -c code
        multiagent export-all codex-config -o ./codex-configs -c code
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
        multiagent enhance code/code-reviewer -p all -t claude-code -o .claude/agents
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


@main.command(name="eval-routing")
@click.option("--json", "json_output", is_flag=True, help="Output the report as JSON")
@click.option("--fail-under", type=float, help="Exit non-zero if pass rate is below this value")
def eval_routing_cmd(json_output: bool, fail_under: float | None) -> None:
    """Evaluate router decisions against the built-in task corpus."""
    from multiagent.routing_eval import evaluate_routing_corpus

    report = evaluate_routing_corpus(Catalog())
    if json_output:
        click.echo(json.dumps(report.to_dict(), indent=2))
    else:
        console.print(
            f"\n[bold]Routing eval:[/bold] {report.passed}/{report.total} "
            f"passed ({report.pass_rate:.0%})"
        )
        console.print(
            "[dim]Scores:[/dim] "
            f"agents {report.scores['agent_match_rate']:.0%}, "
            f"patterns {report.scores['pattern_match_rate']:.0%}, "
            f"targets {report.scores['target_match_rate']:.0%}, "
            f"forbidden {report.scores['forbidden_match_rate']:.0%}"
        )
        if report.failures:
            table = Table(show_header=True, header_style="bold red")
            table.add_column("Case")
            table.add_column("Expected")
            table.add_column("Actual")
            for result in report.failures:
                table.add_row(
                    result.case.id,
                    ", ".join(result.case.expected_agents),
                    ", ".join(result.actual_agents),
                )
            console.print(table)

    if fail_under is not None and report.pass_rate < fail_under:
        raise click.ClickException(
            f"Routing pass rate {report.pass_rate:.0%} is below {fail_under:.0%}"
        )


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
    exp_idx = click.prompt(
        "  Select format",
        type=click.IntRange(1, len(EXPORT_TARGETS)),
        default=5,
    )
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


def _print_route_decision(task: str, rec, explain: bool = False, target: str | None = None) -> None:
    """Render a dry-run route decision for humans."""
    console.print(f"\n[bold]Task:[/bold] {task}")
    console.print("[bold yellow]Dry run:[/bold yellow] no agents executed")
    console.print(f"[bold]Pattern:[/bold] {rec.pattern} — {rec.pattern_reason}")
    console.print(f"[bold]Confidence:[/bold] {rec.confidence:.0%}\n")

    if rec.agents:
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Agent", style="green")
        table.add_column("Category", style="dim")
        table.add_column("Description")
        for agent in rec.agents:
            table.add_row(agent.full_name, agent.category, agent.description)
        console.print(table)

        estimate = CostEstimator.estimate_team(rec.agents)
        cheapest = estimate.cheapest()
        console.print(
            f"\n[bold]Cheapest estimate:[/bold] {cheapest.model} — "
            f"${cheapest.cost_usd:.4f}/run"
        )

        if target:
            console.print(f"\n[bold]Target:[/bold] {target}")
            export_table = Table(show_header=True, header_style="bold cyan")
            export_table.add_column("Agent", style="green")
            export_table.add_column("Format")
            export_table.add_column("Command", style="dim")
            for item in _target_export_plan(rec.agents, target):
                export_table.add_row(item["agent"], item["format"], item["command"])
            console.print(export_table)
            console.print("\n[bold]Export commands:[/bold]")
            for item in _target_export_plan(rec.agents, target):
                console.print(f"  {item['command']}")
    else:
        console.print("[yellow]No matching agents found.[/yellow]")

    if rec.alternatives:
        console.print(f"[bold]Alternative patterns:[/bold] {', '.join(rec.alternatives)}")

    if explain:
        console.print("\n[bold]Why[/bold]")
        for reason in rec.reasons or ["No routing reasons were recorded."]:
            console.print(f"  - {reason}")
        if rec.warnings:
            console.print("\n[bold yellow]Warnings[/bold yellow]")
            for warning in rec.warnings:
                console.print(f"  - {warning}")


def _target_export_plan(agents, target: str) -> list[dict[str, str]]:
    """Build dry-run export commands for a routed agent team."""
    return [
        {
            "agent": agent.full_name,
            "target": target,
            "format": _target_format_label(target),
            "output_file": (
                f"exports/{target}/{agent.category}/{agent.name}{_target_extension(target)}"
            ),
            "command": f"multiagent export {agent.full_name} {target}",
        }
        for agent in agents
    ]


def _target_format_label(target: str) -> str:
    labels = {
        "a2a-agent-card": "A2A Agent Card JSON",
        "agentskill": "AgentSkills SKILL.md",
        "claude-code": "Claude Code subagent Markdown",
        "codex": "Codex AGENTS.md section",
        "codex-config": "Codex config.toml snippet",
        "gemini": "Google ADK YAML",
        "chatgpt": "ChatGPT system instructions",
        "raw": "Plain system prompt",
    }
    return labels[target]


def _target_extension(target: str) -> str:
    extensions = {
        "a2a-agent-card": ".agent-card.json",
        "agentskill": ".md",
        "claude-code": ".md",
        "codex": ".md",
        "codex-config": ".toml",
        "gemini": ".yaml",
        "chatgpt": ".txt",
        "raw": ".txt",
    }
    return extensions[target]


if __name__ == "__main__":
    main()
