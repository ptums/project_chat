# API Contract: Revamp DAAS RAG System

## Function: `build_daas_rag_context`

**Location**: `brain_core/context_builder.py`

**Purpose**: Build RAG context for DAAS project by retrieving related dreams using vector similarity search.

### Signature

```python
def build_daas_rag_context(user_message: str, top_k: int = 3) -> Dict[str, Any]:
    """
    Build RAG context for DAAS project with related dreams.

    Retrieves top-k relevant dreams from conversation_index using vector similarity
    search based on themes, symbols, or events in the user message. Formats
    dreams with clear separation and truncation to optimize token usage.

    Args:
        user_message: User query containing themes, symbols, or events to search
        top_k: Number of dreams to retrieve (default: 3, max: 5)

    Returns:
        Dict with:
        - 'context': Formatted string with related dreams (empty if none found)
        - 'notes': List of source notes (e.g., "Retrieved 3 dreams via vector similarity")

    Raises:
        None - always returns a dict (empty context if retrieval fails)
    """
```

### Behavior

1. **Input Validation**

   - If `user_message` is empty or None, return empty context
   - If `top_k` > 5, cap at 5
   - If `top_k` < 1, default to 3

2. **Embedding Generation**

   - Call `generate_embedding(user_message)` from `embedding_service.py`
   - Handle embedding generation errors gracefully

3. **Vector Similarity Search**

   - Query `conversation_index` table:
     - Filter: `project = 'DAAS'` AND `embedding IS NOT NULL`
     - Order by: `embedding <=> query_embedding` (cosine distance)
     - Limit: `top_k`
   - Return: `session_id`, `title`, `summary_short`, `memory_snippet`

4. **Formatting**

   - For each retrieved dream:
     - Title: Use full title
     - Summary: Truncate `summary_short` to 300 chars (add "..." if truncated)
     - Memory: Truncate `memory_snippet` to 200 chars (add "..." if truncated)
   - Format with markdown headers and separators
   - Add header: "### Related Dreams for Analysis"

5. **Output**
   - If dreams found: Return formatted context string
   - If no dreams found: Return empty context string
   - Always include notes about retrieval

### Example Output

```python
{
    "context": """### Related Dreams for Analysis

**Dream: Flying Over Ocean**
- **Summary**: Dreamed of flying over a vast ocean, feeling free and unburdened...
- **Key Details**: Ocean represented emotional depth, flying symbolized liberation from...

---

**Dream: Underwater City**
- **Summary**: Explored an underwater city with ancient architecture, felt peaceful...
- **Key Details**: Water represented subconscious, city symbolized structured thoughts...

---

**Dream: Desert Journey**
- **Summary**: Walked through desert, found oasis with clear water, felt relief...
- **Key Details**: Desert represented emotional dryness, oasis symbolized hope...""",

    "notes": ["Retrieved 3 dreams via vector similarity search"]
}
```

### Error Handling

- **Embedding generation fails**: Log error, return empty context
- **Database query fails**: Log error, return empty context
- **No dreams found**: Return empty context (not an error)
- **Invalid input**: Return empty context with appropriate logging

### Performance Requirements

- **Target**: <500ms total execution time
- **Breakdown**:
  - Embedding generation: <200ms
  - Database query: <200ms
  - Formatting: <100ms

### Token Limits

- **Target**: <1000 tokens for RAG context
- **Per dream**: ~250 tokens (title + summary + memory + formatting)
- **3 dreams**: ~750 tokens
- **5 dreams**: ~1250 tokens (acceptable if highly relevant)

## Integration Point: `build_project_context()`

**Location**: `brain_core/context_builder.py` (lines ~704-786)

**Changes**:

- Remove existing DAAS retrieval logic (lines 704-786)
- Add new DAAS handling:

```python
# DAAS-specific retrieval: new RAG format
if project == 'DAAS':
    try:
        return build_daas_rag_context(user_message, top_k=3)
    except Exception as e:
        logger.error(f"DAAS RAG generation failed: {e}")
        # Fall through to default behavior (keyword-based search)
```

## Dependencies

- `embedding_service.generate_embedding()`: Generate query embeddings
- `db.get_conn()`: Database connection
- `conversation_index` table: Source of dream data
- PostgreSQL pgvector extension: Vector similarity search
