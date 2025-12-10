# Feature Specification: Enhance THN RAG System

**Feature ID**: `013-enhance-thn-rag`  
**Date**: 2025-01-27  
**Status**: Planning

## Overview

Replace the current RAG implementation for THN project with a new, improved RAG system that provides:

1. **History & Context**: Last 5 conversations from `conversation_index` table
2. **Relevant Code Snippets**: Code chunks from `thn_code_index` table (via `code_index` table)

The goal is to give project THN a general overview of conversations from a personal level, maintaining contextual knowledge to anticipate where conversations should be going. Code snippets aid in code review and analysis tasks.

## Requirements

### Functional Requirements

1. **Remove Current THN RAG Implementation**

   - Remove existing THN-specific RAG code in `build_project_context()` function
   - Remove or deprecate `get_thn_code_context()` usage in context builder
   - Clean up any THN-specific retrieval logic that doesn't match new format

2. **Implement New RAG Format**

   **History & Context Section:**

   - Query `conversation_index` table for THN project
   - Retrieve last 5 conversations (ordered by `indexed_at DESC`)
   - Format each entry with:
     - Title (`title`)
     - Tags (`tags` - JSONB array)
     - Key Entities (`key_entities` - JSONB array)
     - Summary (`summary_detailed`)
     - Memory Snippet (`memory_snippet`)

   **Relevant Code Snippets Section:**

   - Query `code_index` table (THN code)
   - Retrieve top 5 relevant code chunks using vector similarity search
   - Format each entry with:
     - File path (`file_path`)
     - Language (`language`)
     - Brief description (extracted from metadata or file path)
     - Code chunk text (`chunk_text`)

3. **RAG Format Template**

   ````
   ### History & Context: Last 5 Conversations

   - **Title:** {title_1}
   - **Tags:** {tags_1}
   - **Key Entities:** {key_entities_1}
   - **Summary:** {summary_detailed_1}
   - **Memory Snippet:** {memory_snippet_1}

   ... (4 more conversation entries)

   ### Relevant Code Snippets

   {# Example Code Snippet #}
   **File:** {file_path_1}
   **Language:** {language_1}
   **Description:** {brief_description_1}
   ```{language_1}
   {chunk_text_1}
   ````

   ... (4 more code snippets)

   ```

   ```

4. **Integration Points**
   - New RAG should be generated in `build_project_context()` for THN project only
   - Output format should match existing context dict structure: `{"context": str, "notes": List[str]}`
   - RAG should be included in system messages in `chat.py` **after** the project_knowledge section (which contains overview and rules)
   - Message order: System prompt (base + project extension with overview/rules) → THN RAG → Note reads → Conversation history

### Non-Functional Requirements

1. **Performance**

   - RAG generation should complete in <500ms
   - Use efficient database queries with proper indexes
   - Cache conversation queries when possible

2. **Cost Optimization**

   - Limit conversation history to 5 entries
   - Limit code snippets to 5 entries
   - Consider truncating long summaries/memory snippets if needed
   - Use vector similarity search efficiently (top_k=5)

3. **Maintainability**
   - Code should be modular and testable
   - Clear separation between conversation retrieval and code retrieval
   - Proper error handling and fallback behavior

## Technical Context

### Current Implementation

- **Location**: `brain_core/context_builder.py` - `build_project_context()` function (lines 489-562)
- **Current THN RAG**: Uses `get_thn_code_context()` from `thn_code_retrieval.py`
- **Database Tables**:
  - `conversation_index`: Stores conversation summaries, tags, entities, memory snippets
  - `code_index`: Stores code chunks with embeddings (THN code)

### Database Schema

**conversation_index table:**

- `session_id` (UUID, PK)
- `project` (TEXT) - filter by 'THN'
- `title` (TEXT)
- `tags` (JSONB)
- `summary_detailed` (TEXT)
- `key_entities` (JSONB)
- `memory_snippet` (TEXT)
- `indexed_at` (TIMESTAMPTZ) - for ordering

**code_index table:**

- `id` (UUID, PK)
- `repository_name` (TEXT)
- `file_path` (TEXT)
- `language` (TEXT)
- `chunk_text` (TEXT)
- `chunk_metadata` (JSONB)
- `embedding` (vector(1536))
- `production_targets` (TEXT[])

### Integration Points

- `brain_core/chat.py`: Uses `build_project_context()` output in system messages
- `brain_core/thn_code_retrieval.py`: Existing code retrieval functions (may need modification)
- `brain_core/db.py`: Database connection utilities

## Success Criteria

1. ✅ Current THN RAG implementation removed
2. ✅ New RAG format implemented with History & Context section (5 conversations)
3. ✅ New RAG format implemented with Relevant Code Snippets section (5 code chunks)
4. ✅ RAG integrates correctly into chat system messages
5. ✅ Performance meets <500ms requirement
6. ✅ Code is maintainable and follows project patterns

## Open Questions

1. Should we use vector similarity search for conversation retrieval, or simple date-based ordering?
2. How should we handle missing fields (e.g., if `summary_detailed` is NULL)?
3. Should code snippets be filtered by repository_name for THN-specific repos only?
4. What should "brief_description" be for code snippets? Extract from metadata or generate from file path?
