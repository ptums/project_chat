# Implementation Plan: Ollama Conversation Organizer

**Branch**: `001-ollama-organizer` | **Date**: 2025-11-25 | **Spec**: [/specs/001-ollama-organizer/spec.md](./spec.md)  
**Input**: Feature specification from `/specs/001-ollama-organizer/spec.md`

## Summary

Add an Ollama-powered memory layer invoked via `/save` that summarizes chat sessions into a new `conversation_index` table, supplies richer context to GPT-5.1-mini, and exposes tooling to re-index past sessions. Work covers schema changes, an HTTP helper for Ollama, transcript/prompt utilities, indexing workflows (CLI and batch script), and a project-aware context builder consumed by the chat engine.

## Technical Context

**Language/Version**: Python 3.10 (repo `.python-version` + venv)  
**Primary Dependencies**: psycopg2, Flask, OpenAI SDK, `requests` (new for Ollama client)  
**Storage**: PostgreSQL (existing conversations + new `conversation_index` table)  
**Testing**: Existing project relies on manual + ad-hoc testing (no dedicated framework specified)  
**Target Platform**: Local CLI + Flask API running on macOS/Linux dev hosts  
**Project Type**: Single repository housing CLI, API server, and shared `brain_core` modules  
**Performance Goals**: Fast enough for interactive CLI; `/save` should finish <10s; context builder must not block main chat loop noticeably  
**Constraints**: Must avoid breaking current chat flows; new components must work in dev/prod modes with configurability via `.env`; Ollama endpoint varies per machine  
**Scale/Scope**: Single user workflow, dozens-to-hundreds of sessions; conversation index limited to ~200 recent entries per project for context building

## Constitution Check

Constitution file currently contains placeholders with no enforced principles, so no blocking gates. Continue to document reasoning and keep changes incremental to stay aligned with implied simplicity/observability expectations.

## Project Structure

### Documentation (this feature)

```text
specs/001-ollama-organizer/
├── plan.md          # This file (/speckit.plan output)
├── research.md      # Phase 0 research findings
├── data-model.md    # Phase 1 data contracts
├── quickstart.md    # Phase 1 implementation guide
├── contracts/       # Phase 1 API/CLI contract notes
└── tasks.md         # Generated later via /speckit.tasks
```

### Source Code (repository root)

```text
brain_core/
├── chat.py
├── config.py
├── conversation_indexer.py   # NEW
├── context_builder.py        # NEW
├── db.py
├── mock_client.py
├── usage_tracker.py
└── __init__.py

chat_cli.py
api_server.py
reindex_conversations.py      # NEW script
.env.example / README.md
```

**Structure Decision**: Extend existing `brain_core` package with new helpers (Ollama client, indexer, context builder) and place operational scripts at repo root. CLI (`chat_cli.py`) orchestrates `/save`, while batch tooling lives in `reindex_conversations.py`.

## Complexity Tracking

Not required (no constitution violations identified).
