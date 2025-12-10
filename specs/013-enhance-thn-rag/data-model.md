# Data Model: Enhance THN RAG System

## Overview

This feature modifies the RAG (Retrieval Augmented Generation) system for THN project. No database schema changes are required - we use existing tables (`conversation_index` and `code_index`).

## Existing Tables Used

### 1. conversation_index

**Purpose**: Stores conversation summaries and metadata for all projects.

**Relevant Columns for THN RAG**:
| Column | Type | Usage |
|--------|------|-------|
| `session_id` | UUID | Primary key (not used in RAG output) |
| `project` | TEXT | Filter: `WHERE project = 'THN'` |
| `title` | TEXT | Displayed in RAG as "**Title:** {title}" |
| `tags` | JSONB | Displayed as comma-separated list |
| `key_entities` | JSONB | Displayed as comma-separated list |
| `summary_detailed` | TEXT | Displayed in RAG (truncated to 500 chars if needed) |
| `memory_snippet` | TEXT | Displayed in RAG (truncated to 300 chars if needed) |
| `indexed_at` | TIMESTAMPTZ | Used for ordering: `ORDER BY indexed_at DESC` |

**Query Pattern**:

```sql
SELECT title, tags, key_entities, summary_detailed, memory_snippet
FROM conversation_index
WHERE project = 'THN'
ORDER BY indexed_at DESC
LIMIT 5
```

### 2. code_index

**Purpose**: Stores code chunks with embeddings for semantic search.

**Relevant Columns for THN RAG**:
| Column | Type | Usage |
|--------|------|-------|
| `id` | UUID | Primary key (not used in RAG output) |
| `file_path` | TEXT | Displayed as "**File:** {file_path}" |
| `language` | TEXT | Displayed as "**Language:** {language}" |
| `chunk_text` | TEXT | Displayed in code block (truncated to 1000 chars if needed) |
| `chunk_metadata` | JSONB | Used to extract function_name/class_name for description |
| `embedding` | vector(1536) | Used for vector similarity search |

**Query Pattern**:

```sql
SELECT file_path, language, chunk_text, chunk_metadata
FROM code_index
WHERE embedding IS NOT NULL
ORDER BY embedding <=> %s::vector
LIMIT 5
```

## Data Flow

1. **User sends message** → `chat_turn()` in `chat.py`
2. **Build system prompt** → `build_project_system_prompt(project='THN')` includes base prompt + project overview + rules
3. **Build context** → `build_project_context(project='THN', user_message)` in `context_builder.py`
4. **Query conversations** → SELECT from `conversation_index` WHERE project='THN' ORDER BY indexed_at DESC LIMIT 5
5. **Query code** → Vector similarity search on `code_index` using user_message embedding
6. **Format RAG** → Combine into formatted string with History & Context and Relevant Code Snippets sections
7. **Return context** → `{"context": str, "notes": List[str]}`
8. **Inject into messages** → Added as system message in `chat.py` **after** the system prompt (which contains overview/rules)

**Message Order**:

- System message 1: Base prompt + project overview + project rules (from `build_project_system_prompt()`)
- System message 2: THN RAG (History & Context + Relevant Code Snippets) (from `build_project_context()`)
- System message 3: Note reads (if any)
- User/Assistant messages: Conversation history

## Data Transformations

### Conversation Entry Formatting

**Input**: Row from `conversation_index`

```python
{
    'title': 'THN Network Setup',
    'tags': ['networking', 'vlan', 'firewall'],
    'key_entities': ['Firewalla', 'Mac Mini'],
    'summary_detailed': 'Long summary text...',
    'memory_snippet': 'Memory text...'
}
```

**Output**: Formatted string

```
- **Title:** THN Network Setup
- **Tags:** networking, vlan, firewall
- **Key Entities:** Firewalla, Mac Mini
- **Summary:** Long summary text... (truncated if >500 chars)
- **Memory Snippet:** Memory text... (truncated if >300 chars)
```

### Code Snippet Formatting

**Input**: Row from `code_index`

```python
{
    'file_path': 'brain_core/context_builder.py',
    'language': 'python',
    'chunk_text': 'def build_project_context(...):\n    ...',
    'chunk_metadata': {'function_name': 'build_project_context'}
}
```

**Output**: Formatted string

````
**File:** brain_core/context_builder.py
**Language:** python
**Description:** build_project_context
```python
def build_project_context(...):
    ...
````

```

## Constraints and Validation

1. **Conversation Retrieval**:
   - Must filter by `project = 'THN'`
   - Must order by `indexed_at DESC`
   - Must limit to 5 entries
   - Handle NULL fields gracefully

2. **Code Retrieval**:
   - Must use vector similarity search
   - Must limit to 5 entries
   - Must filter `WHERE embedding IS NOT NULL`
   - Handle missing metadata gracefully

3. **Formatting**:
   - Truncate `summary_detailed` to 500 characters
   - Truncate `memory_snippet` to 300 characters
   - Truncate `chunk_text` to 1000 characters
   - Format JSONB arrays as comma-separated strings

## Error Handling

- If no conversations found: Return empty History & Context section or omit section
- If no code found: Return empty Relevant Code Snippets section or omit section
- If database error: Log error and return empty context dict
- If embedding generation fails: Skip code retrieval, return conversation-only RAG
```
