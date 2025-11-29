# Production Setup Guide

Simple guide for setting up project_chat in a production environment.

## Prerequisites

- PostgreSQL 14+ installed and running
- Python 3.10+ installed
- pgvector extension installed (for DAAS semantic search)
- ChatGPT export zip file ready

## Setup Steps

### 1. Configure Environment

Create `.env` or `.env.local` with your production database settings:

```bash
# Database Configuration
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=your_production_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password

# OpenAI (required for DAAS embeddings)
OPENAI_API_KEY=your_openai_api_key

# Ollama (optional, for conversation indexing)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3:8b
```

### 2. Initialize Database

```bash
# Create database if it doesn't exist
python3 init_db.py

# Or manually:
createdb your_production_db_name
```

### 3. Run Migrations

```bash
# Run all migrations at once
./db/migrations/run_all_migrations.sh your_production_db_name

# Or manually:
psql -d your_production_db_name -f db/migrations/000_initial_schema.sql
psql -d your_production_db_name -f db/migrations/001_create_conversation_index.sql
psql -d your_production_db_name -c "CREATE EXTENSION IF NOT EXISTS vector;"
psql -d your_production_db_name -f db/migrations/002_daas_embeddings.sql
```

### 4. Load Project Knowledge

```bash
psql -d your_production_db_name -f db/seeds/project_knowledge_seed.sql
```

### 5. Import ChatGPT Conversations

```bash
# Test import first (dry-run)
python3 import_chatgpt_from_zip.py chatgpt_export.zip --dry-run

# Actually import
python3 import_chatgpt_from_zip.py chatgpt_export.zip
```

### 6. Index Conversations (Optional)

If you have Ollama running and want to organize conversations:

```bash
# Verify table structure
python3 setup_prod_conversation_index.py --verify

# Index all conversations
python3 setup_prod_conversation_index.py --index-all
```

### 7. Generate Embeddings for DAAS

```bash
# Generate embeddings for DAAS dream entries
python3 backfill_embeddings.py
```

## Verification

```bash
# Check conversations imported
psql -d your_production_db_name -c "SELECT COUNT(*) FROM conversations;"

# Check messages imported
psql -d your_production_db_name -c "SELECT COUNT(*) FROM messages;"

# Check indexed conversations
psql -d your_production_db_name -c "SELECT COUNT(*) FROM conversation_index;"

# Check DAAS embeddings
psql -d your_production_db_name -c "SELECT COUNT(*) FROM conversation_index WHERE project='DAAS' AND embedding IS NOT NULL;"
```

## Troubleshooting

### pgvector Extension Not Found

Install pgvector for your PostgreSQL version, then:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Invalid Project Values

If you have conversations with invalid project values:

```bash
# Fix invalid projects
python3 fix_invalid_projects.py --fix

# Delete empty conversations (optional)
python3 fix_invalid_projects.py --delete-empty
```

### Import Errors

- Ensure the zip file contains `conversations.json`
- Check database connection settings in `.env`
- Verify database exists and user has proper permissions

## Next Steps

Once setup is complete, you can start using the chat interface:

```bash
python3 chat_cli.py
```

