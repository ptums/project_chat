# Contract: Database Backup Script

**Feature**: 001-database-backup  
**Date**: 2025-01-27  
**Contract Type**: CLI Command

## Command Interface

### Command Name

```bash
python3 backup_db.py [OPTIONS]
```

### Synopsis

```bash
backup_db.py [--env ENV] [--output-dir DIR] [--verify FILE] [--list] [--help]
```

## Options

### `--env ENV`

**Type**: String  
**Values**: `dev` | `prod` | `auto`  
**Default**: `auto`  
**Required**: No

**Description**: Specify target environment for backup. If `auto`, detects from environment variables (ENV_MODE or database name variables).

**Examples**:
```bash
python3 backup_db.py --env dev
python3 backup_db.py --env prod
python3 backup_db.py --env auto  # Default behavior
```

### `--output-dir DIR`

**Type**: String (filesystem path)  
**Default**: `db/backups/`  
**Required**: No

**Description**: Custom directory for backup file storage. Directory will be created if it doesn't exist.

**Examples**:
```bash
python3 backup_db.py --output-dir /backups/production
python3 backup_db.py --output-dir ~/backups
```

### `--verify FILE`

**Type**: String (backup file path)  
**Default**: None  
**Required**: No

**Description**: Verify integrity of an existing backup file. Reads corresponding metadata file and validates checksum and structure.

**Examples**:
```bash
python3 backup_db.py --verify db/backups/project_chat_dev_2025-01-27T14-30-00Z.dump
```

### `--list`

**Type**: Flag  
**Default**: False  
**Required**: No

**Description**: List all backup files in the backup directory with their metadata (timestamp, environment, size, verification status).

**Examples**:
```bash
python3 backup_db.py --list
```

### `--help`

**Type**: Flag  
**Description**: Display help message and exit.

## Environment Requirements

### Required Environment Variables

**For Development**:
- `DEV_DB_HOST` (or `DB_HOST`)
- `DEV_DB_PORT` (or `DB_PORT`)
- `DEV_DB_NAME` (required)
- `DEV_DB_USER` (or `DB_USER`)
- `DEV_DB_PASSWORD` (or `DB_PASSWORD`)

**For Production**:
- `DB_HOST`
- `DB_PORT`
- `DB_NAME` (required)
- `DB_USER`
- `DB_PASSWORD`

**Optional**:
- `ENV_MODE`: Used for automatic environment detection if `--env auto`

### Required System Tools

- `pg_dump`: PostgreSQL backup utility (must be in PATH)
- `pg_restore`: PostgreSQL restore utility (for verification, must be in PATH)

### File System Requirements

- Backup directory must be writable
- Sufficient disk space (recommended: 2x database size)

## Behavior

### Default Behavior (No Options)

When run without options, the script:
1. Detects environment automatically from configuration
2. Creates backup in default location (`db/backups/`)
3. Generates timestamped backup file and metadata
4. Verifies backup integrity
5. Displays backup summary

### Backup Creation

**Input**: Environment configuration (from .env files or command-line)

**Process**:
1. Load database configuration for specified environment
2. Validate database connection
3. Check backup directory exists and is writable
4. Estimate disk space requirements
5. Generate backup filename with timestamp
6. Run `pg_dump` to create backup file
7. Calculate SHA256 checksum
8. Query database for table counts and version info
9. Create metadata JSON file
10. Verify backup file integrity (`pg_restore --list`)
11. Display success message with backup location

**Output**: 
- Backup file: `{database_name}_{environment}_{timestamp}.dump`
- Metadata file: `{database_name}_{environment}_{timestamp}.metadata.json`
- Success message to stdout

**Exit Code**: 0 on success, non-zero on failure

### Backup Verification

**Input**: Path to backup file (via `--verify` option)

**Process**:
1. Check backup file exists
2. Load corresponding metadata file
3. Calculate current SHA256 checksum of backup file
4. Compare with stored checksum in metadata
5. Run `pg_restore --list` to verify file structure
6. Report verification results

**Output**: 
- Verification status (success/failure)
- Checksum match status
- Structure validation status
- Error details if verification fails

**Exit Code**: 0 if verification passes, non-zero if fails

### Backup Listing

**Input**: None (uses default backup directory or `--output-dir`)

**Process**:
1. Scan backup directory for `.dump` files
2. For each backup file, load corresponding metadata file
3. Display formatted list with: timestamp, environment, database name, size, verification status

**Output**: 
- Table of backup files with metadata
- Sorted by timestamp (newest first)

**Exit Code**: 0 on success, non-zero on error

## Output Format

### Success Output

```
✓ Backup created successfully

Backup File: db/backups/project_chat_dev_2025-01-27T14-30-00Z.dump
Metadata:    db/backups/project_chat_dev_2025-01-27T14-30-00Z.metadata.json
Size:        50.0 MB
Environment: dev
Database:    project_chat_dev
Tables:      4 (150 conversations, 3420 messages, 12 project_knowledge, 145 conversation_index)
Checksum:    a1b2c3d4e5f6...
Verified:    ✓ Integrity check passed
```

### Error Output

```
✗ Backup failed: Database connection error

Error: connection to server at "127.0.0.1", port 5432 failed: FATAL: database "project_chat_dev" does not exist

Troubleshooting:
  1. Verify database exists: psql -l
  2. Check database name in .env.local: DEV_DB_NAME
  3. Create database if needed: createdb project_chat_dev
```

### Verification Output

```
✓ Backup verification passed

File:        db/backups/project_chat_dev_2025-01-27T14-30-00Z.dump
Checksum:    ✓ Match (a1b2c3d4e5f6...)
Structure:   ✓ Valid (pg_restore --list succeeded)
Size:        50.0 MB
Timestamp:   2025-01-27T14:30:00Z
```

### List Output

```
Backup Files (db/backups/):

Timestamp                Environment  Database            Size      Status
2025-01-27T15:00:00Z    prod         project_chat_prod    125.3 MB  ✓ Verified
2025-01-27T14:30:00Z    dev          project_chat_dev     50.0 MB   ✓ Verified
2025-01-27T10:00:00Z    prod         project_chat_prod    120.1 MB  ✓ Verified
```

## Error Handling

### Error Categories

1. **Configuration Errors**: Missing or invalid environment variables
2. **Connection Errors**: Database server unreachable or authentication failed
3. **Permission Errors**: Insufficient database or filesystem permissions
4. **Disk Space Errors**: Insufficient space for backup
5. **Tool Errors**: `pg_dump` or `pg_restore` not found or failed
6. **File Errors**: Backup file creation or metadata file write failed
7. **Verification Errors**: Backup file integrity check failed

### Error Messages

All errors must:
- Use clear, actionable language
- Include specific error details (from underlying tools)
- Provide troubleshooting steps when applicable
- Exit with non-zero status code

### Error Exit Codes

- `1`: General error (unspecified)
- `2`: Configuration error (missing/invalid env vars)
- `3`: Database connection error
- `4`: Permission error
- `5`: Disk space error
- `6`: Tool not found (`pg_dump`/`pg_restore`)
- `7`: Backup creation failed
- `8`: Verification failed

## Examples

### Basic Usage

```bash
# Backup development database (auto-detect environment)
python3 backup_db.py

# Backup production database
python3 backup_db.py --env prod

# Backup to custom location
python3 backup_db.py --output-dir /backups/production
```

### Verification

```bash
# Verify a specific backup file
python3 backup_db.py --verify db/backups/project_chat_dev_2025-01-27T14-30-00Z.dump
```

### Listing

```bash
# List all backups
python3 backup_db.py --list

# List backups in custom directory
python3 backup_db.py --list --output-dir /backups/production
```

## Integration

### With Existing Scripts

- Uses `brain_core/config.py` for database configuration (same as `init_db.py`, `setup_dev.py`)
- Follows same environment detection pattern as `init_db.py`
- Uses same error handling approach as other database scripts

### With Cron/Scheduling

Script can be scheduled via cron for automated backups:

```bash
# Daily backup at 2 AM
0 2 * * * cd /path/to/project_chat && python3 backup_db.py --env prod >> /var/log/backup.log 2>&1
```

## Testing

### Manual Testing Scenarios

1. **Successful Backup**: Run backup, verify files created, verify integrity
2. **Environment Detection**: Test auto-detection for dev and prod
3. **Custom Output Directory**: Test backup to non-default location
4. **Verification**: Test verification of valid and invalid backup files
5. **Error Handling**: Test with missing database, insufficient permissions, no disk space
6. **Listing**: Test listing with multiple backup files

