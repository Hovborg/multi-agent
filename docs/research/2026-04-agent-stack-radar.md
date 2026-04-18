# Agent Stack Radar - April 2026

Verificeret: 2026-04-19
Target root: `/mnt/c/codex_projekts/02-dev/06-multi-agent`

## Kort konklusion

Det giver mening at opdatere projektet, men ikke som endnu en fuld multi-agent runtime. Markedet har allerede runtime-frameworks. Projektets bedste vinkel er at være et framework-agnostisk katalog, router og eksportlag, der kan generere korrekte konfigurationer til Codex, Claude Code, OpenAI Agents SDK, Google ADK/A2A, LangGraph, CrewAI, smolagents og AgentSkills.

Det vigtigste nye i april 2026 er ikke "flere agenter". Det er bedre styring af:

- hvornår en specialist overtager samtalen vs bruges som tool
- tool permissions og approval gates
- tracing/evals
- protokol-eksport: MCP, A2A og AG-UI
- kontekst-isolation gennem subagents/routere i stedet for store monolitiske prompts

## Lokal status

Verificeret med lokale kommandoer 2026-04-19:

- Kataloget loader 48 agenter i 11 kategorier.
- Projektet har adaptere til OpenAI SDK, Claude SDK, LangGraph, CrewAI, Google ADK og smolagents.
- Adapterne er primært tynde config-konvertere, ikke fulde runtime-buildere.
- CLI har nu `route` og `auto` som dry-run routere.

Docs cleanup udført 2026-04-19:

- README og i18n-filer bruger nu verificeret katalogantal.
- Det ubekræftede Anthropic-citat er fjernet.
- Framework star-tal/status er fjernet fra comparison/docs.
- `claude-code` export er gjort til Claude Code subagent-format, og AgentSkills har fået separat `agentskill` target.

## Verificerede eksterne signaler

### OpenAI / Codex

OpenAI dokumenterer nu Codex CLI som MCP-server orkestreret med Agents SDK til multi-agent workflows med handoffs, guardrails og traces. Codex config understøtter også agentroller direkte via `agents.<name>.description`, `agents.<name>.config_file`, `agents.<name>.nickname_candidates`, `agents.max_threads`, `agents.max_depth` og `features.multi_agent`.

Kilder:

- https://developers.openai.com/codex/guides/agents-sdk#creating-multi-agent-workflows
- https://developers.openai.com/codex/config-reference#configtoml
- https://developers.openai.com/api/docs/guides/agents/orchestration
- https://developers.openai.com/api/docs/guides/agents/guardrails-approvals
- https://developers.openai.com/api/docs/guides/agents/integrations-observability

### Claude Code

Claude Code subagents er projekt- eller bruger-scopede Markdown-filer under `.claude/agents/` eller `~/.claude/agents/`. De vælges via `description`, kører i separat context window, kan begrænses med tools, og kan bruges til at route simple opgaver til billigere modeller.

Kilde: https://code.claude.com/docs/en/sub-agents

### LangChain / LangGraph

LangChain docs sammenligner subagents, handoffs, skills og router. For multi-domain opgaver anbefales parallel execution via subagents/router typisk som mere effektivt end lange handoff-kæder eller skills der akkumulerer meget kontekst.

Kilde: https://docs.langchain.com/oss/python/langchain/multi-agent/index

### CrewAI

CrewAI Flows understøtter router-baserede branches, human feedback, streaming execution og flow-plotting. Det passer bedre til deterministic workflow export end at lave endnu en custom runtime.

Kilde: https://docs.crewai.com/en/concepts/flows

### Google ADK og A2A

ADK dokumenterer coordinator/dispatcher, sequential pipeline, parallel fan-out/gather og hierarchical task decomposition. ADK har også A2A-support, hvor en root agent kan arbejde med lokale og remote A2A-agenter.

A2A har officiel 2026-dokumentation som Linux Foundation-projekt. A2A er agent-til-agent laget, mens MCP er agent-til-tool/context laget.

Kilder:

- https://adk.dev/agents/multi-agents/
- https://adk.dev/a2a/
- https://a2a-protocol.org/latest/
- https://a2a-protocol.org/latest/topics/what-is-a2a/
- https://a2a-protocol.org/latest/specification/

### Microsoft Agent Framework

Microsoft Agent Framework er public preview og beskrives som efterfølger til Semantic Kernel og AutoGen. Frameworket har built-in orchestrations: sequential, concurrent, handoff, group chat og magentic, plus human-in-the-loop via approval-required tools.

Kilder:

- https://learn.microsoft.com/en-us/agent-framework/overview/
- https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/

### PydanticAI

PydanticAI lægger vægt på typed multi-agent control flow, usage limits og full-stack observability via Logfire/OpenTelemetry. Det er relevant for eval/trace metadata i kataloget.

Kilde: https://pydantic.dev/docs/ai/guides/multi-agent-applications/

### smolagents

smolagents multi-agent mønsteret bruger en manager agent med `managed_agents`. De managed agents skal have `name` og `description`, så manageren kan kalde dem korrekt.

Kilde: https://huggingface.co/docs/smolagents/v1.22.0/examples/multiagents

### MCP, AgentSkills og AG-UI

MCP latest spec er 2025-11-25. Den definerer tools, resources, prompts, sampling, roots og elicitation. I 2026 har MCP også official SDK tiering og conformance-test-fokus.

AgentSkills er blevet et portabelt format for domain/task-instruktioner. OpenHands og MCP docs beskriver progressive disclosure gennem `SKILL.md`.

AG-UI positionerer sig som agent-til-user laget, komplementært til MCP og A2A.

Kilder:

- https://modelcontextprotocol.io/docs/getting-started/intro
- https://modelcontextprotocol.io/specification/2025-11-25
- https://modelcontextprotocol.io/community/sdk-tiers
- https://modelcontextprotocol.io/docs/develop/build-with-agent-skills
- https://docs.openhands.dev/sdk/guides/skill
- https://docs.ag-ui.com/agentic-protocols

## Hvad vi bør bygge

### P0 - Ret sandhed og positionering

Udført 2026-04-19.

- README/i18n bruger verificeret katalogantal.
- Ubekræftede marketing-citater og volatile star/status tabeller er fjernet.
- `claude-code` genererer Claude Code subagent Markdown.
- `agentskill` genererer portabelt AgentSkills Markdown.

### P1 - Nye export targets

Udført 2026-04-19:

- `claude-code`: generer `.claude/agents/{agent}.md` med YAML frontmatter: `name`, `description`, og prompt body.
- `agentskill`: generer standard `SKILL.md` med description/triggers/progressive disclosure.
- `codex-config`: generer `.codex/config.toml` snippet med `[features].multi_agent`, `[agents]` defaults, `[agents.<name>]`, `description`, og `nickname_candidates`.
- `a2a-agent-card`: generer A2A 1.0 Agent Card JSON med `supportedInterfaces`, `capabilities`, `defaultInputModes`, `defaultOutputModes`, og `skills`.

Bevidst udeladt indtil vi genererer rolle-lag som separate filer:

- `agents.<name>.config_file`

### P2 - Udvid YAML-skemaet

Udført 2026-04-19 som kompatibilitetslag: `AgentDefinition` kan nu læse disse metadatafelter uden at kræve at alle eksisterende YAML-filer udfylder dem.

- `orchestration.control_mode`: `manager_tool`, `handoff`, `subagent`, `router`, `sequential`, `parallel`
- `orchestration.execution_mode`: `dry_run`, `interactive`, `autonomous`, `human_gated`
- `safety.side_effect_risk`: `none`, `low`, `medium`, `high`
- `safety.requires_human_review`: boolean
- `observability.trace_tags`: list
- `observability.eval_criteria`: list
- `outputs.expected_artifacts`: list
- `context.loading`: `always`, `trigger`, `progressive`
- `context.max_context_tokens`: number
- `protocols.mcp`: servers/resources/prompts/tools
- `protocols.a2a`: agent card fields
- `protocols.ag_ui`: stream/state/event hints

### P3 - Gør routeren framework-aware

Udført 2026-04-19 for eksisterende export targets:

- `multiagent route "..." --target codex-config`
- `multiagent route "..." --target a2a-agent-card`

Stadig åbent for adapter-targets der ikke er exportere endnu:

- `multiagent route "..." --target claude-subagent`
- `multiagent route "..." --target openai-agents`
- `multiagent route "..." --target adk`

Routeren bør klassificere:

- single specialist vs multi-agent
- handoff vs agents-as-tools
- parallel vs sequential
- side-effect risk
- human approval needed
- context size risk

### P4 - Adapter upgrades

OpenAI:

- helper for `handoffs`
- helper for `agent.as_tool`
- helper metadata for guardrails and tracing
- optional Codex MCP workflow template

Claude:

- true `.claude/agents/` subagent exporter
- tool permission mapping
- model tier hints

LangGraph:

- supervisor/router graph config
- explicit parallel fan-out config
- state key naming for aggregation

CrewAI:

- Flow export with `@start`, `@listen`, `@router`
- optional `@human_feedback` metadata
- `crewai flow plot` hint in generated docs

Google ADK:

- `SequentialAgent`, `ParallelAgent`, `AgentTool` templates
- A2A consume/expose templates

smolagents:

- manager-agent config with `managed_agents`
- enforce `name` and `description` on managed agents

### P5 - Hvad vi ikke bør bygge nu

- En fuld autonomous runtime fra bunden.
- Et komplet erstatnings-framework for LangGraph/CrewAI/ADK/OpenAI Agents SDK.
- Automatisk side-effect execution som default.
- Model-pris/latest-model tabeller uden live verification.

## Prioriteret roadmap

1. Done: Adapter-specific template helpers for OpenAI handoffs/as_tool, ADK sequential/parallel, CrewAI Flow og smolagents manager.
2. Done: Routing eval corpus med 43 task prompts og forventet agent/pattern/target.
3. Done: Routing eval kører som CI-gate med `multiagent eval-routing --fail-under 1.0`.
4. Done: Corpus dækker danske/flersprogede prompts og uklare target-hints.
5. Done: Negative eval cases dækker tasks, der eksplicit fravælger en specialist.
6. Done: Routing metrics er splittet i agent, pattern, target og forbidden-agent delscorer.
7. Næste: Tilføj weighted score thresholds, så CI kan tillade lavere target-score end agent-score.

## Beslutning

Ja, projektet giver mening, hvis det holdes som katalog/router/export-layer. Det hjælper OpenClaw, fordi samme agent-definition kan blive til Codex config, Claude subagent, AgentSkill, A2A card eller framework config.

Nej, det giver ikke mening at konkurrere med LangGraph, CrewAI, OpenAI Agents SDK, ADK eller Microsoft Agent Framework som runtime. De har allerede de tunge execution loops. Vores fordel er at vælge og generere korrekt konfiguration til dem.
