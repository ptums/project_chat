# Data Model: Database Backup Script

**Feature**: 001-database-backup  
**Date**: 2025-01-27  
**Phase**: 1 - Design

## Overview

This feature does not introduce new database tables. Instead, it creates backup files and metadata files that represent snapshots of database state at specific points in time.

## Entities

### Backup File

**Purpose**: Complete database snapshot in PostgreSQL custom format

**Format**: PostgreSQL custom format dump file (`.dump` extension)

**Properties**:
- **File Path**: Filesystem path to backup file
- **File Name**: `{database_name}_{environment}_{timestamp}.dump`
  - Example: `project_chat_dev_2025-01-27T14-30-00Z.dump`
- **File Size**: Size in bytes (varies based on database size and compression)
- **File Format**: PostgreSQL custom format (`pg_dump -Fc`)
- **Compression**: Level 6 (balance between speed and size)
- **Content**: Complete database schema and data (all tables, indexes, constraints, extensions)

**Validation Rules**:
- File must be readable by `pg_restore`
- File must pass integrity verification (`pg_restore --list` succeeds)
- File checksum (SHA256) must match metadata file checksum

**Relationships**:
- One backup file has one metadata file (1:1)
- Backup file represents one database at one point in time

### Backup Metadata File

**Purpose**: Machine-readable information about a backup file

**Format**: JSON file (`.metadata.json` extension)

**Schema**:
```json
{
  "backup_timestamp": "2025-01-27T14:30:00Z",
  "environment": "dev",
  "database_name": "project_chat_dev",
  "backup_file": "project_chat_dev_2025-01-27T14-30-00Z.dump",
  "backup_size_bytes": 52428800,
  "checksum_sha256": "a1b2c3d4e5f6...",
  "table_counts": {
    "conversations": 150,
    "messages": 3420,
    "project_knowledge": 12,
    "conversation_index": 145
  },
  "pg_dump_version": "15.1",
  "postgresql_version": "15.11"
}
```

**Properties**:
- **backup_timestamp** (string, ISO 8601): When backup was created
- **environment** (string, enum: "dev" | "prod"): Environment identifier
- **database_name** (string): Name of backed up database
- **backup_file** (string): Filename of backup file (without path)
- **backup_size_bytes** (integer): Size of backup file in bytes
- **checksum_sha256** (string, hex): SHA256 checksum of backup file
- **table_counts** (object): Map of table names to row counts
- **pg_dump_version** (string): Version of pg_dump used
- **postgresql_version** (string): Version of PostgreSQL server

**Validation Rules**:
- All fields are required
- `backup_timestamp` must be valid ISO 8601 format
- `environment` must be "dev" or "prod"
- `checksum_sha256` must be 64-character hexadecimal string
- `table_counts` must contain at least one table
- `backup_size_bytes` must be positive integer

**Relationships**:
- One metadata file corresponds to one backup file (1:1)
- Metadata file name matches backup file name with `.metadata.json` extension

### Backup Storage Location

**Purpose**: Directory where backup files are stored

**Default Location**: `db/backups/` (relative to project root)

**Properties**:
- **Path**: Filesystem directory path
- **Permissions**: Must be writable by backup script user
- **Disk Space**: Must have sufficient space (recommended: 2x database size)

**Structure**:
```
db/backups/
├── project_chat_dev_2025-01-27T14-30-00Z.dump
├── project_chat_dev_2025-01-27T14-30-00Z.metadata.json
├── project_chat_prod_2025-01-27T15-00-00Z.dump
└── project_chat_prod_2025-01-27T15-00-00Z.metadata.json
```

**Validation Rules**:
- Directory must exist or be creatable
- Directory must be writable
- Sufficient disk space must be available (checked before backup)

## Data Flow

### Backup Creation Flow

1. **Load Configuration**: Read database connection from .env/.env.local files
2. **Detect Environment**: Determine dev or prod from configuration
3. **Validate Storage**: Check backup directory exists and is writable
4. **Check Disk Space**: Verify sufficient space available (2x database size recommended)
5. **Generate Timestamp**: Create ISO 8601 timestamp for backup
6. **Create Backup File**: Run `pg_dump` to create backup file
7. **Calculate Checksum**: Compute SHA256 checksum of backup file
8. **Query Metadata**: Get table counts and PostgreSQL version
9. **Create Metadata File**: Write JSON metadata file
10. **Verify Integrity**: Run `pg_restore --list` to verify backup file
11. **Report Success**: Display backup location and metadata summary

### Backup Verification Flow

1. **Load Metadata**: Read metadata file (JSON)
2. **Check File Exists**: Verify backup file exists at expected path
3. **Verify Checksum**: Calculate current SHA256 and compare with stored checksum
4. **Verify Structure**: Run `pg_restore --list` to validate backup format
5. **Report Results**: Display verification status (success or failure with details)

## State Transitions

### Backup File States

```
NON_EXISTENT → CREATING → VERIFYING → VERIFIED → (READY)
                    ↓
                 FAILED
```

- **NON_EXISTENT**: Backup file does not exist
- **CREATING**: `pg_dump` is running, file is being written
- **VERIFYING**: Backup file created, integrity check in progress
- **VERIFIED**: Backup file passes all integrity checks
- **FAILED**: Backup creation or verification failed
- **READY**: Backup file is verified and ready for restoration

## Constraints

### Backup File Constraints

- Backup file must be created atomically (all-or-nothing)
- Partial backup files must be detected and cleaned up
- Backup file size must not exceed available disk space
- Backup file must be readable by `pg_restore`

### Metadata File Constraints

- Metadata file must be created after backup file (to include checksum)
- Metadata file must be valid JSON
- All required fields must be present
- Checksum in metadata must match actual backup file checksum

### Storage Constraints

- Backup directory must exist or be creatable
- Backup directory must have write permissions
- Sufficient disk space must be available (checked before backup)
- Backup files should not be committed to version control (gitignored)

## Integration Points

### Database Connection

- Uses existing `brain_core/config.py` for database configuration
- Supports both development (DEV_DB_*) and production (DB_*) environment variables
- Reads from `.env.local` (preferred) or `.env` files

### File System

- Creates backup files in `db/backups/` directory (default)
- Supports custom backup location via command-line argument
- Creates metadata files alongside backup files

### PostgreSQL Tools

- Requires `pg_dump` to be installed and available in PATH
- Requires `pg_restore` for integrity verification
- Uses PostgreSQL connection parameters from environment configuration

