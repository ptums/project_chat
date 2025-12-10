# Quickstart: Enhance THN RAG System

## Overview

This guide explains how to use and validate the new THN RAG system that provides History & Context and Relevant Code Snippets.

## Prerequisites

- PostgreSQL database with `conversation_index` and `code_index` tables
- THN project conversations indexed in `conversation_index` table
- THN code indexed in `code_index` table with embeddings
- Python 3.10+ environment

## Quick Validation

### 1. Verify Database Tables Exist

```sql
-- Check conversation_index table
SELECT table_name FROM information_schema.tables
WHERE table_name = 'conversation_index';

-- Check code_index table
SELECT table_name FROM information_schema.tables
WHERE table_name = 'code_index';
```

### 2. Verify THN Data Exists

```sql
-- Check THN conversations
SELECT COUNT(*) FROM conversation_index WHERE project = 'THN';

-- Check code chunks with embeddings
SELECT COUNT(*) FROM code_index WHERE embedding IS NOT NULL;
```

### 3. Test RAG Generation

Run a chat session with THN project:

```bash
python3 chat_cli.py
```

Then in the chat:

```
/thn
What is the current network setup?
```

The system should:

1. Generate system prompt with project overview and rules (first system message)
2. Generate RAG with History & Context section (last 5 THN conversations)
3. Generate RAG with Relevant Code Snippets section (top 5 code chunks)
4. Include RAG in system messages **after** the project_knowledge section (second system message)

### 4. Verify RAG Format

Check logs for RAG output format. The THN RAG appears as the **second system message**, after the project_knowledge section (overview + rules).

**System Message 1** (Base prompt + project overview + rules):

```
You are a helpful, accurate, and context-aware AI assistant...

In this current conversation is tagged as project THN.

Here's a general overview of the project THN: THN (Tumulty Home Network) is a privacy-first...

---

### Project THN rules:

1. Always provide responses strictly related to THN...
2. Maintain a privacy-first mindset...
...
```

**System Message 2** (THN RAG - History & Context + Relevant Code Snippets):

````
### History & Context: Last 5 Conversations

- **Title:** THN Network Setup
- **Tags:** networking, vlan, firewall
- **Key Entities:** Firewalla, Mac Mini, VLAN 10
- **Summary:** Discussion about setting up VLAN segmentation for IoT devices and server workloads. Configured Firewalla rules to isolate traffic between VLANs...
- **Memory Snippet:** User configured VLAN 10 for IoT devices, VLAN 20 for servers. Firewalla rules prevent cross-VLAN communication except for specific services.

- **Title:** THN Code Review: Context Builder
- **Tags:** code-review, python, context-builder
- **Key Entities:** context_builder.py, RAG system
- **Summary:** Reviewed the context_builder.py implementation for building project-aware context. Discussed improvements to RAG retrieval...
- **Memory Snippet:** Context builder uses vector similarity search for code retrieval. Consider caching frequently accessed code chunks.

... (3 more conversation entries)

### Relevant Code Snippets

**File:** brain_core/context_builder.py
**Language:** python
**Description:** build_project_context
```python
def build_project_context(
    project: str,
    user_message: str,
    limit_memories: int = 200,
    top_n: int = 5,
) -> Dict[str, Any]:
    # Build project-aware context...
````

**File:** brain_core/thn_code_retrieval.py
**Language:** python
**Description:** retrieve_thn_code

```python
def retrieve_thn_code(
    query: str,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    # Vector similarity search...
```

... (3 more code snippets)

````

**Note**: The wrapper text around the RAG content (currently "We're working on project THN together...") should be updated in `chat.py` to be more concise. The RAG sections are self-explanatory and don't need verbose introduction.

## Implementation Steps

### Step 1: Backup Current Code

```bash
# Create backup branch
git checkout -b backup-thn-rag-before-refactor
git add brain_core/context_builder.py
git commit -m "Backup: THN RAG before refactor"
````

### Step 2: Implement New RAG Functions

1. Add `build_thn_rag_context()` function to `context_builder.py`
2. Add helper functions: `_format_conversation_entry()`, `_format_code_snippet()`, etc.
3. Replace THN block in `build_project_context()` with call to new function

### Step 3: Test Implementation

```bash
# Run chat CLI and test THN project
python3 chat_cli.py
/thn
Test message
```

Verify:

- RAG is generated correctly
- Format matches specification
- Performance is acceptable (<500ms)

### Step 4: Verify Integration

Check that RAG appears in system messages **after** project_knowledge section:

```python
# In chat.py, verify message order:
# 1. System message: base prompt + project overview + rules (from build_project_system_prompt)
# 2. System message: THN RAG (from build_project_context)
# 3. System message: Note reads (if any)
# 4. User/Assistant messages: Conversation history

# Check logs for RAG content in second system message
# Verify RAG appears after project_knowledge section
```

## Troubleshooting

### Issue: No conversations in RAG

**Solution**: Ensure THN conversations are indexed:

```bash
python3 scripts/reindex_conversations.py --project THN
```

### Issue: No code snippets in RAG

**Solution**: Ensure code is indexed with embeddings:

```bash
python3 scripts/index_thn_code.py
```

### Issue: RAG generation is slow (>500ms)

**Solution**:

- Check database indexes exist
- Verify vector similarity index is created
- Check query performance with EXPLAIN ANALYZE

### Issue: RAG format is incorrect

**Solution**:

- Check `_format_conversation_entry()` and `_format_code_snippet()` functions
- Verify NULL field handling
- Check truncation logic

## Performance Benchmarks

Expected performance:

- Conversation query: <50ms
- Code similarity search: <200ms
- Formatting: <50ms
- Total RAG generation: <500ms

## Rollback Plan

If issues occur, rollback to previous implementation:

```bash
git checkout backup-thn-rag-before-refactor
# Restore previous context_builder.py
```

## Next Steps

After implementation:

1. Monitor RAG generation performance
2. Collect user feedback on RAG quality
3. Optimize truncation limits if needed
4. Consider adding more fields to RAG if valuable
