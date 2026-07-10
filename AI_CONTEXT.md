Læs `/mnt/c/codex_projekts/.ai/infrastructure.md` for delt system-kontekst.
Læs `/mnt/c/codex_projekts/.ai/model-routing.md` for modelvalg og agent-delegering.

# Multi Agent - AI Context

Updated: 2026-07-11

## Purpose

Framework-agnostisk katalog af AI-agentmønstre, adapters og eksempler.

## Status

- Tilstand: Aktiv udvikling
- Port: ingen fast
- Root: `/mnt/c/codex_projekts/02-dev/06-multi-agent`

## Stack

Python package, docs, web playground

## Runtime Contract

- The catalog ships inside `src/multiagent/catalog_data/` and must load from an installed wheel.
- `multiagent route` is dry-run only; it returns additive `risk`, `context`, and `policy` data.
- `multiagent validate` is the authoritative schema and cross-reference check.
- No model provider, credential, environment variable, port, or live service is required.
- CI must test both the source checkout and an isolated wheel installation.

## Working Rules

- Start her, før du ændrer filer i denne mappe.
- Følg root-instruktionerne i `/mnt/c/codex_projekts/AGENTS.md`.
- Brug `rg` / `rg --files` til søgning.
- Hold ændringer inden for denne mappe, medmindre opgaven kræver tværgående ændringer.
- Commit aldrig secrets, tokens, private credentials eller live `.env`-filer.
- Opdater denne fil, hvis runtime, porte, status eller vigtige regler ændrer sig.

<!-- second-brain-sync:start -->
## Workspace Second Brain

- Shared local memory/search/control plane:
  `/mnt/c/codex_projekts/02-dev/02-second-brain`.
- Use it for source-bound cross-project recall, project cards, decisions,
  retrieval evals and workspace synthesis.
- Heavy/private data and indexes stay in
  `/mnt/c/codex_projekts/05-data/second-brain`.
- Do not copy raw private case data, credentials, logs, databases or model
  artifacts into this project context.
- Re-read the original source receipt before current-state claims.
- Refresh this block with:
  `python3 /mnt/c/codex_projekts/02-dev/02-second-brain/scripts/sync_workspace_docs.py --apply`.
<!-- second-brain-sync:end -->
