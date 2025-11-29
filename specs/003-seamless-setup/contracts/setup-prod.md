# Contract: Production Setup Script

**Feature**: 003-seamless-setup  
**Component**: `setup_prod.py`  
**Date**: 2025-01-27

## Overview

The production setup script (`setup_prod.py`) provides a single-command procedure to set up a production environment. It applies all migrations and loads production seed data (project knowledge). It does NOT create the database (assumes database already exists).

## Command Interface

### Basic Usage

```bash
python3 setup_prod.py
```

### Options

```bash
python3 setup_prod.py [--skip-seed] [--verify-only] [--verbose]
```

- `--skip-seed`: Skip loading production seed data (useful for testing migrations only)
- `--verify-only`: Only verify environment and database state, don't make changes
- `--verbose`: Show detailed output for each step

## Environment Requirements

### Required Environment Variables

- `ENV_MODE`: Must be set to `production` or `prod`
- `DB_NAME`: Production database name (required)
- `DB_HOST`: Database host (default: `127.0.0.1`)
- `DB_PORT`: Database port (default: `5432`)
- `DB_USER`: Database user (required)
- `DB_PASSWORD`: Database password (required)

### Prerequisites

- PostgreSQL server running and accessible
- Production database already exists (script does NOT create database)
- Python 3.10+ with `psycopg2-binary` installed
- Database user has CREATE, ALTER, and INSERT privileges

## Behavior

### Step 1: Environment Validation

1. Check that `ENV_MODE` is set to `production` or `prod`
2. Validate all required database connection variables are set
3. Test connection to production database
4. Warn if connecting to `localhost` or `127.0.0.1` (may indicate misconfiguration)
5. **Error if**: Environment is not production mode
6. **Error if**: Required database variables are missing

### Step 2: Database Initialization

1. Call `init_db.py` to ensure production database exists (reads from `.env`)
2. `init_db.py` will:
   - Read `DB_NAME`, `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` from environment
   - Check if production database exists
   - Create database if it doesn't exist
   - Handle existing databases gracefully (informational message)
3. Verify database is accessible
4. Check current database schema state:
   - Which migrations have been applied
   - Which tables exist
   - Whether seed data is present
5. If `--verify-only` is set, display state and exit
6. **Error if**: Database initialization fails or database is not accessible

### Step 3: Migration Application

1. Check which migrations have been applied (by table existence):
   - Migration 000: `conversations` table exists
   - Migration 001: `conversation_index` table exists
   - Migration 002: `conversation_index.embedding` column exists
2. Run `db/migrations/run_all_migrations.sh` or equivalent Python logic
3. Apply migrations in order: 000 → 001 → 002
4. Skip migrations that have already been applied (informational message)
5. **Error if**: Migration fails (with clear error message)
6. **Warn if**: Running migrations on database with existing data (may require backup)

### Step 4: Seed Data Loading

1. If `--skip-seed` is set, skip this step
2. Execute `db/seeds/project_knowledge_seed.sql` using `psql` or `psycopg2` (shared project knowledge)
3. Execute `db/seeds/prod_seed.sql` using `psql` or `psycopg2` (if any production-specific data)
4. Use UPSERT semantics (`ON CONFLICT DO UPDATE`) for idempotency
5. Verify seed data was loaded:
   - Check project knowledge entries per project (from project_knowledge_seed.sql)
   - Check any production-specific data (from prod_seed.sql)
6. **Error if**: Seed data file is missing or malformed

### Step 5: Verification

1. Verify all required tables exist:
   - `conversations`
   - `messages`
   - `project_knowledge`
   - `conversation_index`
2. Verify seed data is present (if loaded):
   - Check that project knowledge exists for all active projects (THN, DAAS, FF, 700B)
3. Display summary:
   - Database name and host
   - Migrations applied
   - Seed data status
   - Next steps (e.g., "Verify application connectivity")

## Output Format

### Success Output

```
========================================
Production Environment Setup
========================================

✓ Environment validated (ENV_MODE=production)
✓ Database verified: ongoing_projects (127.0.0.1:5432)
✓ Migration 000 already applied (skipped)
✓ Migration 001 already applied (skipped)
✓ Migration 002 applied: DAAS embeddings
✓ Seed data loaded: Project knowledge for 4 projects

Setup complete! Verify application connectivity.
```

### Verification-Only Output

```
========================================
Production Environment Verification
========================================

✓ Environment validated (ENV_MODE=production)
✓ Database verified: ongoing_projects (127.0.0.1:5432)

Migration Status:
  ✓ Migration 000: Applied (conversations table exists)
  ✓ Migration 001: Applied (conversation_index table exists)
  ✓ Migration 002: Applied (embedding column exists)

Seed Data Status:
  ✓ THN: 2 project knowledge entries
  ✓ DAAS: 2 project knowledge entries
  ✓ FF: 1 project knowledge entry
  ✓ 700B: 1 project knowledge entry

All checks passed. Environment is ready.
```

### Error Output

```
ERROR: Environment validation failed
  ENV_MODE is set to 'development', but this is a production setup script.
  Please set ENV_MODE=production in your .env file.

For development setup, use: python3 setup_dev.py
```

## Error Handling

### Common Errors

1. **Environment not production**: Clear error with instructions to set `ENV_MODE=production`
2. **Database doesn't exist**: Error with instructions to create database first
3. **Database connection failed**: Error with connection details and troubleshooting steps
4. **Migration failed**: Show migration number and error message, suggest checking migration file
5. **Seed data missing**: Error with path to expected seed file
6. **Permission denied**: Error with instructions to check database user privileges
7. **Localhost warning**: Warn if connecting to localhost (may indicate misconfiguration)

### Error Messages

All errors should:
- Use clear, descriptive language
- Provide actionable guidance
- Reference relevant environment variables or files
- Suggest next steps or documentation
- Avoid exposing sensitive information (passwords, connection strings)

## Exit Codes

- `0`: Success
- `1`: Environment validation error
- `2`: Database connection/verification error
- `3`: Migration error
- `4`: Seed data loading error
- `5`: Verification error

## Safety Features

### Data Protection

- **No database creation**: Production script does NOT create databases (prevents accidental creation)
- **Migration warnings**: Warn if running migrations on database with existing data
- **Backup recommendation**: Suggest backing up database before running migrations
- **Idempotent operations**: Seed data uses UPSERT to avoid duplicates

### Validation

- **Environment check**: Verify `ENV_MODE=production` before proceeding
- **Database existence**: Verify database exists before attempting operations
- **Connection test**: Test database connection before proceeding
- **Localhost warning**: Warn if connecting to localhost (may indicate dev/prod confusion)

## Examples

### First-time Production Setup

```bash
$ python3 setup_prod.py
========================================
Production Environment Setup
========================================

✓ Environment validated (ENV_MODE=production)
✓ Database verified: ongoing_projects (prod.example.com:5432)
✓ Migration 000 applied: Initial schema
✓ Migration 001 applied: Conversation index
✓ Migration 002 applied: DAAS embeddings
✓ Seed data loaded: Project knowledge for 4 projects

Setup complete! Verify application connectivity.
```

### Update Existing Production Database

```bash
$ python3 setup_prod.py
========================================
Production Environment Setup
========================================

✓ Environment validated (ENV_MODE=production)
✓ Database verified: ongoing_projects (prod.example.com:5432)
⚠ WARNING: Database contains existing data (100 conversations, 500 messages)
  Consider backing up before applying migrations.
Continue? (y/N): y
✓ Migration 000 already applied (skipped)
✓ Migration 001 already applied (skipped)
✓ Migration 002 applied: DAAS embeddings
✓ Seed data loaded: Project knowledge for 4 projects (updated)

Setup complete! Verify application connectivity.
```

### Verification Only

```bash
$ python3 setup_prod.py --verify-only
========================================
Production Environment Verification
========================================

✓ Environment validated (ENV_MODE=production)
✓ Database verified: ongoing_projects (prod.example.com:5432)

Migration Status:
  ✓ Migration 000: Applied (conversations table exists)
  ✓ Migration 001: Applied (conversation_index table exists)
  ✓ Migration 002: Applied (embedding column exists)

Seed Data Status:
  ✓ THN: 2 project knowledge entries
  ✓ DAAS: 2 project knowledge entries
  ✓ FF: 1 project knowledge entry
  ✓ 700B: 1 project knowledge entry

All checks passed. Environment is ready.
```

