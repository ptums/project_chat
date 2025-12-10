# Research: Enhance THN RAG System

**Feature**: 013-enhance-thn-rag  
**Date**: 2025-01-27

## Research Tasks

### 1. Conversation Retrieval Strategy

**Question**: Should we use vector similarity search for conversation retrieval, or simple date-based ordering?

**Findings**:

- `conversation_index` table has `indexed_at` column with DESC index for efficient date-based ordering
- THN conversations may not have embeddings (embeddings are DAAS-specific per migration 002)
- User requirement specifies "Last 5 Conversations" which implies chronological ordering
- Simple date-based query is faster and more predictable than vector search

**Decision**: Use simple date-based ordering (`ORDER BY indexed_at DESC LIMIT 5`) for conversation retrieval.

**Rationale**:

- Matches user requirement for "last 5 conversations"
- Faster query execution (uses existing index)
- More predictable results (always gets most recent conversations)
- No need for embeddings or similarity calculations

**Alternatives considered**:

- Vector similarity search: Rejected - THN conversations may not have embeddings, adds complexity
- Keyword-based relevance: Rejected - User wants chronological overview, not relevance-filtered

---

### 2. Handling Missing Fields

**Question**: How should we handle missing fields (e.g., if `summary_detailed` is NULL)?

**Findings**:

- `conversation_index` fields are nullable (title, tags, summary_detailed, key_entities, memory_snippet)
- Need graceful handling to avoid empty sections in RAG output
- Should still include conversation entry even if some fields are missing

**Decision**:

- Use NULL-safe formatting: Check if field exists before including in output
- Format tags/key_entities as empty string if NULL, or format JSONB arrays as comma-separated strings
- Always include conversation entry if at least one field (title or summary_detailed) exists
- Skip conversation entry only if both title and summary_detailed are NULL

**Rationale**:

- Maintains RAG structure even with incomplete data
- Provides maximum context when available
- Prevents empty or broken formatting

**Alternatives considered**:

- Skip conversations with missing fields: Rejected - loses valuable context
- Use default placeholder text: Rejected - misleading, better to omit field

---

### 3. Code Snippet Repository Filtering

**Question**: Should code snippets be filtered by repository_name for THN-specific repos only?

**Findings**:

- `code_index` table stores code from multiple repositories
- THN project may include code from various repos (not just THN-specific)
- Vector similarity search already filters by relevance to user query
- No clear requirement to filter by repository name

**Decision**: Do NOT filter by repository_name. Use vector similarity search with user_message to retrieve most relevant code chunks regardless of repository.

**Rationale**:

- Vector similarity search already provides relevance filtering
- THN project may legitimately reference code from multiple repositories
- Simpler implementation without repository filtering logic
- User requirement focuses on relevance, not repository boundaries

**Alternatives considered**:

- Filter by repository_name: Rejected - too restrictive, may miss relevant code
- Filter by production_targets: Considered - may add later if needed for specific use cases

---

### 4. Code Snippet Description Generation

**Question**: What should "brief_description" be for code snippets? Extract from metadata or generate from file path?

**Findings**:

- `code_index.chunk_metadata` is JSONB and may contain function_name, class_name, or other metadata
- File path can provide context (e.g., `brain_core/context_builder.py` suggests context building logic)
- No standardized description field in code_index table

**Decision**: Generate brief description from available metadata:

1. If `chunk_metadata` contains `function_name` or `class_name`, use that
2. Otherwise, derive from file path (extract meaningful part, e.g., filename or directory)
3. Fallback to "Code snippet" if nothing available

**Rationale**:

- Leverages existing metadata when available
- Provides useful context even without metadata
- Simple and maintainable approach

**Alternatives considered**:

- Always use file path: Rejected - function/class names are more descriptive
- Generate LLM description: Rejected - adds cost and latency, not necessary
- Leave description empty: Rejected - reduces context value

---

### 5. RAG Format Optimization

**Question**: How should we optimize the RAG format for cost and token efficiency?

**Findings**:

- System messages consume tokens in LLM API calls
- Long summaries and memory snippets can be expensive
- Code chunks can be lengthy
- Need balance between context and cost

**Decision**:

- Truncate `summary_detailed` to 500 characters if longer (with ellipsis)
- Truncate `memory_snippet` to 300 characters if longer (with ellipsis)
- Truncate `chunk_text` to 1000 characters if longer (with ellipsis)
- Format tags/key_entities as concise comma-separated strings (limit to 10 items)

**Rationale**:

- Maintains essential context while reducing token count
- Prevents extremely long RAG sections
- Still provides enough detail for context understanding

**Alternatives considered**:

- No truncation: Rejected - could lead to very expensive API calls
- More aggressive truncation: Rejected - loses too much context value
- Dynamic truncation based on total length: Considered - may add later if needed

---

### 6. Integration with Existing Code

**Question**: How should new RAG integrate with existing `build_project_context()` function?

**Findings**:

- Current THN RAG is in `build_project_context()` function (lines 489-562)
- Function returns `Dict[str, Any]` with `{"context": str, "notes": List[str]}`
- Function is called from `chat.py` and expects this format
- Need to replace THN-specific logic while maintaining function signature

**Decision**:

- Replace THN-specific block (lines 489-562) with new implementation
- Maintain same return format: `{"context": str, "notes": List[str]}`
- Keep error handling and fallback behavior
- Remove calls to `get_thn_code_context()` and MCP notes logic

**Rationale**:

- Maintains compatibility with existing code
- Clean replacement of THN logic
- Preserves error handling patterns

**Alternatives considered**:

- Create separate function: Rejected - adds unnecessary complexity
- Keep old code alongside new: Rejected - violates requirement to remove current implementation

---

## Summary of Decisions

1. **Conversation Retrieval**: Date-based ordering (`ORDER BY indexed_at DESC LIMIT 5`)
2. **Missing Fields**: NULL-safe formatting, include entry if title or summary exists
3. **Code Filtering**: No repository filter, use vector similarity search only
4. **Code Description**: Extract from metadata (function/class) or file path
5. **Cost Optimization**: Truncate long fields (summary: 500, memory: 300, code: 1000 chars)
6. **Integration**: Replace THN block in `build_project_context()`, maintain function signature
