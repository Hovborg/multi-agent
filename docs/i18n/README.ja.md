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
  <strong>AIエージェントパターンの決定版カタログ。一度定義すれば、どのフレームワークでも動作。</strong>
</p>

<p align="center">
  <a href="https://github.com/Hovborg/multi-agent/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <a href="https://pypi.org/project/multi-agent/"><img src="https://img.shields.io/pypi/v/multi-agent.svg" alt="PyPI"></a>
  <a href="https://github.com/Hovborg/multi-agent/stargazers"><img src="https://img.shields.io/github/stars/Hovborg/multi-agent?style=social" alt="GitHub Stars"></a>
  <a href="https://github.com/Hovborg/multi-agent/actions"><img src="https://img.shields.io/github/actions/workflow/status/Hovborg/multi-agent/ci.yml" alt="CI"></a>
  <a href="https://discord.gg/multiagent"><img src="https://img.shields.io/discord/placeholder?label=Discord&logo=discord" alt="Discord"></a>
</p>

<p align="center">
  <a href="#クイックスタート">クイックスタート</a> &bull;
  <a href="#エージェントカタログ">エージェントカタログ</a> &bull;
  <a href="#スマート強化">スマート強化</a> &bull;
  <a href="#任意のプラットフォームへエクスポート">エクスポート</a> &bull;
  <a href="../../web/">プレイグラウンド</a> &bull;
  <a href="../../CONTRIBUTING.md">コントリビュート</a>
</p>

---

**48個のエージェント定義。11カテゴリ。8つのオーケストレーションパターン。6つのフレームワークアダプター。6つのエクスポート先。ベンダーロックインなし。**

`multi-agent` はフレームワーク非依存のプロダクション対応AIエージェントパターンカタログです。YAMLでエージェントを一度定義すれば、CrewAI、LangGraph、OpenAI Agents SDK、Claude SDK、Google ADK、smolagentsのいずれでも実行できます。

エージェントの車輪の再発明はやめましょう。組み合わせて使いましょう。

## なぜ multi-agent か？

| | multi-agent | CrewAI | LangGraph | OpenAI SDK | Claude SDK |
|---|:---:|:---:|:---:|:---:|:---:|
| フレームワーク非依存の定義 | **対応** | 非対応 | 非対応 | 非対応 | 非対応 |
| 任意のAIプラットフォームへエクスポート | **対応** | 非対応 | 非対応 | 非対応 | 非対応 |
| 再利用可能なエージェントカタログ | **対応** | フレームワーク固有 | フレームワーク固有 | フレームワーク固有 | フレームワーク固有 |
| パターンライブラリ（8パターン） | **対応** | 2 | 3 | 2 | 2 |
| 組み込みコスト見積り | **対応** | 非対応 | 非対応 | 非対応 | 非対応 |
| エージェント推薦エンジン | **対応** | 非対応 | 非対応 | 非対応 | 非対応 |
| 任意のLLMに対応 | **対応** | 対応 | 対応 | OpenAIのみ | Claudeのみ |
| MCPネイティブ | **対応** | 部分的 | アダプター | 対応 | 対応 |

## クイックスタート

```bash
pip install multi-agent
```

### 1. カタログを検索

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

### 2. エージェント定義を使用

```python
from multiagent import Catalog, patterns

# カタログからエージェントを読み込み
catalog = Catalog()
reviewer = catalog.load("code/code-reviewer")
test_writer = catalog.load("code/test-writer")

# パターンで組み合わせ
team = patterns.supervisor_worker(
    supervisor=reviewer,
    workers=[test_writer],
    model="claude-sonnet-4-6"  # または任意のモデル
)

result = team.run("Review this PR and write missing tests", context={
    "diff": open("changes.diff").read()
})
```

### 3. お好みのフレームワークで使用

```python
# CrewAI アダプター
from multiagent.adapters import crewai
crew = crewai.from_catalog(["code/code-reviewer", "code/test-writer"])
result = crew.kickoff()

# LangGraph アダプター
from multiagent.adapters import langgraph
graph = langgraph.from_catalog(["research/deep-researcher", "research/fact-checker"])
result = graph.invoke({"query": "Latest AI agent frameworks"})

# OpenAI Agents SDK アダプター
from multiagent.adapters import openai_sdk
agent = openai_sdk.from_catalog("code/code-reviewer")
result = agent.run("Review this code")
```

## エージェントカタログ

| カテゴリ | エージェント | 説明 |
|----------|-------------|------|
| **[code/](../../catalog/code/)** | `code-reviewer` `code-generator` `test-writer` `refactorer` `debugger` `security-auditor` `documentation-writer` `pr-summarizer` | ソフトウェア開発ライフサイクル |
| **[research/](../../catalog/research/)** | `deep-researcher` `web-scraper` `fact-checker` `paper-analyst` `competitive-intel` | リサーチと分析 |
| **[data/](../../catalog/data/)** | `data-analyst` `sql-generator` `report-writer` | データエンジニアリングと分析 |
| **[devops/](../../catalog/devops/)** | `ci-cd-agent` `infra-provisioner` `monitoring-agent` `incident-responder` | インフラとオペレーション |
| **[content/](../../catalog/content/)** | `writer` `editor` `translator` `seo-optimizer` | コンテンツ制作パイプライン |
| **[finance/](../../catalog/finance/)** | `trading-analyst` `portfolio-optimizer` `financial-reporter` `fraud-detector` `tax-advisor` | 金融分析とコンプライアンス |
| **[support/](../../catalog/support/)** | `customer-support` `ticket-router` `knowledge-base-builder` `escalation-agent` | カスタマーサービスパイプライン |
| **[legal/](../../catalog/legal/)** | `contract-reviewer` `legal-researcher` `compliance-checker` `document-drafter` | 法務とコンプライアンス |
| **[personal/](../../catalog/personal/)** | `email-assistant` `meeting-scheduler` `note-taker` `task-manager` | パーソナル生産性向上 |
| **[security/](../../catalog/security/)** | `vulnerability-scanner` `log-analyzer` `access-reviewer` `incident-analyst` | セキュリティオペレーション |
| **[orchestration/](../../catalog/orchestration/)** | `task-router` `cost-optimizer` `quality-gate` | 調整用メタエージェント |

## スマート強化

研究に裏付けられたプロンプトエンジニアリング技術であらゆるエージェントを強化：

```bash
multiagent enhance code/code-reviewer -p all
```

| 強化項目 | 効果 | 出典 |
|----------|------|------|
| `reasoning` | タスク完了率 +20% | OpenAI SWE-bench |
| `error_recovery` | 5段階リトライ階層 | Anthropicエンジニアリング |
| `verification` | 出力前セルフチェック | Claude Code内部 |
| `confidence` | ハルシネーション 40-60%削減 | 学術研究 |
| `tool_discipline` | 高速化、エラー削減 | OpenAI GPT-5.4ガイド |
| `failure_modes` | 6つのアンチパターンを回避 | 120以上のリークプロンプト研究 |
| `context_management` | 長時間タスクの改善 | LangChainコンテキストエンジニアリング |
| `information_priority` | 推測より事実を優先 | Manus AI / Anthropic |

## 任意のプラットフォームへエクスポート

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

| ターゲット | フォーマット | 対応サービス |
|------------|-------------|-------------|
| `claude-code` | `.md` subagent ファイル | Claude Code `.claude/agents/` |
| `agentskill` | `SKILL.md` 形式 Markdown | AgentSkills 互換ツール |
| `a2a-agent-card` | Agent Card JSON | `.well-known/agent-card.json` による A2A discovery |
| `codex` | AGENTS.md セクション | OpenAI Codex, OpenClaw |
| `codex-config` | `.codex/config.toml` スニペット | OpenAI Codex multi-agent ロール |
| `gemini` | ADK YAML設定 | Google Gemini, Vertex AI |
| `chatgpt` | システムインストラクション | ChatGPT, Custom GPTs |
| `raw` | プレーンシステムプロンプト | **任意のLLM** — Ollama, LM Studio, llama.cpp, vLLM等 |

## インタラクティブプレイグラウンド

ブラウザでエージェントを閲覧、強化をテスト、コストを比較、チームを視覚的に構築：

**[プレイグラウンドを開く](../../web/index.html)**（バックエンド不要 — 純粋な静的HTML）

## コントリビュート

コントリビューション大歓迎です！詳しくは [CONTRIBUTING.md](../../CONTRIBUTING.md) をご覧ください。

- **エージェントを追加** — カタログに新しいYAMLエージェント定義を提出
- **パターンを追加** — 新しいオーケストレーションパターンを例付きで文書化
- **アダプターを追加** — フレームワークアダプターを作成
- **ドキュメントを改善** — より良い例、チュートリアル、翻訳

---

<p align="center">
  <sub>このプロジェクトがより良いエージェント構築に役立ったら、Starをいただけると嬉しいです。</sub>
</p>
