# Implementation Plan: THN Code RAG Pipeline Enhancement

**Branch**: `008-thn-code-rag-pipeline` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-thn-code-rag-pipeline/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a RAG (Retrieval-Augmented Generation) pipeline for THN project that indexes code from THN-related repositories, stores embeddings in PostgreSQL using pgvector, and retrieves relevant code snippets during THN conversations. This enables context-aware debugging and technical consultation that understands both the codebase and production environment. The implementation follows the DAAS RAG pattern but focuses on code files instead of conversation summaries.

## Technical Context

**Language/Version**: Python 3.10+ (existing project standard)  
**Primary Dependencies**: `psycopg2-binary`, `pgvector` (PostgreSQL extension), `openai` (existing), `gitpython` (for repository management), existing `brain_core.embedding_service` and `brain_core.db` modules  
**Storage**: PostgreSQL (new `code_index` table with pgvector for code embeddings), file system (`repos/` directory for cloned repositories)  
**Testing**: Manual testing (consistent with project standards), incremental indexing validation  
**Target Platform**: macOS/Linux (same as existing project)  
**Project Type**: Single project (CLI application with shared brain_core modules)  
**Performance Goals**: Code indexing processes 100-1000 files per batch; vector similarity search completes in <500ms; embedding generation respects OpenAI rate limits (3000 req/min)  
**Constraints**: Must not break existing chat flows; THN-only feature (other projects unchanged); code indexing is manual/incremental (not real-time); must handle large codebases efficiently  
**Scale/Scope**: Multiple THN repositories (tens to hundreds of files per repo); vector search over code snippets; top-k retrieval (default 5-10 snippets)

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

**Pre-Phase 0**: Constitution file contains placeholders, so no blocking gates. Continue to document reasoning and keep changes incremental.

**Post-Phase 1**:

- ✅ Extends existing infrastructure (pgvector, embedding_service) rather than creating new systems
- ✅ Maintains simplicity: THN-only feature, other projects unchanged
- ✅ Uses existing technologies (PostgreSQL, OpenAI SDK, pgvector) with minimal new dependencies (gitpython)
- ✅ No breaking changes to existing APIs or CLI commands
- ✅ Incremental enhancement to existing chat flow

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
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
├── embedding_service.py        # Existing - used for code embeddings
├── db.py                       # Existing - database connection
├── thn_code_indexer.py         # NEW - code indexing and embedding generation
├── thn_code_retrieval.py       # NEW - code retrieval for THN context
└── context_builder.py          # MODIFIED - integrate THN code retrieval

repos/                          # NEW - directory for cloned THN repositories
├── repo1/
├── repo2/
└── ...

scripts/
├── index_thn_code.py           # NEW - script to index THN repositories
└── backfill_thn_embeddings.py # NEW - backfill embeddings for existing code

db/migrations/
└── 003_thn_code_index.sql     # NEW - migration for code_index table

chat_cli.py                     # MODIFIED - integrate THN code retrieval in chat flow
```

**Structure Decision**: Single project structure. New modules follow DAAS pattern (`thn_code_indexer.py`, `thn_code_retrieval.py`). Repository cloning happens in `repos/` directory at project root. Indexing scripts in `scripts/` directory for manual execution.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A       |            |                                      |
