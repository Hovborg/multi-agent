# CLAUDE.md - multi-agent

## Project Overview
Open-source catalog of AI agent patterns. Framework-agnostic YAML definitions that work across CrewAI, LangGraph, OpenAI SDK, Claude SDK, Google ADK, and smolagents.

## Structure
- `catalog/` — YAML agent definitions organized by category
- `src/multiagent/` — Python package (catalog loader, patterns, cost estimator, CLI, adapters)
- `docs/` — Pattern documentation, framework guides, protocol guides
- `examples/` — Runnable Python examples
- `tests/` — pytest test suite

## Development
```bash
pip install -e ".[dev]"
pytest
ruff check .
```

## Key Files
- `src/multiagent/catalog.py` — Agent loading and search
- `src/multiagent/patterns.py` — 8 orchestration pattern classes
- `src/multiagent/cost.py` — Cost estimation with model pricing
- `src/multiagent/router.py` — Task → agent recommendation engine
- `src/multiagent/cli.py` — CLI tool (search, info, list, recommend)

## Conventions
- Python 3.10+ with type hints
- YAML for agent definitions, Python for logic
- All agents must have: name, description, system_prompt, category, cost_profile
- MIT license
