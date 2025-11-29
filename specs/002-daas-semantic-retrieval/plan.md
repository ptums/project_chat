# Implementation Plan: DAAS Semantic Dream Retrieval and Streaming Responses

**Branch**: `002-daas-semantic-retrieval` | **Date**: 2025-01-27 | **Spec**: [/specs/002-daas-semantic-retrieval/spec.md](./spec.md)  
**Input**: Feature specification from `/specs/002-daas-semantic-retrieval/spec.md`

## Summary

Implement custom retrieval rules for DAAS project that support both single-dream queries (by quoted title) and pattern-based queries (via vector similarity search). Add semantic vector embeddings to DAAS conversation entries to enable theme and pattern recognition across dreams. Implement streaming response display for both CLI and API interfaces to provide ChatGPT-like progressive text display. Work covers embedding generation/storage, vector similarity search, quoted title detection, retrieval mode routing, and streaming response infrastructure.

## Technical Context

**Language/Version**: Python 3.10+ (repo `.python-version` + venv)  
**Primary Dependencies**: psycopg2, Flask, OpenAI SDK, `requests` (existing), `pgvector` extension (PostgreSQL), OpenAI embeddings API  
**Storage**: PostgreSQL (existing `conversation_index` table + new `embedding` column for DAAS entries)  
**Testing**: Existing project relies on manual + ad-hoc testing (no dedicated framework specified)  
**Target Platform**: Local CLI + Flask API running on macOS/Linux dev hosts  
**Project Type**: Single repository housing CLI, API server, and shared `brain_core` modules  
**Performance Goals**: Vector similarity search completes in <500ms; streaming responses begin within 2 seconds; embedding backfill processes 50 entries per batch with 1s delay (3000 req/min rate limit)  
**Constraints**: Must avoid breaking current chat flows; DAAS-only feature (other projects unchanged); embeddings only for DAAS project entries; streaming must work in both CLI and API contexts  
**Scale/Scope**: Single user workflow, dozens-to-hundreds of DAAS dream sessions; vector search over DAAS entries only; top-k retrieval (default 5-10 dreams)

## Constitution Check

**Pre-Phase 0**: Constitution file currently contains placeholders with no enforced principles, so no blocking gates. Continue to document reasoning and keep changes incremental to stay aligned with implied simplicity/observability expectations.

**Post-Phase 1**:

- ✅ Extends existing infrastructure (conversation_index) rather than creating new systems
- ✅ Maintains simplicity: DAAS-only feature, other projects unchanged
- ✅ Uses existing technologies (PostgreSQL, OpenAI SDK) with minimal new dependencies (pgvector)
- ✅ No breaking changes to existing APIs or CLI commands
- ✅ Incremental enhancement to existing chat flow

## Project Structure

### Documentation (this feature)

```text
specs/002-daas-semantic-retrieval/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
brain_core/
├── chat.py
├── config.py
├── conversation_indexer.py
├── context_builder.py
├── db.py
├── memory.py
├── mock_client.py
├── usage_tracker.py
├── embedding_service.py    # NEW: Embedding generation and vector operations
├── daas_retrieval.py        # NEW: DAAS-specific retrieval logic (quoted title + vector search)
└── __init__.py

chat_cli.py                  # MODIFIED: Add streaming response support
api_server.py                # MODIFIED: Add streaming response support (if exists)
backfill_embeddings.py       # NEW: Script to generate embeddings for existing DAAS entries
```

**Structure Decision**: Extend existing `brain_core` package with new modules for embedding service and DAAS-specific retrieval. Add backfill script at repo root for operational tasks. Modify existing CLI and API to support streaming responses.

## Complexity Tracking

Not required (no constitution violations identified).
