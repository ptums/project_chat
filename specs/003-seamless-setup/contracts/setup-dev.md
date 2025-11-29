# Contract: Development Setup Script

**Feature**: 003-seamless-setup  
**Component**: `setup_dev.py`  
**Date**: 2025-01-27

## Overview

The development setup script (`setup_dev.py`) provides a single-command procedure to set up a local development environment. It creates the development database, applies all migrations, and loads development seed data.

## Command Interface

### Basic Usage

```bash
python3 setup_dev.py
```

### Options

```bash
python3 setup_dev.py [--skip-seed] [--force-recreate] [--verbose]
```

- `--skip-seed`: Skip loading development seed data (useful for testing migrations only)
- `--force-recreate`: Drop and recreate the database if it already exists (destructive)
- `--verbose`: Show detailed output for each step

## Environment Requirements

### Required Environment Variables

- `ENV_MODE`: Must be set to `development` or `dev`
- `DEV_DB_NAME`: Development database name (default: `project_chat_dev`)
- `DEV_DB_HOST`: Database host (default: `127.0.0.1`)
- `DEV_DB_PORT`: Database port (default: `5432`)
- `DEV_DB_USER`: Database user (default: `dev_user`)
- `DEV_DB_PASSWORD`: Database password (default: empty string)

### Prerequisites

- PostgreSQL server running and accessible
- Python 3.10+ with `psycopg2-binary` installed
- Database user has CREATE DATABASE privileges (for initial setup)

## Behavior

### Step 1: Environment Validation

1. Check that `ENV_MODE` is set to `development` or `dev`
2. Validate database connection variables are set
3. Test connection to PostgreSQL server
4. **Error if**: Environment is not development mode

### Step 2: Database Initialization

1. Call `init_db.py` to initialize the database (reads from `.env.local` or `.env`)
2. `init_db.py` will:
   - Read `DEV_DB_NAME`, `DEV_DB_HOST`, `DEV_DB_PORT`, `DEV_DB_USER`, `DEV_DB_PASSWORD` from environment
   - Check if development database exists
   - Create database if it doesn't exist
   - Handle existing databases gracefully (informational message)
3. If `--force-recreate` is set:
   - Drop existing database first
   - Then call `init_db.py` to create new database
4. **Error if**: Database initialization fails (permissions, connection issues)

### Step 3: Migration Application

1. Check which migrations have been applied (by table existence):
   - Migration 000: `conversations` table exists
   - Migration 001: `conversation_index` table exists
   - Migration 002: `conversation_index.embedding` column exists
2. Run `db/migrations/run_all_migrations.sh` or equivalent Python logic
3. Apply migrations in order: 000 → 001 → 002
4. Skip migrations that have already been applied (informational message)
5. **Error if**: Migration fails (with clear error message)

### Step 4: Seed Data Loading

1. If `--skip-seed` is set, skip this step
2. Execute `db/seeds/project_knowledge_seed.sql` using `psql` or `psycopg2` (shared project knowledge) - **loaded first as foundational data for RAG**
3. Execute `db/seeds/dev_seed.sql` using `psql` or `psycopg2` (sample conversations) - **loaded after project knowledge**
4. Use UPSERT semantics (`ON CONFLICT DO UPDATE`) for idempotency
5. Verify seed data was loaded:
   - Check project knowledge entries (from project_knowledge_seed.sql)
   - Check conversation count (from dev_seed.sql)
6. **Error if**: Seed data file is missing or malformed

### Step 5: Verification

1. Verify all required tables exist:
   - `conversations`
   - `messages`
   - `project_knowledge`
   - `conversation_index`
2. Verify seed data is present (if loaded):
   - Check that at least 3 conversations exist
   - Check that messages exist for seed conversations
3. Display summary:
   - Database name
   - Migrations applied
   - Seed data status
   - Next steps (e.g., "Run: python3 chat_cli.py")

## Output Format

### Success Output

```
========================================
Development Environment Setup
========================================

✓ Environment validated (ENV_MODE=development)
✓ Database created: project_chat_dev
✓ Migration 000 applied: Initial schema
✓ Migration 001 applied: Conversation index
✓ Migration 002 applied: DAAS embeddings
✓ Seed data loaded: 3 sample conversations

Setup complete! You can now run:
  python3 chat_cli.py
```

### Error Output

```
ERROR: Environment validation failed
  ENV_MODE is set to 'production', but this is a development setup script.
  Please set ENV_MODE=development in your .env.local file.

For production setup, use: python3 setup_prod.py
```

## Error Handling

### Common Errors

1. **Environment not development**: Clear error with instructions to set `ENV_MODE=development`
2. **Database connection failed**: Error with connection details and troubleshooting steps
3. **Migration failed**: Show migration number and error message, suggest checking migration file
4. **Seed data missing**: Error with path to expected seed file
5. **Permission denied**: Error with instructions to check database user privileges

### Error Messages

All errors should:

- Use clear, descriptive language
- Provide actionable guidance
- Reference relevant environment variables or files
- Suggest next steps or documentation

## Exit Codes

- `0`: Success
- `1`: Environment validation error
- `2`: Database creation/connection error
- `3`: Migration error
- `4`: Seed data loading error
- `5`: Verification error

## Examples

### First-time Setup

```bash
$ python3 setup_dev.py
========================================
Development Environment Setup
========================================

✓ Environment validated (ENV_MODE=development)
✓ Database created: project_chat_dev
✓ Migration 000 applied: Initial schema
✓ Migration 001 applied: Conversation index
✓ Migration 002 applied: DAAS embeddings
✓ Seed data loaded: 3 sample conversations

Setup complete! You can now run:
  python3 chat_cli.py
```

### Re-running Setup (Database Exists)

```bash
$ python3 setup_dev.py
========================================
Development Environment Setup
========================================

✓ Environment validated (ENV_MODE=development)
ℹ Database already exists: project_chat_dev
✓ Migration 000 already applied (skipped)
✓ Migration 001 already applied (skipped)
✓ Migration 002 already applied (skipped)
✓ Seed data loaded: 3 sample conversations (updated)

Setup complete! You can now run:
  python3 chat_cli.py
```

### Force Recreate Database

```bash
$ python3 setup_dev.py --force-recreate
========================================
Development Environment Setup
========================================

⚠ WARNING: This will delete all data in project_chat_dev
Continue? (y/N): y
✓ Database dropped and recreated: project_chat_dev
✓ Migration 000 applied: Initial schema
✓ Migration 001 applied: Conversation index
✓ Migration 002 applied: DAAS embeddings
✓ Seed data loaded: 3 sample conversations

Setup complete! You can now run:
  python3 chat_cli.py
```
