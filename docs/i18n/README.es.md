<p align="center">
  <a href="../../README.md">English</a> •
  <a href="README.zh-CN.md">简体中文</a> •
  <a href="README.ja.md">日本語</a> •
  <a href="README.ko.md">한국어</a> •
  <a href="README.es.md">Español</a> •
  <a href="README.de.md">Deutsch</a> •
  <a href="README.da.md">Dansk</a>
</p>

<p align="center">
  <img src="../../docs/assets/banner.svg" alt="multi-agent banner" width="700">
</p>

<h1 align="center">multi-agent</h1>

<p align="center">
  <strong>El catalogo definitivo de patrones de agentes IA. Una definicion, cualquier framework.</strong>
</p>

<p align="center">
  <a href="https://github.com/Hovborg/multi-agent/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <a href="https://pypi.org/project/multi-agent/"><img src="https://img.shields.io/pypi/v/multi-agent.svg" alt="PyPI"></a>
  <a href="https://github.com/Hovborg/multi-agent/stargazers"><img src="https://img.shields.io/github/stars/Hovborg/multi-agent?style=social" alt="GitHub Stars"></a>
  <a href="https://github.com/Hovborg/multi-agent/actions"><img src="https://img.shields.io/github/actions/workflow/status/Hovborg/multi-agent/ci.yml" alt="CI"></a>
  <a href="https://discord.gg/multiagent"><img src="https://img.shields.io/discord/placeholder?label=Discord&logo=discord" alt="Discord"></a>
</p>

<p align="center">
  <a href="#inicio-rapido">Inicio Rapido</a> &bull;
  <a href="#catalogo-de-agentes">Catalogo de Agentes</a> &bull;
  <a href="#mejoras-inteligentes">Mejoras Inteligentes</a> &bull;
  <a href="#exportar-a-cualquier-plataforma">Exportar</a> &bull;
  <a href="../../web/">Playground</a> &bull;
  <a href="../../CONTRIBUTING.md">Contribuir</a>
</p>

---

**48 definiciones de agentes. 11 categorias. 8 patrones de orquestacion. 6 adaptadores de frameworks. 8 destinos de exportacion. Sin dependencia de proveedor.**

`multi-agent` es un catalogo de patrones de agentes IA listos para produccion, independiente del framework. Define tus agentes una vez en YAML y ejecutalos en CrewAI, LangGraph, OpenAI Agents SDK, Claude SDK, Google ADK o smolagents.

Deja de reinventar agentes. Empieza a componerlos.

## Por que multi-agent?

| | multi-agent | CrewAI | LangGraph | OpenAI SDK | Claude SDK |
|---|:---:|:---:|:---:|:---:|:---:|
| Definiciones independientes del framework | **Si** | No | No | No | No |
| Exportar a cualquier plataforma IA | **Si** | No | No | No | No |
| Catalogo reutilizable de agentes | **Si** | Especifico del framework | Especifico del framework | Especifico del framework | Especifico del framework |
| Biblioteca de patrones (8 patrones) | **Si** | 2 | 3 | 2 | 2 |
| Estimacion de costos integrada | **Si** | No | No | No | No |
| Motor de recomendacion de agentes | **Si** | No | No | No | No |
| Compatible con cualquier LLM | **Si** | Si | Si | Solo OpenAI | Solo Claude |
| MCP nativo | **Si** | Parcial | Adaptador | Si | Si |

## Inicio Rapido

```bash
pip install multi-agent
```

### 1. Explorar el catalogo

```bash
multiagent search "code review"
```

```
Found 3 agents matching "code review":

  code/code-reviewer     Review PRs for bugs, style, and security
  code/test-writer       Generate tests for changed code
  code/refactorer        Suggest and apply refactoring improvements

Recommended pattern: supervisor-worker (1 reviewer + N specialists)
Estimated cost: ~$0.03/review (Claude Haiku) to ~$0.25/review (GPT-4o)
```

### 2. Usar una definicion de agente

```python
from multiagent import Catalog, patterns

# Cargar agentes del catalogo
catalog = Catalog()
reviewer = catalog.load("code/code-reviewer")
test_writer = catalog.load("code/test-writer")

# Componer con un patron
team = patterns.supervisor_worker(
    supervisor=reviewer,
    workers=[test_writer],
    model="claude-sonnet-4-6"  # o cualquier modelo
)

result = team.run("Review this PR and write missing tests", context={
    "diff": open("changes.diff").read()
})
```

### 3. O usar con tu framework favorito

```python
# Adaptador CrewAI
from multiagent.adapters import crewai
crew = crewai.from_catalog(["code/code-reviewer", "code/test-writer"])
result = crew.kickoff()

# Adaptador LangGraph
from multiagent.adapters import langgraph
graph = langgraph.from_catalog(["research/deep-researcher", "research/fact-checker"])
result = graph.invoke({"query": "Latest AI agent frameworks"})

# Adaptador OpenAI Agents SDK
from multiagent.adapters import openai_sdk
agent = openai_sdk.from_catalog("code/code-reviewer")
result = agent.run("Review this code")
```

## Catalogo de Agentes

| Categoria | Agentes | Descripcion |
|-----------|---------|-------------|
| **[code/](../../catalog/code/)** | `code-reviewer` `code-generator` `test-writer` `refactorer` `debugger` `security-auditor` `documentation-writer` `pr-summarizer` | Ciclo de vida del desarrollo de software |
| **[research/](../../catalog/research/)** | `deep-researcher` `web-scraper` `fact-checker` `paper-analyst` `competitive-intel` | Investigacion y analisis |
| **[data/](../../catalog/data/)** | `data-analyst` `sql-generator` `report-writer` | Ingenieria y analisis de datos |
| **[devops/](../../catalog/devops/)** | `ci-cd-agent` `infra-provisioner` `monitoring-agent` `incident-responder` | Infraestructura y operaciones |
| **[content/](../../catalog/content/)** | `writer` `editor` `translator` `seo-optimizer` | Pipeline de creacion de contenido |
| **[finance/](../../catalog/finance/)** | `trading-analyst` `portfolio-optimizer` `financial-reporter` `fraud-detector` `tax-advisor` | Analisis financiero y cumplimiento |
| **[support/](../../catalog/support/)** | `customer-support` `ticket-router` `knowledge-base-builder` `escalation-agent` | Pipeline de servicio al cliente |
| **[legal/](../../catalog/legal/)** | `contract-reviewer` `legal-researcher` `compliance-checker` `document-drafter` | Legal y cumplimiento normativo |
| **[personal/](../../catalog/personal/)** | `email-assistant` `meeting-scheduler` `note-taker` `task-manager` | Productividad personal |
| **[security/](../../catalog/security/)** | `vulnerability-scanner` `log-analyzer` `access-reviewer` `incident-analyst` | Operaciones de seguridad |
| **[orchestration/](../../catalog/orchestration/)** | `task-router` `cost-optimizer` `quality-gate` | Meta-agentes de coordinacion |

## Mejoras Inteligentes

Mejora cualquier agente con tecnicas de ingenieria de prompts respaldadas por investigacion:

```bash
multiagent enhance code/code-reviewer -p all
```

| Mejora | Efecto | Fuente |
|--------|--------|--------|
| `reasoning` | +20% completado de tareas | OpenAI SWE-bench |
| `error_recovery` | Jerarquia de reintentos de 5 niveles | Ingenieria Anthropic |
| `verification` | Autoverificacion antes de responder | Claude Code interno |
| `confidence` | -40-60% alucinaciones | Investigacion academica |
| `tool_discipline` | Mas rapido, menos errores | Guia OpenAI GPT-5.4 |
| `failure_modes` | Evita 6 antipatrones | Estudio de 120+ prompts filtrados |
| `context_management` | Mejora tareas de larga duracion | LangChain context engineering |
| `information_priority` | Hechos sobre suposiciones | Manus AI / Anthropic |

## Exportar a Cualquier Plataforma

```bash
multiagent export code/code-reviewer claude-code -o .claude/agents
multiagent export code/code-reviewer agentskill -o .agents/skills/code-reviewer
multiagent export code/code-reviewer a2a-agent-card -o ./agent-cards
multiagent export code/code-reviewer codex
mkdir -p .codex
multiagent export code/code-reviewer codex-config > .codex/config.toml
multiagent export code/code-reviewer gemini -o ./adk-agents
multiagent export code/code-reviewer chatgpt
multiagent export code/code-reviewer raw
```

| Destino | Formato | Compatible con |
|---------|---------|----------------|
| `claude-code` | Archivos subagent `.md` | Claude Code `.claude/agents/` |
| `agentskill` | Markdown estilo `SKILL.md` | Herramientas compatibles con AgentSkills |
| `a2a-agent-card` | Agent Card JSON | Descubrimiento A2A via `.well-known/agent-card.json` |
| `codex` | Secciones AGENTS.md | OpenAI Codex, OpenClaw |
| `codex-config` | Fragmento `.codex/config.toml` | Roles multi-agent de OpenAI Codex |
| `gemini` | Configuracion ADK YAML | Google Gemini, Vertex AI |
| `chatgpt` | Instrucciones del sistema | ChatGPT, Custom GPTs |
| `raw` | Prompt del sistema plano | **Cualquier LLM** — Ollama, LM Studio, llama.cpp, vLLM, etc. |

## Playground Interactivo

Explora agentes, prueba mejoras, compara costos y construye equipos visualmente en el navegador:

**[Abrir Playground](../../web/index.html)** (sin backend necesario — HTML estatico puro)

## Contribuir

Nos encantan las contribuciones! Consulta [CONTRIBUTING.md](../../CONTRIBUTING.md) para mas detalles.

- **Agregar un agente** — Enviar una nueva definicion YAML al catalogo
- **Agregar un patron** — Documentar un nuevo patron de orquestacion con ejemplos
- **Agregar un adaptador** — Crear un adaptador de framework
- **Mejorar la documentacion** — Mejores ejemplos, tutoriales, traducciones

---

<p align="center">
  <sub>Si esto te ayuda a construir mejores agentes, una estrella significaria mucho.</sub>
</p>
