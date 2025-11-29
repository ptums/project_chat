# Database Setup Guide

Complete guide for setting up the project_chat database from scratch, including all migrations and data import scripts.

## Overview

This project uses PostgreSQL with the following features:
- **001-dev-environment**: Base tables (conversations, messages, project_knowledge)
- **001-ollama-organizer**: Conversation indexing (conversation_index table)
- **002-daas-semantic-retrieval**: Vector embeddings for DAAS dreams (pgvector extension)

## Quick Setup (Fresh Database)

### Step 1: Run All Migrations

```bash
# Option A: Run all migrations at once
./db/migrations/run_all_migrations.sh your_database_name

# Option B: Run migrations individually
psql -d your_database_name -f db/migrations/000_initial_schema.sql
psql -d your_database_name -f db/migrations/001_create_conversation_index.sql
psql -d your_database_name -c "CREATE EXTENSION IF NOT EXISTS vector;"
psql -d your_database_name -f db/migrations/002_daas_embeddings.sql
```

### Step 2: Import ChatGPT Conversations

```bash
# Place your ChatGPT export zip file in the project root
# Then run:
python3 import_chatgpt_from_zip.py chatgpt_export.zip

# Or test first with dry-run:
python3 import_chatgpt_from_zip.py chatgpt_export.zip --dry-run
```

### Step 3: Index Conversations (Optional)

If you want to organize and index the imported conversations:

```bash
# Index all conversations (requires Ollama running)
python3 setup_prod_conversation_index.py --index-all

# Or verify table structure first:
python3 setup_prod_conversation_index.py --verify
```

### Step 4: Generate Embeddings for DAAS Entries

```bash
# Generate embeddings for existing DAAS conversations
python3 backfill_embeddings.py
```

## Migration Scripts

### 000_initial_schema.sql
**Feature**: 001-dev-environment  
**Creates**:
- `conversations` table (id, title, project, created_at)
- `messages` table (id, conversation_id FK, role, content, meta_json, created_at)
- `project_knowledge` table (id, project, key, summary, created_at)
- Indexes for performance

**Foreign Keys**:
- `messages.conversation_id` → `conversations.id` (ON DELETE CASCADE)

### 001_create_conversation_index.sql
**Feature**: 001-ollama-organizer  
**Creates**:
- `conversation_index` table (session_id PK, project, title, tags, summaries, etc.)
- Indexes for project and date queries

**Foreign Keys**:
- `conversation_index.session_id` → `conversations.id` (ON DELETE CASCADE)

### 002_daas_embeddings.sql
**Feature**: 002-daas-semantic-retrieval  
**Requires**: pgvector extension  
**Adds**:
- `embedding` column to `conversation_index` (vector(1536))
- Vector similarity index for DAAS entries

## Data Import Scripts

### import_chatgpt_from_zip.py
**Purpose**: Import ChatGPT conversation exports from a zip file

**Usage**:
```bash
python3 import_chatgpt_from_zip.py <zip_file_path> [--dry-run]
```

**Features**:
- Extracts zip file automatically
- Finds `conversations.json` in various locations
- Imports conversations and messages
- Infers project tags (THN, DAAS, FF, 700B, general)
- Handles duplicate imports gracefully
- Dry-run mode for testing

**Example**:
```bash
# Test import without saving
python3 import_chatgpt_from_zip.py chatgpt_export.zip --dry-run

# Actually import
python3 import_chatgpt_from_zip.py chatgpt_export.zip
```

### setup_prod_conversation_index.py
**Purpose**: Set up and manage conversation_index table

**Usage**:
```bash
# Verify table structure
python3 setup_prod_conversation_index.py --verify

# Find unindexed conversations
python3 setup_prod_conversation_index.py --index-all --dry-run

# Index all conversations (requires Ollama)
python3 setup_prod_conversation_index.py --index-all

# Index specific conversation
python3 setup_prod_conversation_index.py --index <session_id>
```

### backfill_embeddings.py
**Purpose**: Generate embeddings for existing DAAS entries

**Usage**:
```bash
python3 backfill_embeddings.py
```

**Features**:
- Processes in batches (50 entries per batch)
- Skips entries that already have embeddings
- Shows progress and handles errors gracefully
- Respects OpenAI rate limits

## Table Relationships

```
conversations (id)
    ├── messages (conversation_id FK → conversations.id)
    └── conversation_index (session_id FK → conversations.id)
            └── embedding column (vector(1536)) for DAAS entries

project_knowledge (standalone, no FKs)
```

## Verification Queries

After running migrations, verify everything is set up correctly:

```sql
-- Check all tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
  AND table_name IN ('conversations', 'messages', 'project_knowledge', 'conversation_index')
ORDER BY table_name;

-- Check foreign keys
SELECT 
    tc.table_name, 
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
ORDER BY tc.table_name;

-- Check pgvector extension
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Check embedding column
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'conversation_index' 
  AND column_name = 'embedding';

-- Check vector index
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'conversation_index' 
  AND indexname = 'idx_conversation_index_embedding';
```

## Rollback Scripts

If you need to rollback migrations:

```bash
# Rollback in reverse order
psql -d your_database -f db/migrations/002_daas_embeddings_rollback.sql
psql -d your_database -f db/migrations/001_create_conversation_index_rollback.sql
psql -d your_database -f db/migrations/000_initial_schema_rollback.sql
```

**Warning**: Rollback scripts will DELETE all data in the affected tables!

## Complete Setup Workflow

For a fresh production database:

```bash
# 1. Create database (if needed)
createdb your_database_name

# 2. Run all migrations
./db/migrations/run_all_migrations.sh your_database_name

# 3. Import ChatGPT conversations
python3 import_chatgpt_from_zip.py chatgpt_export.zip

# 4. Verify import
psql -d your_database_name -c "SELECT COUNT(*) FROM conversations;"
psql -d your_database_name -c "SELECT COUNT(*) FROM messages;"

# 5. Index conversations (optional, requires Ollama)
python3 setup_prod_conversation_index.py --index-all

# 6. Generate embeddings for DAAS entries
python3 backfill_embeddings.py

# 7. Verify embeddings
psql -d your_database_name -c "SELECT COUNT(*) FROM conversation_index WHERE embedding IS NOT NULL;"
```

## Troubleshooting

### Migration fails with "relation already exists"
- Tables already exist from a previous setup
- Either drop and recreate, or skip the migration that's failing
- Check what tables exist: `\dt` in psql

### Foreign key constraint fails
- Ensure migrations are run in order (000 → 001 → 002)
- Check that parent tables exist before creating child tables

### pgvector extension not found
- Install pgvector first (see INSTALL_PGVECTOR_M1.md or README.md)
- Then run: `CREATE EXTENSION IF NOT EXISTS vector;`

### Import script can't find conversations.json
- Ensure the zip file contains `conversations.json` at the root
- Or in a subdirectory like `chatgpt_export/conversations.json`
- The script will search recursively

### Embedding generation fails
- Check that OPENAI_API_KEY is set in your environment
- Verify the API key is valid
- Check rate limits if processing many entries

