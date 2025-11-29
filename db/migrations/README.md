# Database Migrations

This directory contains SQL migration scripts for the project_chat database schema.

## Migration Order

Run migrations in numerical order:

1. **000_initial_schema.sql** - Creates base tables: `conversations`, `messages`, `project_knowledge` (001-dev-environment)
2. **001_create_conversation_index.sql** - Creates the `conversation_index` table (001-ollama-organizer feature)
3. **002_daas_embeddings.sql** - Adds `embedding` column and vector index for DAAS semantic retrieval (002-daas-semantic-retrieval)

## Quick Start

### Run All Migrations at Once

```bash
# Make script executable (if not already)
chmod +x db/migrations/run_all_migrations.sh

# Run all migrations
./db/migrations/run_all_migrations.sh your_database_name
```

This will run all migrations in order and install pgvector if needed.

## Usage

### Production Setup (Fresh Database)

If you're setting up a completely fresh database:

```bash
# 1. Create base schema (conversations, messages, project_knowledge)
psql -d your_production_database -f db/migrations/000_initial_schema.sql

# 2. Create the conversation_index table
psql -d your_production_database -f db/migrations/001_create_conversation_index.sql

# 3. Install pgvector extension (if not already installed)
psql -d your_production_database -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 4. Add embedding column and vector index
psql -d your_production_database -f db/migrations/002_daas_embeddings.sql
```

### Production Setup (Existing Database)

If your production database already has base tables but is missing features:

```bash
# 1. Create the conversation_index table (if missing)
psql -d your_production_database -f db/migrations/001_create_conversation_index.sql

# 2. Install pgvector extension (if not already installed)
psql -d your_production_database -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 3. Add embedding column and vector index
psql -d your_production_database -f db/migrations/002_daas_embeddings.sql
```

### Adding Embeddings to Existing conversation_index

If `conversation_index` already exists but you need to add embeddings:

```bash
# 1. Install pgvector extension (if not already installed)
psql -d your_production_database -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 2. Add embedding column and vector index
psql -d your_production_database -f db/migrations/002_daas_embeddings.sql

# 3. Generate embeddings for existing DAAS entries
python3 backfill_embeddings.py
```

## Rollback

If you need to rollback a migration:

```bash
# Rollback DAAS embeddings (removes embedding column and index)
psql -d your_production_database -f db/migrations/002_daas_embeddings_rollback.sql

# Rollback conversation_index (WARNING: deletes all index data!)
psql -d your_production_database -f db/migrations/001_create_conversation_index_rollback.sql
```

## Verification

After running migrations, verify the setup:

```sql
-- Check conversation_index table exists
SELECT table_name FROM information_schema.tables WHERE table_name = 'conversation_index';

-- Check embedding column exists
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'conversation_index' AND column_name = 'embedding';

-- Check vector extension is installed
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Check vector index exists
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'conversation_index' 
  AND indexname = 'idx_conversation_index_embedding';
```

