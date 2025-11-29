# Data Model: DAAS Semantic Dream Retrieval and Streaming Responses

## 1. conversation_index (MODIFIED)

### New Column: embedding

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| embedding | vector(1536) | NULL allowed | Vector embedding for DAAS project entries only. Generated via OpenAI `text-embedding-3-small` model. Used for semantic similarity search. |

### Existing Columns (unchanged)
- session_id (UUID, PK)
- project (TEXT, NOT NULL)
- title (TEXT, NULL)
- tags (JSONB, NULL)
- summary_short (TEXT, NULL)
- summary_detailed (TEXT, NULL)
- key_entities (JSONB, NULL)
- key_topics (JSONB, NULL)
- memory_snippet (TEXT, NULL)
- ollama_model (TEXT, NOT NULL)
- version (INTEGER, NOT NULL)
- indexed_at (TIMESTAMPTZ, NOT NULL)

### Indexes

**New Index**: Vector similarity search index
```sql
CREATE INDEX idx_conversation_index_embedding 
ON conversation_index 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100)
WHERE project = 'DAAS' AND embedding IS NOT NULL;
```

**Rationale**: 
- IVFFlat index provides fast approximate nearest neighbor search
- Partial index (WHERE clause) only indexes DAAS entries with embeddings
- Cosine similarity operator (`<=>`) for semantic search
- `lists = 100` balances speed vs accuracy for expected dataset size

## 2. Embedding Generation Workflow

### Input Data
- Source: `conversation_index` rows where `project = 'DAAS'`
- Text to embed: Combination of `title`, `summary_detailed`, `key_topics`, and `memory_snippet`
- Format: Concatenated text string for embedding generation

### Embedding Storage
- Stored in `conversation_index.embedding` column
- Generated during indexing phase (when `index_session()` is called)
- Backfilled for existing DAAS entries via `backfill_embeddings.py` script

### Validation Rules
- Embedding is NULL for non-DAAS projects (enforced by application logic)
- Embedding is NULL for DAAS entries that haven't been indexed yet
- Embedding dimension must be 1536 (enforced by column type `vector(1536)`)

## 3. Retrieval Modes

### Single-Dream Mode (Quoted Title)
- **Trigger**: User message contains quoted title pattern `"Title"`
- **Query**: Match `conversation_index.title` using pattern matching (ILIKE)
- **Filter**: `project = 'DAAS'` AND `title ILIKE %extracted_title%`
- **Result**: Single conversation entry (most recent if multiple matches)
- **Embedding**: Not used in this mode

### Pattern-Based Mode (Vector Search)
- **Trigger**: User message does NOT contain quoted title
- **Query**: 
  1. Generate embedding for user message
  2. Vector similarity search: `ORDER BY embedding <=> query_embedding LIMIT k`
  3. Filter: `project = 'DAAS' AND embedding IS NOT NULL`
- **Result**: Top-k most semantically similar conversation entries
- **Embedding**: Required for this mode

## 4. Derived Structures

### Query Embedding
- **Source**: User message text
- **Model**: OpenAI `text-embedding-3-small`
- **Dimension**: 1536
- **Usage**: Compared against stored embeddings using cosine similarity

### Retrieval Result
- **Structure**: List of conversation entries with similarity scores
- **Fields**: session_id, title, summary_short, memory_snippet, similarity_score
- **Ordering**: By similarity score (descending)
- **Limit**: Top-k (default 5, configurable)

## 5. Relationships

- `conversation_index.embedding` is self-contained (no foreign keys)
- Vector similarity search operates within `conversation_index` table only
- Embeddings reference the same `session_id` as other conversation_index columns
- No cascading deletes needed (embedding is part of conversation_index row)

## 6. Migration Considerations

### Schema Migration
1. Install pgvector extension: `CREATE EXTENSION IF NOT EXISTS vector;`
2. Add embedding column: `ALTER TABLE conversation_index ADD COLUMN embedding vector(1536);`
3. Create index: (see Indexes section above)

### Data Migration
1. Backfill script processes existing DAAS entries
2. Generates embeddings for entries missing them
3. Updates `conversation_index.embedding` column
4. Safe to re-run (skips entries with existing embeddings)

### Rollback Plan
- Remove index: `DROP INDEX IF EXISTS idx_conversation_index_embedding;`
- Remove column: `ALTER TABLE conversation_index DROP COLUMN embedding;`
- No data loss (embedding is additive, not replacing existing data)

