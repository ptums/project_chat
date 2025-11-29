# Quickstart: Seamless Environment Setup

**Feature**: 003-seamless-setup  
**Date**: 2025-01-27

## Overview

This feature provides single-command setup procedures for both development and production environments. New developers can get started in under 15 minutes, and production deployments are automated and reliable.

## Development Setup (New Developer)

### Prerequisites

- Python 3.10+ installed
- PostgreSQL server running locally
- Git repository cloned

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment

Create a `.env.local` file in the project root:

```bash
# Development environment
ENV_MODE=development
DEV_DB_NAME=project_chat_dev
DEV_DB_HOST=127.0.0.1
DEV_DB_PORT=5432
DEV_DB_USER=your_postgres_user
DEV_DB_PASSWORD=your_postgres_password
```

### Step 3: Run Setup Script

```bash
python3 setup_dev.py
```

This will:
- Initialize the development database using `init_db.py` (reads from `.env.local`)
- Apply all migrations in order (000 → 001 → 002)
- Load development seed data (in order):
  - Shared project knowledge (FF, DAAS, THN, 700B) - loaded first as foundational data for RAG
  - Sample conversations (3 conversations across different projects) - loaded after project knowledge

### Step 4: Verify Setup

```bash
# Start the chat CLI
python3 chat_cli.py

# Or verify database directly
psql -d project_chat_dev -c "SELECT COUNT(*) FROM conversations;"
```

Expected output: At least 3 conversations from seed data.

## Production Setup

### Prerequisites

- Python 3.10+ installed
- PostgreSQL server running and accessible
- Production database already created
- Production environment variables configured

### Step 1: Configure Environment

Set production environment variables (via `.env` file or environment):

```bash
ENV_MODE=production
DB_NAME=ongoing_projects
DB_HOST=your_production_host
DB_PORT=5432
DB_USER=your_production_user
DB_PASSWORD=your_production_password
```

### Step 2: Initialize Production Database

```bash
# Option A: Use init_db.py (recommended)
python3 init_db.py --env prod

# Option B: Manual creation
createdb -h your_production_host -U your_production_user ongoing_projects
```

### Step 3: Run Setup Script

```bash
python3 setup_prod.py
```

This will:
- Verify environment is production mode
- Ensure production database exists (calls `init_db.py` if needed)
- Apply all migrations in order (000 → 001 → 002)
- Load production seed data:
  - Shared project knowledge (FF, DAAS, THN, 700B)
  - Any production-specific data (if `prod_seed.sql` exists)

### Step 4: Verify Setup

```bash
# Verify migrations applied
psql -d ongoing_projects -c "\d conversations"
psql -d ongoing_projects -c "\d conversation_index"

# Verify seed data loaded
psql -d ongoing_projects -c "SELECT project, COUNT(*) FROM project_knowledge GROUP BY project;"
```

Expected output: Project knowledge entries for THN, DAAS, FF, 700B.

## Common Workflows

### Initialize Database Only

If you just need to create the database without running full setup:

```bash
# Development database
python3 init_db.py

# Production database
python3 init_db.py --env prod

# Force recreate (destructive)
python3 init_db.py --force
```

### Re-running Development Setup

If you need to reset your development environment:

```bash
# Force recreate database (destructive)
python3 setup_dev.py --force-recreate
```

Or to update seed data without recreating:

```bash
# Re-run setup (idempotent)
python3 setup_dev.py
```

### Verifying Production Environment

To check production environment state without making changes:

```bash
python3 setup_prod.py --verify-only
```

### Skipping Seed Data

To test migrations only (without seed data):

```bash
# Development
python3 setup_dev.py --skip-seed

# Production
python3 setup_prod.py --skip-seed
```

## Troubleshooting

### Database Connection Failed

**Error**: `psycopg2.OperationalError: connection to server failed`

**Solutions**:
1. Verify PostgreSQL is running: `pg_isready`
2. Check connection variables in `.env.local` (dev) or `.env` (prod)
3. Verify database user has correct permissions
4. Check firewall/network connectivity for production

### Migration Already Applied

**Message**: `Migration 000 already applied (skipped)`

**Action**: This is normal. Migrations are idempotent and will skip if already applied.

### Environment Mode Mismatch

**Error**: `ENV_MODE is set to 'production', but this is a development setup script`

**Solution**: 
- For development: Set `ENV_MODE=development` in `.env.local`
- For production: Use `setup_prod.py` instead of `setup_dev.py`

### Seed Data Not Loading

**Error**: `Seed data file not found: db/seeds/dev_seed.sql`

**Solution**:
1. Verify seed files exist in `db/seeds/` directory
2. Check file permissions (should be readable)
3. Verify SQL syntax is valid

### Database Initialization Fails

**Error**: `Database name not found in environment variables`

**Solution**:
1. Check that `.env.local` (dev) or `.env` (prod) file exists
2. Verify `DEV_DB_NAME` (dev) or `DB_NAME` (prod) is set
3. Ensure `ENV_MODE` is set correctly (`development` or `production`)
4. Use `--env dev` or `--env prod` to explicitly specify environment

### pgvector Extension Not Found

**Error**: `ERROR: extension "vector" is not available`

**Solution**:
1. Install pgvector extension (see README.md for platform-specific instructions)
2. Run: `psql -d your_database -c "CREATE EXTENSION IF NOT EXISTS vector;"`
3. Re-run setup script

## Next Steps

After setup is complete:

1. **Development**: Start using the chat CLI (`python3 chat_cli.py`)
2. **Production**: Verify application connectivity and test features
3. **Import Data**: Use `import_chatgpt_from_zip.py` to import historical conversations
4. **Index Conversations**: Use `setup_prod_conversation_index.py` to index conversations (requires Ollama)
5. **Generate Embeddings**: Use `backfill_embeddings.py` to generate embeddings for DAAS entries

## Additional Resources

- **Main README**: `/README.md` - Project overview and features
- **Database Setup Guide**: `/DATABASE_SETUP.md` - Detailed database setup instructions
- **Migration Guide**: `/db/migrations/README.md` - Migration-specific documentation
- **Feature Specs**: `/specs/` - Detailed feature specifications

