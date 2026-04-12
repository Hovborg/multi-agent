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
  <strong>AI 智能体模式权威目录。一次定义，任意框架运行。</strong>
</p>

<p align="center">
  <a href="https://github.com/Hovborg/multi-agent/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <a href="https://pypi.org/project/multi-agent/"><img src="https://img.shields.io/pypi/v/multi-agent.svg" alt="PyPI"></a>
  <a href="https://github.com/Hovborg/multi-agent/stargazers"><img src="https://img.shields.io/github/stars/Hovborg/multi-agent?style=social" alt="GitHub Stars"></a>
  <a href="https://github.com/Hovborg/multi-agent/actions"><img src="https://img.shields.io/github/actions/workflow/status/Hovborg/multi-agent/ci.yml" alt="CI"></a>
  <a href="https://discord.gg/multiagent"><img src="https://img.shields.io/discord/placeholder?label=Discord&logo=discord" alt="Discord"></a>
</p>

<p align="center">
  <a href="#快速开始">快速开始</a> &bull;
  <a href="#智能体目录">智能体目录</a> &bull;
  <a href="#智能增强">智能增强</a> &bull;
  <a href="#导出到任意平台">导出</a> &bull;
  <a href="../../web/">在线演练场</a> &bull;
  <a href="../../CONTRIBUTING.md">参与贡献</a>
</p>

---

**50+ 经过实战检验的智能体定义。11 个类别。8 种编排模式。6 个框架适配器。5 个导出目标。零锁定。**

`multi-agent` 是一个框架无关的生产级 AI 智能体模式目录。用 YAML 定义一次智能体，即可在 CrewAI、LangGraph、OpenAI Agents SDK、Claude SDK、Google ADK 或 smolagents 上运行。

> *"57% 的企业智能体故障是编排故障，而非模型故障。"* — Anthropic, 2026

不要重复造轮子。开始组合智能体吧。

## 为什么选择 multi-agent？

| | multi-agent | CrewAI | LangGraph | OpenAI SDK | Claude SDK |
|---|:---:|:---:|:---:|:---:|:---:|
| 框架无关定义 | **是** | 否 | 否 | 否 | 否 |
| 导出至任意 AI 平台 | **是** | 否 | 否 | 否 | 否 |
| 50+ 角色智能体目录 | **是** | ~10 | ~5 | ~3 | ~5 |
| 模式库（8 种模式） | **是** | 2 | 3 | 2 | 2 |
| 内置成本估算 | **是** | 否 | 否 | 否 | 否 |
| 智能体推荐引擎 | **是** | 否 | 否 | 否 | 否 |
| 支持任意 LLM | **是** | 是 | 是 | 仅 OpenAI | 仅 Claude |
| 原生 MCP 支持 | **是** | 部分 | 适配器 | 是 | 是 |
| 核心代码行数 | **~600** | 18K | 25K | 8K | 12K |

## 快速开始

```bash
pip install multi-agent
```

### 1. 浏览目录

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

### 2. 使用智能体定义

```python
from multiagent import Catalog, patterns

# 从目录加载智能体
catalog = Catalog()
reviewer = catalog.load("code/code-reviewer")
test_writer = catalog.load("code/test-writer")

# 用模式组合
team = patterns.supervisor_worker(
    supervisor=reviewer,
    workers=[test_writer],
    model="claude-sonnet-4-6"  # 或任意模型
)

result = team.run("Review this PR and write missing tests", context={
    "diff": open("changes.diff").read()
})
```

### 3. 或与你喜欢的框架一起使用

```python
# CrewAI 适配器
from multiagent.adapters import crewai
crew = crewai.from_catalog(["code/code-reviewer", "code/test-writer"])
result = crew.kickoff()

# LangGraph 适配器
from multiagent.adapters import langgraph
graph = langgraph.from_catalog(["research/deep-researcher", "research/fact-checker"])
result = graph.invoke({"query": "Latest AI agent frameworks"})

# OpenAI Agents SDK 适配器
from multiagent.adapters import openai_sdk
agent = openai_sdk.from_catalog("code/code-reviewer")
result = agent.run("Review this code")
```

## 智能体目录

| 类别 | 智能体 | 描述 |
|------|--------|------|
| **[code/](../../catalog/code/)** | `code-reviewer` `code-generator` `test-writer` `refactorer` `debugger` `security-auditor` `documentation-writer` `pr-summarizer` | 软件开发全生命周期 |
| **[research/](../../catalog/research/)** | `deep-researcher` `web-scraper` `fact-checker` `paper-analyst` `competitive-intel` | 研究与分析 |
| **[data/](../../catalog/data/)** | `data-analyst` `sql-generator` `report-writer` | 数据工程与分析 |
| **[devops/](../../catalog/devops/)** | `ci-cd-agent` `infra-provisioner` `monitoring-agent` `incident-responder` | 基础设施与运维 |
| **[content/](../../catalog/content/)** | `writer` `editor` `translator` `seo-optimizer` | 内容创作流水线 |
| **[finance/](../../catalog/finance/)** | `trading-analyst` `portfolio-optimizer` `financial-reporter` `fraud-detector` `tax-advisor` | 金融分析与合规 |
| **[support/](../../catalog/support/)** | `customer-support` `ticket-router` `knowledge-base-builder` `escalation-agent` | 客户服务流水线 |
| **[legal/](../../catalog/legal/)** | `contract-reviewer` `legal-researcher` `compliance-checker` `document-drafter` | 法律与合规 |
| **[personal/](../../catalog/personal/)** | `email-assistant` `meeting-scheduler` `note-taker` `task-manager` | 个人效率工具 |
| **[security/](../../catalog/security/)** | `vulnerability-scanner` `log-analyzer` `access-reviewer` `incident-analyst` | 安全运营 |
| **[orchestration/](../../catalog/orchestration/)** | `task-router` `cost-optimizer` `quality-gate` | 协调用元智能体 |

## 智能增强

用经过研究验证的提示工程技术提升任意智能体：

```bash
multiagent enhance code/code-reviewer -p all
```

| 增强项 | 效果 | 来源 |
|--------|------|------|
| `reasoning` | 任务完成率 +20% | OpenAI SWE-bench |
| `error_recovery` | 5 级重试层级 | Anthropic 工程实践 |
| `verification` | 输出前自检 | Claude Code 内部 |
| `confidence` | 幻觉减少 40-60% | 学术研究 |
| `tool_discipline` | 更快、更少错误 | OpenAI GPT-5.4 指南 |
| `failure_modes` | 避免 6 种反模式 | 120+ 泄露提示词研究 |
| `context_management` | 改善长任务表现 | LangChain 上下文工程 |
| `information_priority` | 事实优先于猜测 | Manus AI / Anthropic |

## 导出到任意平台

```bash
multiagent export code/code-reviewer claude-code -o .agents/skills
multiagent export code/code-reviewer codex
multiagent export code/code-reviewer gemini -o ./adk-agents
multiagent export code/code-reviewer chatgpt
multiagent export code/code-reviewer raw
```

| 目标 | 格式 | 适用于 |
|------|------|--------|
| `claude-code` | `.md` 技能文件 | Claude Code, Claude Desktop |
| `codex` | AGENTS.md 章节 | OpenAI Codex, OpenClaw |
| `gemini` | ADK YAML 配置 | Google Gemini, Vertex AI |
| `chatgpt` | 系统指令 | ChatGPT, Custom GPTs |
| `raw` | 纯系统提示 | **任意 LLM** — Ollama, LM Studio, llama.cpp, vLLM 等 |

## 在线演练场

在浏览器中浏览智能体、测试增强、比较成本、可视化构建团队：

**[打开演练场](../../web/index.html)**（无需后端 — 纯静态 HTML）

## 参与贡献

我们欢迎贡献！详见 [CONTRIBUTING.md](../../CONTRIBUTING.md)。

- **添加智能体** — 向目录提交新的 YAML 智能体定义
- **添加模式** — 记录新的编排模式及示例
- **添加适配器** — 创建框架适配器
- **改进文档** — 更好的示例、教程、翻译

---

<p align="center">
  <sub>如果这个项目对你构建更好的智能体有帮助，请给我们一个 Star。</sub>
</p>
