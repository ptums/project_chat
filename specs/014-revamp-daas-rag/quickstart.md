# Quickstart: Revamp DAAS RAG System

**Feature**: `014-revamp-daas-rag`  
**Date**: 2025-01-27

## Overview

This feature revamps the DAAS RAG system to provide focused, cost-effective dream analysis retrieval without confusing conversation history.

## What Changes

### For Users

- **No visible changes** to CLI interface
- RAG retrieval happens automatically for DAAS project conversations
- **Removed**: "Thinking for DAAS" spinner messages (cleaner interface)
- **Improved**: More focused dream retrieval by themes/symbols/events

### For Developers

1. **File Deletions**:

   - `brain_core/daas_retrieval.py` - Entire file removed

2. **File Modifications**:

   - `brain_core/context_builder.py`:
     - Remove old DAAS retrieval code (lines 704-786)
     - Add new `build_daas_rag_context()` function
   - `chat_cli.py`:
     - Remove "Thinking for [PROJECT]" spinner (3 locations)

3. **New Function**:
   - `build_daas_rag_context(user_message: str, top_k: int = 3) -> Dict[str, Any]`

## Implementation Steps

### Step 1: Remove Old DAAS RAG Code

```bash
# Delete the old retrieval file
rm brain_core/daas_retrieval.py
```

### Step 2: Remove Old Code from context_builder.py

Remove lines 704-786 in `brain_core/context_builder.py` (the entire DAAS-specific retrieval block).

### Step 3: Implement New DAAS RAG Function

Add `build_daas_rag_context()` function to `brain_core/context_builder.py`:

```python
def build_daas_rag_context(user_message: str, top_k: int = 3) -> Dict[str, Any]:
    """
    Build RAG context for DAAS project with related dreams.

    Retrieves top-k relevant dreams using vector similarity search.
    """
    if not user_message or not user_message.strip():
        return {"context": "", "notes": []}

    # Cap top_k at 5
    top_k = min(top_k, 5) if top_k > 0 else 3

    try:
        # Generate embedding for user message
        query_embedding = generate_embedding(user_message)
        embedding_str = '[' + ','.join(str(x) for x in query_embedding) + ']'

        # Vector similarity search
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT session_id, title, summary_short, memory_snippet
                    FROM conversation_index
                    WHERE project = 'DAAS'
                      AND embedding IS NOT NULL
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                    """,
                    (embedding_str, top_k),
                )
                rows = cur.fetchall()

        if not rows:
            return {"context": "", "notes": []}

        # Format dreams with truncation
        dream_parts = ["### Related Dreams for Analysis\n"]
        for row in rows:
            session_id, title, summary_short, memory_snippet = row

            dream_parts.append(f"**Dream: {title or 'Untitled'}**")

            if summary_short:
                summary = summary_short[:300] + ("..." if len(summary_short) > 300 else "")
                dream_parts.append(f"- **Summary**: {summary}")

            if memory_snippet:
                memory = memory_snippet[:200] + ("..." if len(memory_snippet) > 200 else "")
                dream_parts.append(f"- **Key Details**: {memory}")

            dream_parts.append("")  # Empty line
            dream_parts.append("---")  # Separator
            dream_parts.append("")  # Empty line

        # Remove last separator
        if dream_parts[-1] == "" and dream_parts[-2] == "---":
            dream_parts = dream_parts[:-2]

        context = "\n".join(dream_parts)

        return {
            "context": context,
            "notes": [f"Retrieved {len(rows)} dreams via vector similarity search"]
        }

    except Exception as e:
        logger.error(f"Error building DAAS RAG context: {e}")
        return {"context": "", "notes": []}
```

### Step 4: Integrate New Function

In `build_project_context()`, replace old DAAS code with:

```python
# DAAS-specific retrieval: new RAG format
if project == 'DAAS':
    try:
        return build_daas_rag_context(user_message, top_k=3)
    except Exception as e:
        logger.error(f"DAAS RAG generation failed: {e}")
        # Fall through to default behavior
```

### Step 5: Remove Thinking Spinner

In `chat_cli.py`, remove or comment out:

- Line ~1356: `thinking_label = f"{style['emoji']} Thinking for {style['label']}"`
- Line ~1502: Same
- Line ~1625: Same
- Remove spinner thread creation and start calls
- Remove `stop_event.set()` calls

## Testing

### Manual Testing Steps

1. **Start a new DAAS conversation**:

   ```bash
   python chat_cli.py
   # Select DAAS project
   ```

2. **Send a query about themes/symbols**:

   ```
   What dreams have I had about water?
   ```

3. **Verify**:

   - No "Thinking for DAAS" spinner appears
   - Response includes related dreams (if any exist in database)
   - Dreams are clearly separated
   - Content is truncated appropriately

4. **Check logs**:
   - Look for "Retrieved X dreams via vector similarity search"
   - No errors in RAG generation

### Verification Checklist

- [ ] `daas_retrieval.py` file deleted
- [ ] Old DAAS code removed from `context_builder.py`
- [ ] New `build_daas_rag_context()` function implemented
- [ ] Function integrated into `build_project_context()`
- [ ] "Thinking" spinner removed from `chat_cli.py`
- [ ] RAG retrieves relevant dreams
- [ ] Dreams formatted with clear separation
- [ ] Content truncated appropriately
- [ ] No conversation history in RAG
- [ ] Performance <500ms

## Rollback Plan

If issues arise:

1. **Restore old code**:

   - Restore `daas_retrieval.py` from git history
   - Restore old DAAS code in `context_builder.py`
   - Restore spinner in `chat_cli.py`

2. **Git commands**:
   ```bash
   git checkout HEAD -- brain_core/daas_retrieval.py
   git checkout HEAD -- brain_core/context_builder.py
   git checkout HEAD -- chat_cli.py
   ```

## Performance Monitoring

Monitor these metrics:

- RAG generation time (should be <500ms)
- Token usage (should be <1000 tokens)
- Number of dreams retrieved (should be 3-5)
- User satisfaction with dream relevance

## Next Steps

After implementation:

1. Test with various DAAS queries
2. Monitor token usage and adjust truncation if needed
3. Gather user feedback on dream relevance
4. Consider fine-tuning `top_k` parameter based on results
