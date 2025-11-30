# Quickstart: THN Code RAG Pipeline Implementation

**Feature**: 008-thn-code-rag-pipeline  
**Date**: 2025-01-27

## Prerequisites

1. **PostgreSQL with pgvector extension** (already installed for DAAS)
   ```bash
   # Verify pgvector is installed
   psql -d project_chat -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
   ```

2. **Python dependencies**
   ```bash
   pip install gitpython psycopg2-binary openai python-dotenv
   # Note: pgvector, openai already installed for DAAS
   ```

3. **OpenAI API key** (already configured for DAAS)
   - Verify in `.env`: `OPENAI_API_KEY=sk-...`

4. **Git access to THN repositories**
   - SSH keys configured for GitLab access
   - Or HTTPS with credentials

## Implementation Steps

### Step 1: Database Schema Migration

```sql
-- Create code_index table
CREATE TABLE IF NOT EXISTS code_index (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    language TEXT NOT NULL,
    chunk_text TEXT NOT NULL,
    chunk_metadata JSONB,
    embedding vector(1536),
    production_targets TEXT[],
    indexed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_updated TIMESTAMPTZ
);

-- Create indexes
CREATE INDEX idx_code_index_embedding 
ON code_index 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100)
WHERE embedding IS NOT NULL;

CREATE INDEX idx_code_index_repo_lang 
ON code_index (repository_name, language);

CREATE INDEX idx_code_index_file_path 
ON code_index (file_path);

CREATE INDEX idx_code_index_production_targets 
ON code_index USING GIN (production_targets);
```

### Step 2: Create Repository Directory

```bash
mkdir -p repos
mkdir -p repos/.metadata
```

### Step 3: Clone THN Repositories

```bash
# Example: Clone a THN repository
python3 -c "
from brain_core.thn_code_indexer import clone_repository
path = clone_repository(
    'git@gitlab.local:user/thn-automation.git',
    'thn-automation'
)
print(f'Cloned to: {path}')
"
```

Or manually:
```bash
cd repos
git clone git@gitlab.local:user/thn-automation.git
git clone git@gitlab.local:user/thn-monitoring.git
# ... clone other THN repositories
```

### Step 4: Index Repository Code

```bash
# Index a single repository
python3 scripts/index_thn_code.py \
    --repository repos/thn-automation \
    --name thn-automation \
    --production-targets tumultymedia,tumultymedia2

# Index all repositories in repos/
python3 scripts/index_thn_code.py --all
```

### Step 5: Verify Indexing

```sql
-- Check indexed code chunks
SELECT repository_name, language, COUNT(*) as chunk_count
FROM code_index
GROUP BY repository_name, language
ORDER BY repository_name, language;

-- Check embeddings generated
SELECT 
    repository_name,
    COUNT(*) as total_chunks,
    COUNT(embedding) as chunks_with_embeddings
FROM code_index
GROUP BY repository_name;
```

### Step 6: Test Code Retrieval

```python
# Test retrieval in Python
from brain_core.thn_code_retrieval import retrieve_thn_code

results = retrieve_thn_code(
    "How do I configure the router?",
    top_k=5
)

for result in results:
    print(f"File: {result['file_path']}")
    print(f"Similarity: {result['similarity']:.2f}")
    print(f"Code: {result['chunk_text'][:100]}...")
    print("---")
```

### Step 7: Test in Chat CLI

```bash
# Start chat CLI
python3 chat_cli.py

# Switch to THN project
/thn

# Ask a question that should retrieve code
How does the network setup script work?

# Verify code context is included in response
```

## Testing Scenarios

### Scenario 1: Basic Code Retrieval

**Goal**: Verify code retrieval works for THN queries

1. **Index a repository**:
   ```bash
   python3 scripts/index_thn_code.py \
       --repository repos/thn-automation \
       --name thn-automation
   ```

2. **Start chat CLI**:
   ```bash
   python3 chat_cli.py
   ```

3. **Switch to THN**:
   ```
   /thn
   ```

4. **Ask code-related question**:
   ```
   How do I configure the router in the automation script?
   ```

5. **Verify**:
   - Response includes relevant code snippets
   - Code snippets are from thn-automation repository
   - Response is contextually relevant

**Expected Outcome**: THN retrieves and includes relevant code in response

---

### Scenario 2: Production Environment Filtering

**Goal**: Verify code filtering by production machine

1. **Index repository with production targets**:
   ```bash
   python3 scripts/index_thn_code.py \
       --repository repos/thn-automation \
       --name thn-automation \
       --production-targets tumultymedia
   ```

2. **Start chat and ask about specific machine**:
   ```
   /thn
   What code runs on tumultymedia?
   ```

3. **Verify**:
   - Only code with `production_targets` containing "tumultymedia" is retrieved
   - Response mentions the specific machine context

**Expected Outcome**: Code retrieval is filtered by production target

---

### Scenario 3: File-Specific Retrieval

**Goal**: Verify retrieval of specific files

1. **Index repository**:
   ```bash
   python3 scripts/index_thn_code.py \
       --repository repos/thn-automation \
       --name thn-automation
   ```

2. **Ask about specific file**:
   ```
   /thn
   Show me the code in network_setup.py
   ```

3. **Verify**:
   - All chunks from network_setup.py are retrieved
   - Response includes complete file context

**Expected Outcome**: File-specific retrieval returns all chunks from that file

---

### Scenario 4: Incremental Indexing

**Goal**: Verify incremental updates work correctly

1. **Initial indexing**:
   ```bash
   python3 scripts/index_thn_code.py \
       --repository repos/thn-automation \
       --name thn-automation
   ```

2. **Make changes to repository**:
   ```bash
   cd repos/thn-automation
   # Edit a file or add new file
   git add .
   git commit -m "Test change"
   ```

3. **Re-index**:
   ```bash
   python3 scripts/index_thn_code.py \
       --repository repos/thn-automation \
       --name thn-automation \
       --incremental
   ```

4. **Verify**:
   - Only changed/new files are processed
   - Existing embeddings are not regenerated
   - New chunks are added to database

**Expected Outcome**: Incremental indexing only processes changed files

---

### Scenario 5: Teaching and Learning Support

**Goal**: Verify THN can explain code and propose learning projects

1. **Index repository with code**:
   ```bash
   python3 scripts/index_thn_code.py \
       --repository repos/thn-automation \
       --name thn-automation
   ```

2. **Ask for explanation**:
   ```
   /thn
   Explain how the router configuration function works
   ```

3. **Ask for learning project**:
   ```
   /thn
   What project would help me understand network automation better?
   ```

4. **Verify**:
   - Explanation uses actual code from repository
   - Learning project is based on codebase patterns
   - Response is educational and practical

**Expected Outcome**: THN provides teaching support using code context

---

### Scenario 6: Cross-Project Restriction

**Goal**: Verify THN restricts to THN codebase by default

1. **Index THN repository**:
   ```bash
   python3 scripts/index_thn_code.py \
       --repository repos/thn-automation \
       --name thn-automation
   ```

2. **Ask question in THN context**:
   ```
   /thn
   How does the network setup work?
   ```

3. **Verify**:
   - Only THN code is retrieved
   - No code from other projects (DAAS, FF, etc.) is included
   - Response focuses on THN codebase

**Expected Outcome**: THN code retrieval is restricted to THN repositories

---

### Scenario 7: Error Handling

**Goal**: Verify graceful error handling

1. **Test with missing repository**:
   ```bash
   python3 scripts/index_thn_code.py \
       --repository repos/nonexistent \
       --name nonexistent
   ```
   - Should show clear error message
   - Should not crash

2. **Test with invalid file**:
   - Create repository with syntax error in Python file
   - Index repository
   - Should log warning but continue processing other files

3. **Test with API failure**:
   - Temporarily disable OpenAI API key
   - Try to index repository
   - Should show clear error about API failure

**Expected Outcome**: All errors are handled gracefully with clear messages

---

## Troubleshooting

### Issue: pgvector extension not found

**Solution**:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Issue: Embeddings not generating

**Check**:
- OpenAI API key is set in `.env`
- API key has sufficient credits
- Network connection is working

**Verify**:
```python
from brain_core.embedding_service import generate_embedding
test_embedding = generate_embedding("test")
print(f"Embedding dimension: {len(test_embedding)}")  # Should be 1536
```

### Issue: Code retrieval returns no results

**Check**:
- Repository is indexed (check `code_index` table)
- Embeddings are generated (check `embedding IS NOT NULL`)
- Query is in THN project context

**Verify**:
```sql
SELECT COUNT(*) FROM code_index WHERE embedding IS NOT NULL;
```

### Issue: Slow indexing

**Solutions**:
- Process in smaller batches
- Use incremental indexing for updates
- Check OpenAI rate limits

---

## Performance Benchmarks

**Expected Performance**:
- Code indexing: ~100-500 files per minute (depends on file size)
- Embedding generation: ~50 chunks per batch (respects rate limits)
- Code retrieval: <500ms for similarity search
- Context building: <100ms (excluding retrieval)

**Optimization Tips**:
- Use incremental indexing for updates
- Batch embedding generation
- Use database indexes effectively
- Cache frequently accessed code chunks

---

## Next Steps

After successful implementation:
1. Index all THN repositories
2. Test code retrieval in various scenarios
3. Integrate with production environment mapping
4. Enhance teaching and learning support
5. Monitor performance and optimize as needed

