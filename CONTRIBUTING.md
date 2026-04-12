# Contributing to multi-agent

Thank you for your interest in contributing! This project thrives on community contributions.

## Ways to Contribute

### Add an Agent to the Catalog

The most impactful contribution is adding new agent definitions.

1. Fork the repo and create a branch: `git checkout -b add-agent/my-agent`
2. Create a YAML file in the appropriate `catalog/` subdirectory
3. Follow the [agent definition format](#agent-definition-format)
4. Add tests if applicable
5. Submit a PR

### Agent Definition Format

```yaml
name: agent-name          # Lowercase, hyphenated
version: "1.0"
description: One-line description of what the agent does
category: code             # code, research, data, devops, content, orchestration
tags: [tag1, tag2, tag3]

system_prompt: |
  Detailed system prompt with best practices.
  Should be 10-30 lines of practical instructions.

tools:
  - type: mcp
    server: filesystem
  - type: function
    name: tool_name
    description: What the tool does

parameters:
  temperature: 0.1         # 0.0-1.0, lower = more deterministic
  max_tokens: 4096

cost_profile:
  input_tokens_per_run: 3000
  output_tokens_per_run: 2000
  recommended_models:
    quality: claude-sonnet-4-6
    balanced: claude-haiku-4-5
    budget: gemma4-27b
  estimated_cost:
    claude-haiku-4-5: 0.003
    claude-sonnet-4-6: 0.025

works_with:
  - category/other-agent

recommended_patterns:
  - name: pattern-name
    description: Why this pattern works for this agent
```

### Add an Orchestration Pattern

1. Create documentation in `docs/patterns/your-pattern.md`
2. Add the pattern class to `src/multiagent/patterns.py`
3. Include at least one runnable example
4. Submit a PR

### Add a Framework Adapter

1. Create the adapter in `src/multiagent/adapters/your_framework.py`
2. Follow the existing adapter pattern (lazy imports, clear error messages)
3. Add the framework to `pyproject.toml` optional dependencies
4. Submit a PR

## Development Setup

```bash
git clone https://github.com/Hovborg/multi-agent.git
cd multi-agent
pip install -e ".[dev]"
pytest
```

## Code Style

- Python 3.10+
- Formatted with `ruff`
- Type hints on all public functions
- Docstrings on all public classes and functions

```bash
ruff check .
ruff format .
pytest
```

## Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Keep PRs focused — one feature/fix per PR
4. Write a clear PR description

## Code of Conduct

Be kind. Be constructive. We're all here to build something useful.
