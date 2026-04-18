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
  <strong>Det ultimative katalog over AI-agent-moenstre. Definer en gang, koer paa ethvert framework.</strong>
</p>

<p align="center">
  <a href="https://github.com/Hovborg/multi-agent/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <a href="https://pypi.org/project/multi-agent/"><img src="https://img.shields.io/pypi/v/multi-agent.svg" alt="PyPI"></a>
  <a href="https://github.com/Hovborg/multi-agent/stargazers"><img src="https://img.shields.io/github/stars/Hovborg/multi-agent?style=social" alt="GitHub Stars"></a>
  <a href="https://github.com/Hovborg/multi-agent/actions"><img src="https://img.shields.io/github/actions/workflow/status/Hovborg/multi-agent/ci.yml" alt="CI"></a>
  <a href="https://discord.gg/multiagent"><img src="https://img.shields.io/discord/placeholder?label=Discord&logo=discord" alt="Discord"></a>
</p>

<p align="center">
  <a href="#hurtig-start">Hurtig Start</a> &bull;
  <a href="#agent-katalog">Agent-katalog</a> &bull;
  <a href="#smarte-forbedringer">Smarte Forbedringer</a> &bull;
  <a href="#eksporter-til-enhver-platform">Eksport</a> &bull;
  <a href="../../web/">Playground</a> &bull;
  <a href="../../CONTRIBUTING.md">Bidrag</a>
</p>

---

**48 agent-definitioner. 11 kategorier. 8 orkestreringmoenstre. 6 framework-adaptere. 8 eksportmaal. Ingen vendor lock-in.**

`multi-agent` er et framework-uafhaengigt katalog af produktionsklare AI-agent-moenstre. Definer dine agenter en gang i YAML, og koer dem paa CrewAI, LangGraph, OpenAI Agents SDK, Claude SDK, Google ADK eller smolagents.

Stop med at genopfinde agenter. Begynd at sammensaette dem.

## Hvorfor multi-agent?

| | multi-agent | CrewAI | LangGraph | OpenAI SDK | Claude SDK |
|---|:---:|:---:|:---:|:---:|:---:|
| Framework-uafhaengige definitioner | **Ja** | Nej | Nej | Nej | Nej |
| Eksporter til enhver AI-platform | **Ja** | Nej | Nej | Nej | Nej |
| Genbrugeligt agent-katalog | **Ja** | Framework-specifikt | Framework-specifikt | Framework-specifikt | Framework-specifikt |
| Moensterbibliotek (8 moenstre) | **Ja** | 2 | 3 | 2 | 2 |
| Indbygget prisestimat | **Ja** | Nej | Nej | Nej | Nej |
| Agent-anbefalingsmotor | **Ja** | Nej | Nej | Nej | Nej |
| Virker med enhver LLM | **Ja** | Ja | Ja | Kun OpenAI | Kun Claude |
| MCP nativt | **Ja** | Delvist | Adapter | Ja | Ja |

## Hurtig Start

```bash
pip install multi-agent
```

### 1. Gennemse kataloget

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

### 2. Brug en agent-definition

```python
from multiagent import Catalog, patterns

# Indlaes agenter fra kataloget
catalog = Catalog()
reviewer = catalog.load("code/code-reviewer")
test_writer = catalog.load("code/test-writer")

# Kombiner med et moenster
team = patterns.supervisor_worker(
    supervisor=reviewer,
    workers=[test_writer],
    model="claude-sonnet-4-6"  # eller enhver model
)

result = team.run("Review this PR and write missing tests", context={
    "diff": open("changes.diff").read()
})
```

### 3. Eller brug med dit foretrukne framework

```python
# CrewAI-adapter
from multiagent.adapters import crewai
crew = crewai.from_catalog(["code/code-reviewer", "code/test-writer"])
result = crew.kickoff()

# LangGraph-adapter
from multiagent.adapters import langgraph
graph = langgraph.from_catalog(["research/deep-researcher", "research/fact-checker"])
result = graph.invoke({"query": "Latest AI agent frameworks"})

# OpenAI Agents SDK-adapter
from multiagent.adapters import openai_sdk
agent = openai_sdk.from_catalog("code/code-reviewer")
result = agent.run("Review this code")
```

## Agent-katalog

| Kategori | Agenter | Beskrivelse |
|----------|---------|-------------|
| **[code/](../../catalog/code/)** | `code-reviewer` `code-generator` `test-writer` `refactorer` `debugger` `security-auditor` `documentation-writer` `pr-summarizer` | Softwareudviklingens livscyklus |
| **[research/](../../catalog/research/)** | `deep-researcher` `web-scraper` `fact-checker` `paper-analyst` `competitive-intel` | Research og analyse |
| **[data/](../../catalog/data/)** | `data-analyst` `sql-generator` `report-writer` | Data engineering og analyse |
| **[devops/](../../catalog/devops/)** | `ci-cd-agent` `infra-provisioner` `monitoring-agent` `incident-responder` | Infrastruktur og drift |
| **[content/](../../catalog/content/)** | `writer` `editor` `translator` `seo-optimizer` | Indholdsproduktions-pipeline |
| **[finance/](../../catalog/finance/)** | `trading-analyst` `portfolio-optimizer` `financial-reporter` `fraud-detector` `tax-advisor` | Finansanalyse og compliance |
| **[support/](../../catalog/support/)** | `customer-support` `ticket-router` `knowledge-base-builder` `escalation-agent` | Kundeservice-pipeline |
| **[legal/](../../catalog/legal/)** | `contract-reviewer` `legal-researcher` `compliance-checker` `document-drafter` | Jura og compliance |
| **[personal/](../../catalog/personal/)** | `email-assistant` `meeting-scheduler` `note-taker` `task-manager` | Personlig produktivitet |
| **[security/](../../catalog/security/)** | `vulnerability-scanner` `log-analyzer` `access-reviewer` `incident-analyst` | Sikkerhedsoperationer |
| **[orchestration/](../../catalog/orchestration/)** | `task-router` `cost-optimizer` `quality-gate` | Meta-agenter til koordinering |

## Smarte Forbedringer

Goer enhver agent bedre med forskningsbaserede prompt-engineering-teknikker:

```bash
multiagent enhance code/code-reviewer -p all
```

| Forbedring | Effekt | Kilde |
|------------|--------|-------|
| `reasoning` | +20% opgavegennemfoerelse | OpenAI SWE-bench |
| `error_recovery` | 5-niveau genforsoegshierarki | Anthropic engineering |
| `verification` | Selvtjek foer output | Claude Code internt |
| `confidence` | -40-60% hallucinationer | Akademisk forskning |
| `tool_discipline` | Hurtigere, faerre fejl | OpenAI GPT-5.4-guide |
| `failure_modes` | Undgaar 6 anti-moenstre | 120+ laekkede prompts-studie |
| `context_management` | Bedre langvarige opgaver | LangChain context engineering |
| `information_priority` | Fakta frem for gaetterier | Manus AI / Anthropic |

## Eksporter til Enhver Platform

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

| Maal | Format | Kompatibelt med |
|------|--------|-----------------|
| `claude-code` | `.md`-subagent-filer | Claude Code `.claude/agents/` |
| `agentskill` | `SKILL.md`-style Markdown | AgentSkills-kompatible vaerktoejer |
| `a2a-agent-card` | Agent Card JSON | A2A discovery via `.well-known/agent-card.json` |
| `codex` | AGENTS.md-sektioner | OpenAI Codex, OpenClaw |
| `codex-config` | `.codex/config.toml`-snippet | OpenAI Codex multi-agent-roller |
| `gemini` | ADK YAML-konfiguration | Google Gemini, Vertex AI |
| `chatgpt` | Systeminstruktioner | ChatGPT, Custom GPTs |
| `raw` | Ren system-prompt | **Enhver LLM** — Ollama, LM Studio, llama.cpp, vLLM, osv. |

## Interaktiv Playground

Udforsk agenter, test forbedringer, sammenlign priser og byg teams visuelt i browseren:

**[Aabn Playground](../../web/index.html)** (ingen backend nødvendig — rent statisk HTML)

## Bidrag

Vi elsker bidrag! Se [CONTRIBUTING.md](../../CONTRIBUTING.md) for detaljer.

- **Tilfoej en agent** — Indsend en ny YAML-agent-definition til kataloget
- **Tilfoej et moenster** — Dokumenter et nyt orkestreringsmoenster med eksempler
- **Tilfoej en adapter** — Opret en framework-adapter
- **Forbedr dokumentation** — Bedre eksempler, tutorials, oversaettelser

---

<p align="center">
  <sub>Hvis dette hjaelper dig med at bygge bedre agenter, ville en stjerne betyde meget.</sub>
</p>
