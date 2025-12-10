# Implementation Plan: Revamp DAAS RAG System

**Branch**: `014-revamp-daas-rag` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/014-revamp-daas-rag/spec.md`

## Summary

Revamp the DAAS RAG system to provide focused, cost-effective dream analysis retrieval. Remove existing DAAS retrieval code that uses conversation history, and implement a new system that retrieves related dreams by themes, symbols, or events while keeping each dream's events separate and self-contained. Remove debugging "Thinking" messages from the chat interface.

## Technical Context

**Language/Version**: Python 3.10+ (existing project standard)  
**Primary Dependencies**: Existing dependencies (psycopg2, OpenAI, pgvector)  
**Storage**: PostgreSQL with `conversation_index` table (existing schema)  
**Testing**: Manual testing (consistent with project standards)  
**Target Platform**: Linux/macOS CLI application  
**Project Type**: Single project (Python CLI)  
**Performance Goals**: RAG generation <500ms (similar to THN RAG target)  
**Constraints**:

- Token limit: <1000 tokens for RAG context
- No conversation history in RAG
- DAAS-tagged data only
- Cost-conscious retrieval (limit retrieved content)
  **Scale/Scope**:
- Single DAAS project retrieval
- 3-5 dreams per query (configurable)
- Existing database schema (no migrations needed)

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

No constitution violations identified. This feature:

- Follows existing project patterns (similar to THN RAG implementation)
- Uses existing database schema
- Maintains separation of concerns
- No breaking changes to existing functionality

## Project Structure

### Documentation (this feature)

```text
specs/014-revamp-daas-rag/
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
├── context_builder.py    # Modify: Remove old DAAS retrieval, add new implementation
├── daas_retrieval.py    # DELETE: Remove entire file
└── embedding_service.py  # Use existing: Vector similarity search

chat_cli.py              # Modify: Remove "Thinking for [PROJECT]" spinner messages
```

**Structure Decision**: Single project structure. All changes are modifications to existing files in `brain_core/` and `chat_cli.py`. No new modules required.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations identified.

## Phase 0: Research & Design Decisions ✅

**Status**: Complete - See `research.md` for all decisions.

### Research Tasks

1. **Vector Similarity Search for DAAS Dreams**

   - Research: How to extract themes/symbols/events from user query for vector search
   - Decision: Use full user message for embedding generation (similar to THN code search)
   - Rationale: Simpler than parsing themes/symbols, leverages existing embedding infrastructure

2. **Dream Formatting and Separation**

   - Research: Best format for presenting multiple dreams with clear boundaries
   - Decision: Use markdown-style separation with clear headers and separators
   - Rationale: Maintains readability while keeping dreams distinct

3. **Token Optimization Strategies**

   - Research: How to limit retrieved content while maintaining usefulness
   - Decision:
     - Truncate summaries to 300 chars
     - Truncate memory snippets to 200 chars
     - Limit to 3-5 dreams (configurable)
   - Rationale: Balances context richness with token efficiency

4. **Removing Debugging Messages**
   - Research: Where "Thinking" spinner is implemented
   - Decision: Remove spinner thread and thinking label from chat_cli.py
   - Rationale: Improves user experience by removing unnecessary visual noise

## Phase 1: Design & Contracts ✅

**Status**: Complete - See `data-model.md`, `contracts/api.md`, and `quickstart.md`.

### Data Model

**Existing Tables Used:**

- `conversation_index`: Contains DAAS dreams with embeddings
  - Fields used: `session_id`, `title`, `summary_short`, `memory_snippet`, `embedding`
  - Filter: `project = 'DAAS'`
  - Search: Vector similarity using `embedding <=> query_embedding`

**No Schema Changes Required**

### API Contracts

**Function: `build_daas_rag_context(user_message: str) -> Dict[str, Any]`**

- **Location**: `brain_core/context_builder.py`
- **Purpose**: Build RAG context for DAAS project
- **Input**: User message string
- **Output**: Dict with `context` (formatted string) and `notes` (list of source notes)
- **Behavior**:
  - Generate embedding for user_message
  - Query `conversation_index` WHERE `project = 'DAAS'` using vector similarity
  - Return top 3-5 dreams (configurable)
  - Format with clear separation between dreams
  - Truncate content to stay within token limits

**Integration Point: `build_project_context()`**

- Remove old DAAS retrieval logic (lines 704-786)
- Add call to `build_daas_rag_context()` for DAAS project
- Follow pattern similar to THN RAG implementation

### Quickstart Guide

**For Developers:**

1. Remove `brain_core/daas_retrieval.py` file
2. Remove DAAS-specific code from `build_project_context()` in `context_builder.py`
3. Implement `build_daas_rag_context()` function
4. Remove "Thinking" spinner from `chat_cli.py` (3 locations)
5. Test with DAAS project conversation

**For Users:**

- No changes to CLI interface
- RAG retrieval happens automatically for DAAS project
- No "Thinking" messages during processing

## Phase 2: Implementation Tasks

_(Tasks will be generated by `/speckit.tasks` command)_

## Success Metrics

1. ✅ `daas_retrieval.py` file deleted
2. ✅ Old DAAS code removed from `context_builder.py`
3. ✅ New `build_daas_rag_context()` function implemented
4. ✅ RAG retrieves 3-5 relevant dreams by themes/symbols/events
5. ✅ Dreams formatted with clear separation
6. ✅ No conversation history in RAG context
7. ✅ "Thinking" messages removed from chat interface
8. ✅ RAG generation completes in <500ms
9. ✅ RAG context stays under 1000 tokens
