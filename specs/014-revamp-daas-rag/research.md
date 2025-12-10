# Research: Revamp DAAS RAG System

**Feature**: `014-revamp-daas-rag`  
**Date**: 2025-01-27

## Research Decisions

### 1. Vector Similarity Search Strategy

**Question**: How should we extract themes/symbols/events from user query for vector search?

**Decision**: Use the full user message for embedding generation, similar to THN code search implementation.

**Rationale**:

- Simpler implementation - no need to parse or extract specific themes/symbols
- Leverages existing embedding infrastructure (`embedding_service.py`)
- User's natural language query already contains relevant themes/symbols/events
- Consistent with THN RAG approach (uses full user message)

**Alternatives Considered**:

- Parse query for specific keywords (themes, symbols, events) - **Rejected**: Too complex, may miss context
- Use separate embeddings for title, summary, memory - **Rejected**: More complex, not needed for initial implementation
- Hybrid approach (keywords + full query) - **Rejected**: Over-engineering for current needs

**Implementation**: Use `generate_embedding(user_message)` from `embedding_service.py`, then query `conversation_index` with vector similarity search.

---

### 2. Dream Formatting and Separation

**Question**: What's the best format for presenting multiple dreams with clear boundaries?

**Decision**: Use markdown-style formatting with clear headers and horizontal separators between dreams.

**Format**:

```
### Related Dreams for Analysis

**Dream: [Title]**
- **Themes**: [extracted or from summary]
- **Summary**: [truncated to 300 chars]
- **Key Details**: [memory_snippet truncated to 200 chars]

---

**Dream: [Title]**
...
```

**Rationale**:

- Clear visual separation between dreams
- Maintains readability
- Easy to parse and understand
- Consistent with existing project formatting patterns

**Alternatives Considered**:

- Numbered list format - **Rejected**: Less clear separation
- Single paragraph with separators only - **Rejected**: Harder to scan
- JSON-like structure - **Rejected**: Too verbose, not human-readable

---

### 3. Token Optimization Strategies

**Question**: How to limit retrieved content while maintaining usefulness?

**Decision**:

- Truncate `summary_short` to 300 characters
- Truncate `memory_snippet` to 200 characters
- Limit to 3-5 dreams per query (configurable, default: 3)
- Only include essential fields: title, summary, memory_snippet

**Rationale**:

- 300 chars for summary provides enough context without excessive tokens
- 200 chars for memory snippet captures key details
- 3-5 dreams balances relevance with token usage
- Essential fields only keeps focus on what matters for analysis

**Token Estimation**:

- Per dream: ~50 (title) + ~100 (summary) + ~70 (memory) + ~30 (formatting) = ~250 tokens
- 3 dreams: ~750 tokens
- 5 dreams: ~1250 tokens (slightly over target, but acceptable)
- Formatting overhead: ~100 tokens
- **Total**: ~850-1350 tokens (within reasonable range)

**Alternatives Considered**:

- No truncation - **Rejected**: Could easily exceed 2000+ tokens
- More aggressive truncation (150/100) - **Rejected**: Loses important context
- Only title + summary - **Rejected**: Memory snippets provide valuable symbolic details

---

### 4. Removing Debugging Messages

**Question**: Where is the "Thinking for [PROJECT]" spinner implemented and how to remove it?

**Decision**: Remove spinner thread and thinking label from `chat_cli.py` in three locations (lines ~1356, ~1502, ~1625).

**Rationale**:

- Improves user experience by removing visual noise
- RAG generation is fast enough (<500ms) that spinner is unnecessary
- Cleaner interface without debugging messages

**Implementation**:

- Remove `thinking_label` variable assignment
- Remove `spinner_thread` creation and start
- Remove `stop_event.set()` call
- Keep the actual RAG generation logic (it happens in background)

**Alternatives Considered**:

- Keep spinner but make it optional via flag - **Rejected**: User explicitly requested removal
- Replace with simpler loading indicator - **Rejected**: User wants no debugging messages
- Log to file instead - **Rejected**: Not what user requested

---

### 5. Integration with Existing System

**Question**: How should new DAAS RAG integrate with `build_project_context()`?

**Decision**: Follow the same pattern as THN RAG:

- Check if `project == 'DAAS'`
- Call `build_daas_rag_context(user_message)`
- Return formatted context dict
- Handle errors gracefully with fallback

**Rationale**:

- Consistent with existing code patterns
- Easy to maintain and understand
- Clear separation of concerns
- Follows established project conventions

**Code Structure**:

```python
if project == 'DAAS':
    try:
        return build_daas_rag_context(user_message)
    except Exception as e:
        logger.error(f"DAAS RAG generation failed: {e}")
        # Fall through to default behavior
```

---

## Technical Decisions Summary

| Decision            | Choice                              | Rationale                                 |
| ------------------- | ----------------------------------- | ----------------------------------------- |
| Vector Search Input | Full user message                   | Simple, leverages existing infrastructure |
| Dream Format        | Markdown with separators            | Clear, readable, consistent               |
| Token Limits        | 300/200 char truncation, 3-5 dreams | Balances context with efficiency          |
| Debug Messages      | Remove completely                   | User request, cleaner UX                  |
| Integration Pattern | Follow THN RAG pattern              | Consistency, maintainability              |

## Open Questions Resolved

✅ All technical questions resolved. No remaining clarifications needed.
