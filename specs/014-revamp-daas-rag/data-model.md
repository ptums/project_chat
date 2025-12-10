# Data Model: Revamp DAAS RAG System

## Overview

No new database schema changes required. This feature uses existing tables and indexes.

## Existing Tables Used

### `conversation_index`

**Purpose**: Stores indexed conversation data including DAAS dreams with embeddings.

**Fields Used**:

- `session_id` (UUID): Unique identifier for the conversation/dream
- `title` (TEXT): Dream title
- `summary_short` (TEXT): Brief summary of the dream
- `memory_snippet` (TEXT): Key memorable details from the dream
- `embedding` (vector): Vector embedding for similarity search
- `project` (TEXT): Project tag (filtered to 'DAAS')

**Indexes Used**:

- Existing vector index on `embedding` column (pgvector)
- Existing index on `project` column

**Query Pattern**:

```sql
SELECT session_id, title, summary_short, memory_snippet
FROM conversation_index
WHERE project = 'DAAS'
  AND embedding IS NOT NULL
ORDER BY embedding <=> %s::vector
LIMIT 3
```

## Data Transformations

### Input: User Message

- Raw text query from user
- Contains themes, symbols, or events they want to explore

### Processing: Embedding Generation

- User message → `generate_embedding(user_message)` → Vector embedding
- Uses existing `embedding_service.py` infrastructure

### Processing: Vector Similarity Search

- Query embedding compared against stored dream embeddings
- Cosine distance (`<=>`) used for similarity
- Top 3-5 most similar dreams retrieved

### Output: Formatted RAG Context

- Each dream formatted with:
  - Title (full)
  - Summary (truncated to 300 chars)
  - Memory snippet (truncated to 200 chars)
- Dreams separated with clear markdown formatting
- Total context: ~850-1350 tokens

## Data Flow

```
User Message
    ↓
Generate Embedding (embedding_service.py)
    ↓
Vector Similarity Search (conversation_index table)
    ↓
Retrieve Top 3-5 Dreams
    ↓
Format with Truncation
    ↓
Return RAG Context Dict
    ↓
Inject into System Prompt
```

## Constraints

1. **No Conversation History**: Only dream data from `conversation_index`, no conversation messages
2. **DAAS-Only**: Strictly filtered by `project = 'DAAS'`
3. **Token Limits**: Content truncated to stay under 1000 token target
4. **Performance**: Query must complete in <500ms

## Validation Rules

- User message must not be empty
- At least one dream with embedding must exist in database
- Retrieved dreams must have non-null embedding
- Truncation preserves meaning (no mid-word cuts)
