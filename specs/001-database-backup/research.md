# Research: Database Backup Script

**Feature**: 001-database-backup  
**Date**: 2025-01-27  
**Phase**: 0 - Research

## Research Questions

1. What PostgreSQL backup tool should be used for complete database backups?
2. What backup file format best supports restoration and integrity verification?
3. How to verify backup file integrity after creation?
4. How to handle large databases (up to 10GB) efficiently?
5. How to ensure zero-downtime backups?
6. What metadata should be included with backups?

## Findings

### 1. PostgreSQL Backup Tool: pg_dump

**Decision**: Use `pg_dump` (PostgreSQL's native backup utility)

**Rationale**:
- Standard PostgreSQL tool, available on all PostgreSQL installations
- Supports complete database backups (schema + data)
- Handles all PostgreSQL data types including vector embeddings (pgvector)
- Creates portable SQL dumps that can be restored with `psql` or `pg_restore`
- Supports compression for large databases
- Non-blocking: creates consistent snapshots without locking tables
- Well-documented and widely used

**Alternatives Considered**:
- `pg_dumpall`: Rejected - backs up entire PostgreSQL cluster, not single database
- Custom Python backup script: Rejected - would need to handle all PostgreSQL types, complex, error-prone
- Third-party backup tools: Rejected - adds unnecessary dependencies, pg_dump is sufficient

### 2. Backup File Format: Custom Format with Compression

**Decision**: Use `pg_dump` with `-Fc` (custom format) and `-Z 6` (compression level 6)

**Rationale**:
- Custom format (`-Fc`) supports parallel restoration and selective table restoration
- Compression reduces storage requirements (critical for 10GB databases)
- Custom format includes metadata about database structure
- Can be restored with `pg_restore` (more flexible than plain SQL)
- Compression level 6 provides good balance between speed and compression ratio
- Custom format files can be verified for integrity

**Alternatives Considered**:
- Plain SQL format (`-Fp`): Rejected - larger file size, slower restoration, no selective restore
- Tar format (`-Ft`): Rejected - less flexible than custom format, similar compression
- No compression: Rejected - backup files would be too large (10GB+ uncompressed)

### 3. Backup Integrity Verification

**Decision**: Use `pg_restore --list` to verify backup file structure, plus file checksum (SHA256)

**Rationale**:
- `pg_restore --list` validates backup file format and structure without full restoration
- SHA256 checksum detects file corruption or tampering
- Fast verification (doesn't require full restore)
- Standard approach for backup verification
- Can be stored in metadata file for later verification

**Alternatives Considered**:
- Full restore test: Rejected - too slow and resource-intensive for regular verification
- File size check only: Rejected - doesn't detect corruption, only truncation
- No verification: Rejected - violates requirement FR-008 (must validate integrity)

### 4. Large Database Handling

**Decision**: Use `pg_dump` with compression and streaming output to avoid memory issues

**Rationale**:
- `pg_dump` handles large databases efficiently by streaming output
- Compression reduces storage requirements and transfer time
- Custom format supports parallel operations during restore
- No memory limitations for databases up to 10GB
- Standard PostgreSQL tool optimized for large databases

**Alternatives Considered**:
- Table-by-table backup: Rejected - complex, slower, harder to maintain consistency
- Incremental backups: Rejected - out of scope, only full backups required
- Database replication: Rejected - overkill for backup use case

### 5. Zero-Downtime Backups

**Decision**: Use `pg_dump` default behavior (non-blocking snapshot)

**Rationale**:
- `pg_dump` creates consistent snapshots without requiring table locks
- Uses PostgreSQL's MVCC (Multi-Version Concurrency Control) for consistency
- Does not block reads or writes during backup
- Standard PostgreSQL behavior, no special configuration needed
- Meets zero-downtime requirement (SC-003)

**Alternatives Considered**:
- Exclusive locks: Rejected - would cause downtime, violates requirement
- Read replicas: Rejected - adds complexity, not needed for backup use case
- Scheduled maintenance windows: Rejected - violates zero-downtime requirement

### 6. Backup Metadata

**Decision**: Create separate JSON metadata file alongside backup file

**Rationale**:
- JSON format is human-readable and machine-parseable
- Separate file allows metadata inspection without opening backup file
- Can include: timestamp, environment, database name, table counts, file checksum, backup size
- Easy to extend with additional metadata in future
- Can be used for backup management and verification

**Metadata Fields**:
- `backup_timestamp`: ISO 8601 timestamp of backup creation
- `environment`: "dev" or "prod"
- `database_name`: Name of backed up database
- `backup_file`: Path to backup file
- `backup_size_bytes`: Size of backup file in bytes
- `checksum_sha256`: SHA256 checksum of backup file
- `table_counts`: Object with table names and row counts
- `pg_dump_version`: Version of pg_dump used
- `postgresql_version`: Version of PostgreSQL server

**Alternatives Considered**:
- Metadata embedded in backup filename: Rejected - limited metadata, harder to parse
- Metadata in database: Rejected - requires database access, backup should be self-contained
- No metadata: Rejected - violates requirement FR-013 (must include metadata)

## Implementation Notes

### pg_dump Command Structure

```bash
pg_dump -h <host> -p <port> -U <user> -d <database> \
  -Fc \           # Custom format
  -Z 6 \          # Compression level 6
  -f <output_file> \
  --no-owner \    # Don't include ownership commands
  --no-acl        # Don't include ACL commands
```

### Backup File Naming Convention

Format: `{database_name}_{environment}_{timestamp}.dump`

Example: `project_chat_dev_2025-01-27T14-30-00Z.dump`

### Metadata File Naming

Format: `{database_name}_{environment}_{timestamp}.metadata.json`

Example: `project_chat_dev_2025-01-27T14-30-00Z.metadata.json`

### Integrity Verification Process

1. Run `pg_restore --list <backup_file>` to verify file structure
2. Calculate SHA256 checksum of backup file
3. Store checksum in metadata file
4. On verification, compare stored checksum with current file checksum
5. Report success/failure with clear error messages

### Error Handling

- Database connection failures: Clear error message with connection details
- Insufficient disk space: Check available space before backup, fail early with clear message
- Permission errors: Verify database user has read permissions, file system has write permissions
- Interrupted backups: Partial files should be detected and cleaned up
- pg_dump failures: Capture stderr, provide actionable error messages

## Dependencies

- PostgreSQL client tools (pg_dump, pg_restore) - must be installed on system
- Python standard library: hashlib (SHA256), json, subprocess, datetime
- Existing project dependencies: psycopg2-binary, python-dotenv (for config loading)

## References

- PostgreSQL pg_dump documentation: https://www.postgresql.org/docs/current/app-pgdump.html
- PostgreSQL pg_restore documentation: https://www.postgresql.org/docs/current/app-pgrestore.html
- PostgreSQL backup and restore best practices: https://www.postgresql.org/docs/current/backup.html

