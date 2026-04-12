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
  <strong>AI 에이전트 패턴의 결정판 카탈로그. 한 번 정의하면 어떤 프레임워크에서든 실행.</strong>
</p>

<p align="center">
  <a href="https://github.com/Hovborg/multi-agent/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <a href="https://pypi.org/project/multi-agent/"><img src="https://img.shields.io/pypi/v/multi-agent.svg" alt="PyPI"></a>
  <a href="https://github.com/Hovborg/multi-agent/stargazers"><img src="https://img.shields.io/github/stars/Hovborg/multi-agent?style=social" alt="GitHub Stars"></a>
  <a href="https://github.com/Hovborg/multi-agent/actions"><img src="https://img.shields.io/github/actions/workflow/status/Hovborg/multi-agent/ci.yml" alt="CI"></a>
  <a href="https://discord.gg/multiagent"><img src="https://img.shields.io/discord/placeholder?label=Discord&logo=discord" alt="Discord"></a>
</p>

<p align="center">
  <a href="#빠른-시작">빠른 시작</a> &bull;
  <a href="#에이전트-카탈로그">에이전트 카탈로그</a> &bull;
  <a href="#스마트-강화">스마트 강화</a> &bull;
  <a href="#모든-플랫폼으로-내보내기">내보내기</a> &bull;
  <a href="../../web/">플레이그라운드</a> &bull;
  <a href="../../CONTRIBUTING.md">기여하기</a>
</p>

---

**50개 이상의 실전 검증된 에이전트 정의. 11개 카테고리. 8가지 오케스트레이션 패턴. 6개 프레임워크 어댑터. 5개 내보내기 대상. 벤더 종속 없음.**

`multi-agent`는 프레임워크에 구애받지 않는 프로덕션 레디 AI 에이전트 패턴 카탈로그입니다. YAML로 에이전트를 한 번 정의하면 CrewAI, LangGraph, OpenAI Agents SDK, Claude SDK, Google ADK, smolagents 어디서든 실행할 수 있습니다.

> *"기업 에이전트 장애의 57%는 모델 장애가 아닌 오케스트레이션 장애입니다."* — Anthropic, 2026

에이전트를 다시 만들지 마세요. 조합하세요.

## 왜 multi-agent인가?

| | multi-agent | CrewAI | LangGraph | OpenAI SDK | Claude SDK |
|---|:---:|:---:|:---:|:---:|:---:|
| 프레임워크 비종속 정의 | **지원** | 미지원 | 미지원 | 미지원 | 미지원 |
| 모든 AI 플랫폼으로 내보내기 | **지원** | 미지원 | 미지원 | 미지원 | 미지원 |
| 50개 이상 역할의 에이전트 카탈로그 | **지원** | ~10 | ~5 | ~3 | ~5 |
| 패턴 라이브러리 (8개 패턴) | **지원** | 2 | 3 | 2 | 2 |
| 내장 비용 추정 | **지원** | 미지원 | 미지원 | 미지원 | 미지원 |
| 에이전트 추천 엔진 | **지원** | 미지원 | 미지원 | 미지원 | 미지원 |
| 모든 LLM 지원 | **지원** | 지원 | 지원 | OpenAI 전용 | Claude 전용 |
| MCP 네이티브 | **지원** | 부분적 | 어댑터 | 지원 | 지원 |
| 코어 코드 라인 수 | **~600** | 18K | 25K | 8K | 12K |

## 빠른 시작

```bash
pip install multi-agent
```

### 1. 카탈로그 검색

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

### 2. 에이전트 정의 사용

```python
from multiagent import Catalog, patterns

# 카탈로그에서 에이전트 로드
catalog = Catalog()
reviewer = catalog.load("code/code-reviewer")
test_writer = catalog.load("code/test-writer")

# 패턴으로 조합
team = patterns.supervisor_worker(
    supervisor=reviewer,
    workers=[test_writer],
    model="claude-sonnet-4-6"  # 또는 원하는 모델
)

result = team.run("Review this PR and write missing tests", context={
    "diff": open("changes.diff").read()
})
```

### 3. 선호하는 프레임워크에서 사용

```python
# CrewAI 어댑터
from multiagent.adapters import crewai
crew = crewai.from_catalog(["code/code-reviewer", "code/test-writer"])
result = crew.kickoff()

# LangGraph 어댑터
from multiagent.adapters import langgraph
graph = langgraph.from_catalog(["research/deep-researcher", "research/fact-checker"])
result = graph.invoke({"query": "Latest AI agent frameworks"})

# OpenAI Agents SDK 어댑터
from multiagent.adapters import openai_sdk
agent = openai_sdk.from_catalog("code/code-reviewer")
result = agent.run("Review this code")
```

## 에이전트 카탈로그

| 카테고리 | 에이전트 | 설명 |
|----------|----------|------|
| **[code/](../../catalog/code/)** | `code-reviewer` `code-generator` `test-writer` `refactorer` `debugger` `security-auditor` `documentation-writer` `pr-summarizer` | 소프트웨어 개발 라이프사이클 |
| **[research/](../../catalog/research/)** | `deep-researcher` `web-scraper` `fact-checker` `paper-analyst` `competitive-intel` | 리서치 및 분석 |
| **[data/](../../catalog/data/)** | `data-analyst` `sql-generator` `report-writer` | 데이터 엔지니어링 및 분석 |
| **[devops/](../../catalog/devops/)** | `ci-cd-agent` `infra-provisioner` `monitoring-agent` `incident-responder` | 인프라 및 운영 |
| **[content/](../../catalog/content/)** | `writer` `editor` `translator` `seo-optimizer` | 콘텐츠 제작 파이프라인 |
| **[finance/](../../catalog/finance/)** | `trading-analyst` `portfolio-optimizer` `financial-reporter` `fraud-detector` `tax-advisor` | 금융 분석 및 컴플라이언스 |
| **[support/](../../catalog/support/)** | `customer-support` `ticket-router` `knowledge-base-builder` `escalation-agent` | 고객 서비스 파이프라인 |
| **[legal/](../../catalog/legal/)** | `contract-reviewer` `legal-researcher` `compliance-checker` `document-drafter` | 법률 및 컴플라이언스 |
| **[personal/](../../catalog/personal/)** | `email-assistant` `meeting-scheduler` `note-taker` `task-manager` | 개인 생산성 도구 |
| **[security/](../../catalog/security/)** | `vulnerability-scanner` `log-analyzer` `access-reviewer` `incident-analyst` | 보안 운영 |
| **[orchestration/](../../catalog/orchestration/)** | `task-router` `cost-optimizer` `quality-gate` | 조정용 메타 에이전트 |

## 스마트 강화

연구 기반 프롬프트 엔지니어링 기법으로 모든 에이전트를 강화:

```bash
multiagent enhance code/code-reviewer -p all
```

| 강화 항목 | 효과 | 출처 |
|-----------|------|------|
| `reasoning` | 태스크 완료율 +20% | OpenAI SWE-bench |
| `error_recovery` | 5단계 재시도 계층 | Anthropic 엔지니어링 |
| `verification` | 출력 전 자체 검증 | Claude Code 내부 |
| `confidence` | 환각 40-60% 감소 | 학술 연구 |
| `tool_discipline` | 더 빠르고 오류 감소 | OpenAI GPT-5.4 가이드 |
| `failure_modes` | 6가지 안티패턴 회피 | 120+ 유출 프롬프트 연구 |
| `context_management` | 장시간 태스크 개선 | LangChain 컨텍스트 엔지니어링 |
| `information_priority` | 추측보다 사실 우선 | Manus AI / Anthropic |

## 모든 플랫폼으로 내보내기

```bash
multiagent export code/code-reviewer claude-code -o .agents/skills
multiagent export code/code-reviewer codex
multiagent export code/code-reviewer gemini -o ./adk-agents
multiagent export code/code-reviewer chatgpt
multiagent export code/code-reviewer raw
```

| 대상 | 형식 | 호환 서비스 |
|------|------|------------|
| `claude-code` | `.md` 스킬 파일 | Claude Code, Claude Desktop |
| `codex` | AGENTS.md 섹션 | OpenAI Codex, OpenClaw |
| `gemini` | ADK YAML 설정 | Google Gemini, Vertex AI |
| `chatgpt` | 시스템 인스트럭션 | ChatGPT, Custom GPTs |
| `raw` | 플레인 시스템 프롬프트 | **모든 LLM** — Ollama, LM Studio, llama.cpp, vLLM 등 |

## 인터랙티브 플레이그라운드

브라우저에서 에이전트 탐색, 강화 테스트, 비용 비교, 팀 시각적 구성:

**[플레이그라운드 열기](../../web/index.html)** (백엔드 불필요 — 순수 정적 HTML)

## 기여하기

기여를 환영합니다! 자세한 내용은 [CONTRIBUTING.md](../../CONTRIBUTING.md)를 참조하세요.

- **에이전트 추가** — 카탈로그에 새로운 YAML 에이전트 정의 제출
- **패턴 추가** — 예제와 함께 새로운 오케스트레이션 패턴 문서화
- **어댑터 추가** — 프레임워크 어댑터 작성
- **문서 개선** — 더 나은 예제, 튜토리얼, 번역

---

<p align="center">
  <sub>이 프로젝트가 더 나은 에이전트를 만드는 데 도움이 되었다면, Star를 눌러주세요.</sub>
</p>
