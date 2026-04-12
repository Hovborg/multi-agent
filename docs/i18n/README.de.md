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
  <strong>Der definitive Katalog fuer KI-Agenten-Muster. Einmal definieren, auf jedem Framework ausfuehren.</strong>
</p>

<p align="center">
  <a href="https://github.com/Hovborg/multi-agent/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <a href="https://pypi.org/project/multi-agent/"><img src="https://img.shields.io/pypi/v/multi-agent.svg" alt="PyPI"></a>
  <a href="https://github.com/Hovborg/multi-agent/stargazers"><img src="https://img.shields.io/github/stars/Hovborg/multi-agent?style=social" alt="GitHub Stars"></a>
  <a href="https://github.com/Hovborg/multi-agent/actions"><img src="https://img.shields.io/github/actions/workflow/status/Hovborg/multi-agent/ci.yml" alt="CI"></a>
  <a href="https://discord.gg/multiagent"><img src="https://img.shields.io/discord/placeholder?label=Discord&logo=discord" alt="Discord"></a>
</p>

<p align="center">
  <a href="#schnellstart">Schnellstart</a> &bull;
  <a href="#agenten-katalog">Agenten-Katalog</a> &bull;
  <a href="#smarte-verbesserungen">Smarte Verbesserungen</a> &bull;
  <a href="#export-auf-jede-plattform">Export</a> &bull;
  <a href="../../web/">Playground</a> &bull;
  <a href="../../CONTRIBUTING.md">Mitwirken</a>
</p>

---

**Ueber 50 praxiserprobte Agenten-Definitionen. 11 Kategorien. 8 Orchestrierungsmuster. 6 Framework-Adapter. 5 Export-Ziele. Kein Vendor Lock-in.**

`multi-agent` ist ein framework-unabhaengiger Katalog produktionsreifer KI-Agenten-Muster. Definiere deine Agenten einmal in YAML und fuehre sie auf CrewAI, LangGraph, OpenAI Agents SDK, Claude SDK, Google ADK oder smolagents aus.

> *"57% der Agenten-Ausfaelle in Unternehmen sind Orchestrierungs-Fehler, keine Modell-Fehler."* — Anthropic, 2026

Hoer auf, Agenten neu zu erfinden. Fang an, sie zu komponieren.

## Warum multi-agent?

| | multi-agent | CrewAI | LangGraph | OpenAI SDK | Claude SDK |
|---|:---:|:---:|:---:|:---:|:---:|
| Framework-unabhaengige Definitionen | **Ja** | Nein | Nein | Nein | Nein |
| Export auf jede KI-Plattform | **Ja** | Nein | Nein | Nein | Nein |
| Agenten-Katalog mit 50+ Rollen | **Ja** | ~10 | ~5 | ~3 | ~5 |
| Muster-Bibliothek (8 Muster) | **Ja** | 2 | 3 | 2 | 2 |
| Integrierte Kostenschaetzung | **Ja** | Nein | Nein | Nein | Nein |
| Agenten-Empfehlungsengine | **Ja** | Nein | Nein | Nein | Nein |
| Kompatibel mit jedem LLM | **Ja** | Ja | Ja | Nur OpenAI | Nur Claude |
| MCP nativ | **Ja** | Teilweise | Adapter | Ja | Ja |
| Zeilen Kerncode | **~600** | 18K | 25K | 8K | 12K |

## Schnellstart

```bash
pip install multi-agent
```

### 1. Katalog durchsuchen

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

### 2. Eine Agenten-Definition verwenden

```python
from multiagent import Catalog, patterns

# Agenten aus dem Katalog laden
catalog = Catalog()
reviewer = catalog.load("code/code-reviewer")
test_writer = catalog.load("code/test-writer")

# Mit einem Muster kombinieren
team = patterns.supervisor_worker(
    supervisor=reviewer,
    workers=[test_writer],
    model="claude-sonnet-4-6"  # oder ein beliebiges Modell
)

result = team.run("Review this PR and write missing tests", context={
    "diff": open("changes.diff").read()
})
```

### 3. Oder mit deinem bevorzugten Framework verwenden

```python
# CrewAI-Adapter
from multiagent.adapters import crewai
crew = crewai.from_catalog(["code/code-reviewer", "code/test-writer"])
result = crew.kickoff()

# LangGraph-Adapter
from multiagent.adapters import langgraph
graph = langgraph.from_catalog(["research/deep-researcher", "research/fact-checker"])
result = graph.invoke({"query": "Latest AI agent frameworks"})

# OpenAI Agents SDK-Adapter
from multiagent.adapters import openai_sdk
agent = openai_sdk.from_catalog("code/code-reviewer")
result = agent.run("Review this code")
```

## Agenten-Katalog

| Kategorie | Agenten | Beschreibung |
|-----------|---------|--------------|
| **[code/](../../catalog/code/)** | `code-reviewer` `code-generator` `test-writer` `refactorer` `debugger` `security-auditor` `documentation-writer` `pr-summarizer` | Software-Entwicklungslebenszyklus |
| **[research/](../../catalog/research/)** | `deep-researcher` `web-scraper` `fact-checker` `paper-analyst` `competitive-intel` | Recherche und Analyse |
| **[data/](../../catalog/data/)** | `data-analyst` `sql-generator` `report-writer` | Daten-Engineering und -Analyse |
| **[devops/](../../catalog/devops/)** | `ci-cd-agent` `infra-provisioner` `monitoring-agent` `incident-responder` | Infrastruktur und Betrieb |
| **[content/](../../catalog/content/)** | `writer` `editor` `translator` `seo-optimizer` | Content-Erstellungs-Pipeline |
| **[finance/](../../catalog/finance/)** | `trading-analyst` `portfolio-optimizer` `financial-reporter` `fraud-detector` `tax-advisor` | Finanzanalyse und Compliance |
| **[support/](../../catalog/support/)** | `customer-support` `ticket-router` `knowledge-base-builder` `escalation-agent` | Kundenservice-Pipeline |
| **[legal/](../../catalog/legal/)** | `contract-reviewer` `legal-researcher` `compliance-checker` `document-drafter` | Recht und Compliance |
| **[personal/](../../catalog/personal/)** | `email-assistant` `meeting-scheduler` `note-taker` `task-manager` | Persoenliche Produktivitaet |
| **[security/](../../catalog/security/)** | `vulnerability-scanner` `log-analyzer` `access-reviewer` `incident-analyst` | Sicherheitsoperationen |
| **[orchestration/](../../catalog/orchestration/)** | `task-router` `cost-optimizer` `quality-gate` | Meta-Agenten zur Koordination |

## Smarte Verbesserungen

Verbessere jeden Agenten mit forschungsgestuetzten Prompt-Engineering-Techniken:

```bash
multiagent enhance code/code-reviewer -p all
```

| Verbesserung | Effekt | Quelle |
|-------------|--------|--------|
| `reasoning` | +20% Aufgabenabschluss | OpenAI SWE-bench |
| `error_recovery` | 5-stufige Wiederholungshierarchie | Anthropic Engineering |
| `verification` | Selbstpruefung vor der Ausgabe | Claude Code intern |
| `confidence` | -40-60% Halluzinationen | Akademische Forschung |
| `tool_discipline` | Schneller, weniger Fehler | OpenAI GPT-5.4-Leitfaden |
| `failure_modes` | Vermeidet 6 Anti-Muster | Studie 120+ geleakter Prompts |
| `context_management` | Bessere Langzeitaufgaben | LangChain Context Engineering |
| `information_priority` | Fakten statt Vermutungen | Manus AI / Anthropic |

## Export auf jede Plattform

```bash
multiagent export code/code-reviewer claude-code -o .agents/skills
multiagent export code/code-reviewer codex
multiagent export code/code-reviewer gemini -o ./adk-agents
multiagent export code/code-reviewer chatgpt
multiagent export code/code-reviewer raw
```

| Ziel | Format | Kompatibel mit |
|------|--------|----------------|
| `claude-code` | `.md`-Skill-Dateien | Claude Code, Claude Desktop |
| `codex` | AGENTS.md-Abschnitte | OpenAI Codex, OpenClaw |
| `gemini` | ADK-YAML-Konfiguration | Google Gemini, Vertex AI |
| `chatgpt` | Systemanweisungen | ChatGPT, Custom GPTs |
| `raw` | Einfacher System-Prompt | **Jedes LLM** — Ollama, LM Studio, llama.cpp, vLLM, etc. |

## Interaktiver Playground

Durchsuche Agenten, teste Verbesserungen, vergleiche Kosten und baue Teams visuell im Browser:

**[Playground oeffnen](../../web/index.html)** (kein Backend noetig — rein statisches HTML)

## Mitwirken

Wir freuen uns ueber Beitraege! Siehe [CONTRIBUTING.md](../../CONTRIBUTING.md) fuer Details.

- **Agent hinzufuegen** — Eine neue YAML-Agenten-Definition zum Katalog einreichen
- **Muster hinzufuegen** — Ein neues Orchestrierungsmuster mit Beispielen dokumentieren
- **Adapter hinzufuegen** — Einen Framework-Adapter erstellen
- **Dokumentation verbessern** — Bessere Beispiele, Tutorials, Uebersetzungen

---

<p align="center">
  <sub>Wenn dir dieses Projekt beim Bau besserer Agenten hilft, wuerden wir uns ueber einen Stern freuen.</sub>
</p>
