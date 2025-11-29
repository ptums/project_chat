# Contract: Database Initialization Script

**Feature**: 003-seamless-setup  
**Component**: `init_db.py`  
**Date**: 2025-01-27

## Overview

The database initialization script (`init_db.py`) creates a PostgreSQL database based on configuration from `.env.local` (if exists) or `.env` files. It supports both development and production configurations and can be run standalone or called by setup scripts.

## Command Interface

### Basic Usage

```bash
python3 init_db.py
```

### Options

```bash
python3 init_db.py [--env dev|prod] [--force] [--verbose]
```

- `--env`: Specify environment explicitly (`dev` or `prod`). If not provided, auto-detects from `ENV_MODE` or uses dev if `DEV_DB_NAME` is set.
- `--force`: Drop and recreate the database if it already exists (destructive)
- `--verbose`: Show detailed output for each step

## Environment Requirements

### Development Configuration

Reads from `.env.local` (preferred) or `.env`:
- `ENV_MODE`: Should be `development` or `dev` (optional, auto-detected)
- `DEV_DB_NAME`: Development database name (required if `ENV_MODE=development`)
- `DEV_DB_HOST`: Database host (default: `127.0.0.1`)
- `DEV_DB_PORT`: Database port (default: `5432`)
- `DEV_DB_USER`: Database user (default: `dev_user`)
- `DEV_DB_PASSWORD`: Database password (default: empty string)

### Production Configuration

Reads from `.env`:
- `ENV_MODE`: Should be `production` or `prod` (optional, auto-detected)
- `DB_NAME`: Production database name (required if `ENV_MODE=production`)
- `DB_HOST`: Database host (default: `127.0.0.1`)
- `DB_PORT`: Database port (default: `5432`)
- `DB_USER`: Database user (required)
- `DB_PASSWORD`: Database password (required)

### Prerequisites

- PostgreSQL server running and accessible
- Python 3.10+ with `psycopg2-binary` installed
- Database user has CREATE DATABASE privileges
- `.env.local` or `.env` file exists with database configuration

## Behavior

### Step 1: Environment Detection

1. Load environment variables from `.env.local` (if exists), then `.env`
2. If `--env` flag is provided, use that environment
3. Otherwise, detect environment:
   - If `ENV_MODE` is set, use that
   - If `DEV_DB_NAME` is set, assume development
   - If `DB_NAME` is set, assume production
   - Default to development if ambiguous
4. **Error if**: Cannot determine environment and required variables are missing

### Step 2: Configuration Loading

1. Based on detected environment, load appropriate database configuration:
   - Development: `DEV_DB_NAME`, `DEV_DB_HOST`, `DEV_DB_PORT`, `DEV_DB_USER`, `DEV_DB_PASSWORD`
   - Production: `DB_NAME`, `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`
2. Apply defaults for optional variables
3. **Error if**: Required database name is not set

### Step 3: Database Connection Test

1. Connect to PostgreSQL server using configuration (connect to `postgres` database)
2. Test connection and verify user has CREATE DATABASE privileges
3. **Error if**: Connection fails or user lacks privileges

### Step 4: Database Creation

1. Check if target database exists
2. If exists and `--force` is set:
   - Warn user about data loss
   - Drop existing database
   - Create new database
3. If exists and `--force` is not set:
   - Inform user that database exists
   - Exit successfully (no error)
4. If doesn't exist:
   - Create database
   - Inform user of successful creation
5. **Error if**: Database creation fails (permissions, connection issues, name conflicts)

## Output Format

### Success Output (Database Created)

```
========================================
Database Initialization
========================================

✓ Environment detected: development
✓ Configuration loaded from .env.local
✓ Database connection verified
✓ Database created: project_chat_dev

Initialization complete!
```

### Success Output (Database Exists)

```
========================================
Database Initialization
========================================

✓ Environment detected: development
✓ Configuration loaded from .env.local
✓ Database connection verified
ℹ Database already exists: project_chat_dev

No action needed. Database is ready.
```

### Error Output

```
ERROR: Database initialization failed
  Database name not found in environment variables.
  
  For development, set DEV_DB_NAME in .env.local
  For production, set DB_NAME in .env
  
  Example (.env.local):
    ENV_MODE=development
    DEV_DB_NAME=my_dev_database
    DEV_DB_USER=my_user
    DEV_DB_PASSWORD=my_password
```

## Error Handling

### Common Errors

1. **Database name not set**: Clear error with instructions to set `DEV_DB_NAME` or `DB_NAME`
2. **Database connection failed**: Error with connection details and troubleshooting steps
3. **Permission denied**: Error with instructions to check database user privileges
4. **Database already exists**: Informational message (not an error unless `--force` is used)
5. **Environment detection failed**: Error with instructions to set `ENV_MODE` or use `--env` flag

### Error Messages

All errors should:
- Use clear, descriptive language
- Provide actionable guidance
- Reference relevant environment variables or files
- Suggest next steps or documentation

## Exit Codes

- `0`: Success (database created or already exists)
- `1`: Environment detection error
- `2`: Configuration loading error
- `3`: Database connection error
- `4`: Database creation error
- `5`: Permission error

## Examples

### Development Database Initialization

```bash
$ python3 init_db.py
========================================
Database Initialization
========================================

✓ Environment detected: development
✓ Configuration loaded from .env.local
✓ Database connection verified
✓ Database created: project_chat_dev

Initialization complete!
```

### Production Database Initialization

```bash
$ python3 init_db.py --env prod
========================================
Database Initialization
========================================

✓ Environment detected: production
✓ Configuration loaded from .env
✓ Database connection verified
✓ Database created: ongoing_projects

Initialization complete!
```

### Force Recreate Database

```bash
$ python3 init_db.py --force
========================================
Database Initialization
========================================

✓ Environment detected: development
✓ Configuration loaded from .env.local
✓ Database connection verified
⚠ WARNING: This will delete all data in project_chat_dev
Continue? (y/N): y
✓ Database dropped and recreated: project_chat_dev

Initialization complete!
```

## Integration with Setup Scripts

The `init_db.py` script is designed to be called by `setup_dev.py` and `setup_prod.py`:

- `setup_dev.py` calls `init_db.py` before running migrations
- `setup_prod.py` calls `init_db.py` to ensure database exists before migrations
- Both scripts pass appropriate flags (`--env`, `--force`) as needed
- Script can also be run standalone for database creation only

## Standalone Usage

The script can be used independently to create databases:

```bash
# Create development database
python3 init_db.py

# Create production database
python3 init_db.py --env prod

# Force recreate development database
python3 init_db.py --force
```

