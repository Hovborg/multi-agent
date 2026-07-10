# Multi-Agent Modernization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a wheel-safe, strictly validated, policy-aware multi-agent catalog and router with trustworthy CLI, eval, documentation, and artifact verification.

**Architecture:** Package agent YAML beside the Python modules and load it from one package-relative source. Add a dependency-free validation boundary, then derive an additive orchestration policy from deterministic routing results. Verify source behavior and the installed artifact separately.

**Tech Stack:** Python 3.10+, PyYAML, Click, pytest, Hatchling, Ruff, GitHub Actions.

## Global Constraints

- Preserve all existing valid public imports and CLI commands.
- Do not execute agents, contact model providers, or add runtime side effects.
- Do not add a runtime dependency or lockfile.
- Invalid CLI requests must exit non-zero with actionable diagnostics.
- Generated web data and bundled catalog data must have one authoritative source.
- Preserve pre-existing user changes and never stop live services.

---

### Task 1: Package the authoritative catalog

**Files:**
- Move: `catalog/**/*.yaml` to `src/multiagent/catalog_data/**/*.yaml`
- Modify: `src/multiagent/catalog.py`
- Modify: `pyproject.toml`
- Create: `tests/test_distribution.py`

**Interfaces:**
- Produces: `CATALOG_DIR: Path` resolving inside the installed `multiagent` package.
- Produces: wheels containing every bundled agent YAML and `routing_corpus.yaml`.

- [ ] **Step 1: Write failing artifact tests**

Add tests that assert `CATALOG_DIR.is_dir()`, `len(Catalog()) == 48`, and that a freshly built wheel contains the same YAML count as `Catalog().list_all()`.

- [ ] **Step 2: Verify RED**

Run: `uv run --isolated --extra dev --with build pytest tests/test_distribution.py -q`

Expected: failure because the current wheel contains zero catalog YAML files.

- [ ] **Step 3: Move data and configure Hatchling**

Use `git mv catalog src/multiagent/catalog_data`, change the default to:

```python
CATALOG_DIR = Path(__file__).resolve().parent / "catalog_data"
```

Include the package data in both wheel and sdist build targets.

- [ ] **Step 4: Verify GREEN**

Run the focused tests, build wheel/sdist, install the wheel into a temporary venv, and assert `multiagent list` and `Catalog()` both expose 48 agents.

### Task 2: Strict catalog validation and trustworthy CLI failures

**Files:**
- Create: `src/multiagent/validation.py`
- Modify: `src/multiagent/catalog.py`
- Modify: `src/multiagent/cli.py`
- Modify: `tests/test_catalog.py`
- Modify: `tests/test_cli.py`

**Interfaces:**
- Produces: `CatalogError`, `CatalogValidationError`, and `Catalog.validate() -> list[str]`.
- Produces: `multiagent validate` with exit 0 only for a valid catalog.

- [ ] **Step 1: Write failing tests**

Cover malformed roots, wrong field shapes, invalid safety/context enums, duplicate full names, ambiguous short names, broken companion references, unsafe slugs, and non-zero CLI exits.

- [ ] **Step 2: Verify RED**

Run the focused catalog and CLI tests and confirm failures are caused by missing validation behavior.

- [ ] **Step 3: Implement validation boundary**

Validate untrusted YAML before constructing `AgentDefinition`; collect cross-file reference problems after loading. Reject ambiguity instead of returning the first filesystem-dependent match. Convert expected CLI failures to `click.ClickException`.

- [ ] **Step 4: Verify GREEN**

Run focused tests plus `multiagent validate`; require a clean catalog and non-zero subprocess status for missing agents.

### Task 3: Add bounded orchestration policy

**Files:**
- Modify: `src/multiagent/router.py`
- Modify: `src/multiagent/routing_corpus.yaml`
- Modify: `src/multiagent/routing_eval.py`
- Modify: `tests/test_router.py`
- Modify: `tests/test_routing_eval.py`

**Interfaces:**
- Produces: `Recommendation.policy: dict[str, Any]`.
- Route JSON adds `policy` with `control_mode`, `parallelizable`, `max_delegates`, `delegation_contract`, `trust_boundary`, `approval_required`, and `stop_conditions`.

- [ ] **Step 1: Write failing policy tests**

Assert research fan-out is bounded and parallelizable, handoff tasks select handoff control, side-effect routes require approval, and no-match routes prohibit delegation.

- [ ] **Step 2: Verify RED**

Run router/eval tests and confirm policy fields do not exist yet.

- [ ] **Step 3: Implement deterministic policy derivation**

Derive policy only from matched pattern, selected agents, risk, and context. Cap delegation by complexity; require the contract fields `objective`, `output_format`, `allowed_tools`, `source_requirements`, and `stop_conditions`.

- [ ] **Step 4: Extend corpus and evaluator**

Add policy expectations without weakening existing score gates, then require 100% for the bundled corpus.

- [ ] **Step 5: Verify GREEN**

Run focused tests and the full routing eval command with all score thresholds.

### Task 4: Documentation, generated data, and CI artifact gate

**Files:**
- Modify: `README.md`
- Modify: `docs/i18n/README.da.md`
- Modify: `AI_CONTEXT.md`
- Create: `CHANGELOG.md`
- Create: `cookbook/09-safe-delegation-policy.md`
- Modify: `.github/workflows/ci.yml`
- Regenerate: `web/catalog-data.js`

**Interfaces:**
- Documents `multiagent validate` and additive route `policy` JSON.
- CI builds and smoke-tests the installed wheel.

- [ ] **Step 1: Add documentation assertions where practical**

Extend tests to require generated web parity and documented CLI help output.

- [ ] **Step 2: Update user and maintainer docs**

Document validation, policy semantics, compatibility impact, artifact test, and the no-runtime boundary. Record release changes in `CHANGELOG.md`.

- [ ] **Step 3: Update CI**

Build wheel/sdist once, inspect wheel data, install the wheel into an isolated venv, run catalog/route smoke commands, and retain Python 3.10-3.13 source tests.

- [ ] **Step 4: Regenerate web data**

Run `multiagent generate-web-data --output web/catalog-data.js` from the authoritative packaged catalog and verify no drift.

### Task 5: Completion audit and GitHub publication

**Files:**
- Review all intended changes; create no extra runtime files.

**Interfaces:**
- Produces: clean feature commits, pushed branch, and draft PR.

- [ ] **Step 1: Fresh full verification**

Run Ruff, all tests, routing gates, build, artifact inspection, isolated wheel E2E, generated-data parity, CLI help, secret scan, TODO/debug scan, and `git diff --check`.

- [ ] **Step 2: Review scope and documentation/config sync**

Inspect `git status`, staged diff, dependency metadata, docs, generated artifacts, and every pre-existing change. Stage only intended project work.

- [ ] **Step 3: Commit and push**

Create terse commits, push `agent/modernize-multi-agent`, and open a draft PR against `main` with root causes and exact verification evidence.

- [ ] **Step 4: Verify remote state**

Read the PR and GitHub Actions checks. Do not report completion until required checks pass or explicitly report any still-running/failed check as not verified.
