# Multi-Agent Modernization Design

## Goal

Turn the existing framework-neutral catalog and dry-run router into a reliable,
installable, safety-aware multi-agent design tool. Preserve its framework-neutral
identity; do not turn this release into a model-calling runtime.

## Success criteria

- A wheel installed outside the source checkout contains and loads the complete
  catalog and routing corpus.
- Invalid, duplicate, or ambiguous catalog definitions fail predictably with
  actionable diagnostics instead of being skipped or overwritten silently.
- CLI failures use non-zero exit codes and machine-readable routing remains stable.
- Routing decisions expose bounded delegation, context, risk, execution, and
  evaluation guidance that downstream runtimes can enforce.
- Routing evaluation covers positive selection, forbidden selection, risk,
  context, target, and orchestration-policy behavior.
- Generated web data and documentation match the shipped catalog and CLI.
- CI builds the distribution, installs the wheel into a clean environment, and
  runs an end-to-end smoke test.

## Evidence and current defects

The baseline test suite passes in a source checkout, but a fresh wheel contains
zero catalog YAML files. Installing that wheel in an isolated environment makes
`multiagent list` report no agents. The default path in `Catalog` points outside
the installed package. Existing tests hide this because they pass the repository
`catalog/` path explicitly.

The CLI also catches missing-agent errors, prints them, and returns success. This
makes shell scripts and CI unable to distinguish invalid requests from valid
output. Catalog loading catches only a subset of parse failures and silently
overwrites duplicate fully-qualified names.

## Research-grounded direction

The design follows five current cross-framework principles:

1. Use deterministic routing for clear categories and reserve supervisor-style
   orchestration for open, conversation-aware work.
2. Delegate only independent, bounded work with explicit objective, output
   contract, tool boundary, and stopping criteria.
3. Keep specialist contexts isolated and progressively disclose a large agent
   registry instead of injecting every definition into every prompt.
4. Treat side effects, untrusted tool content, and subagent output as policy
   boundaries. Subagent output is not automatically more trusted than tool data.
5. Evaluate outcomes and trajectories, including tool use, risk gates, context,
   latency/cost proxies, and multiple valid orchestration paths.

Primary references:

- OpenAI Agents SDK, Agent orchestration:
  <https://openai.github.io/openai-agents-python/multi_agent/>
- OpenAI Agents SDK, Guardrails and human approval:
  <https://openai.github.io/openai-agents-python/guardrails/>
- LangChain, Subagents and context engineering:
  <https://docs.langchain.com/oss/python/langchain/multi-agent/subagents>
- LangChain, Router architecture:
  <https://docs.langchain.com/oss/python/langchain/multi-agent/router>
- Anthropic, multi-agent research engineering:
  <https://www.anthropic.com/engineering/multi-agent-research-system>
- Anthropic, agent evaluation:
  <https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents>
- Anthropic, agent containment:
  <https://www.anthropic.com/engineering/how-we-contain-claude>

## Architecture

### Packaged catalog

Move the runtime catalog data under `src/multiagent/catalog_data/`, include it in
sdists and wheels, and make that package-relative location the only default.
Repository tooling and the web generator must consume the same authoritative
data. A build-and-install smoke test verifies the artifact rather than the source
tree.

### Typed validation and diagnostics

Introduce a focused validation layer using standard Python plus PyYAML; avoid a
new runtime dependency. Validation checks the required scalar fields, list/map
shapes, supported safety/context values, unique full names, companion references,
and pattern references. `CatalogError` and `CatalogValidationError` preserve file
and field context. Strict loading is the default; an explicit diagnostic command
reports all catalog issues in one pass.

### Routing policy

Keep the deterministic weighted router for reproducibility, but enrich its output
with an orchestration policy:

- `control_mode`: router, manager, or handoff;
- `parallelizable`: whether selected work can fan out safely;
- `max_delegates`: a complexity-scaled upper bound, never unbounded;
- `delegation_contract`: required task, output, tool, and stop fields;
- `trust_boundary`: untrusted inputs and outputs requiring validation;
- `approval_required`: derived from selected agent and tool risk;
- `stop_conditions`: no-match, sufficient-evidence, budget, and review gates.

No agent is executed. The project produces a portable, inspectable plan that
framework adapters can translate.

### Evaluation

Extend the routing corpus and evaluator with policy assertions. Add artifact
tests for wheel contents, isolated installation, CLI exit behavior, generated
web-data parity, catalog referential integrity, and JSON schema stability. Keep
all gates deterministic and offline.

### Documentation and release hygiene

Update README, Danish README where applicable, AI_CONTEXT, cookbook guidance,
and a new CHANGELOG. No environment variables or secrets are introduced. The
project has no lockfile today; because no runtime dependency is added, a new
lockfile is not required. Generated `web/catalog-data.js` is refreshed from the
same packaged source.

## Error handling and safety

- Invalid catalog content produces a non-zero CLI exit and names the file/field.
- Ambiguous short names are rejected with matching candidates.
- Output filenames derive from validated slugs and cannot traverse directories.
- External side-effect capability always yields an approval gate in route plans.
- Untrusted context and delegated outputs remain explicitly untrusted until a
  downstream runtime validates them.
- The package never contacts a model provider or performs side effects.

## Compatibility

Existing public imports and valid CLI commands remain supported. JSON route
output gains additive policy fields. Invalid calls that previously exited zero
will intentionally exit non-zero. Catalog authors may need to fix definitions
that violate the documented schema; all bundled definitions must validate.

## Verification bar

Completion requires, from a clean isolated environment:

1. formatting/lint checks;
2. full unit and integration tests;
3. routing evaluation gates;
4. sdist and wheel builds;
5. wheel-content assertions;
6. wheel installation and CLI/API end-to-end smoke tests outside the repo;
7. generated web-data parity check;
8. repository secret and loose-end scans;
9. final diff review and GitHub CI status after push.
