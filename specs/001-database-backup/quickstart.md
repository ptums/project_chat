# Quick Start: Database Backup Script

**Feature**: 001-database-backup  
**Date**: 2025-01-27

## Prerequisites

- PostgreSQL database (development or production)
- PostgreSQL client tools installed (`pg_dump`, `pg_restore`)
- Python 3.10+
- Database connection credentials in `.env.local` or `.env` file

## Installation

No installation required. The backup script is a standalone Python script that uses existing project dependencies.

Ensure PostgreSQL client tools are installed:

**macOS (Homebrew)**:
```bash
brew install postgresql
```

**Ubuntu/Debian**:
```bash
sudo apt-get install postgresql-client
```

## Quick Start

### 1. Configure Environment

Ensure your `.env.local` (development) or `.env` (production) file contains database connection details:

**Development** (`.env.local`):
```bash
ENV_MODE=development
DEV_DB_HOST=127.0.0.1
DEV_DB_PORT=5432
DEV_DB_NAME=project_chat_dev
DEV_DB_USER=dev_user
DEV_DB_PASSWORD=your_password
```

**Production** (`.env`):
```bash
ENV_MODE=production
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=project_chat_prod
DB_USER=prod_user
DB_PASSWORD=your_password
```

### 2. Create Backup

**Development Database**:
```bash
python3 backup_db.py --env dev
```

**Production Database**:
```bash
python3 backup_db.py --env prod
```

**Auto-detect Environment**:
```bash
python3 backup_db.py
```

### 3. Verify Backup

```bash
python3 backup_db.py --verify db/backups/project_chat_dev_2025-01-27T14-30-00Z.dump
```

### 4. List Backups

```bash
python3 backup_db.py --list
```

## Common Use Cases

### Daily Production Backup

Create a backup of production database:

```bash
python3 backup_db.py --env prod --output-dir /backups/production
```

### Development Database Snapshot

Before making experimental changes, create a backup:

```bash
python3 backup_db.py --env dev
```

### Verify All Backups

Check integrity of all backups in directory:

```bash
for backup in db/backups/*.dump; do
    python3 backup_db.py --verify "$backup"
done
```

### Custom Backup Location

Store backups in a specific directory:

```bash
python3 backup_db.py --env prod --output-dir /mnt/backups/project_chat
```

## Backup File Structure

Backups are stored in `db/backups/` by default:

```
db/backups/
├── project_chat_dev_2025-01-27T14-30-00Z.dump
├── project_chat_dev_2025-01-27T14-30-00Z.metadata.json
├── project_chat_prod_2025-01-27T15-00-00Z.dump
└── project_chat_prod_2025-01-27T15-00-00Z.metadata.json
```

Each backup consists of:
- **`.dump` file**: PostgreSQL custom format backup (compressed)
- **`.metadata.json` file**: Backup metadata (timestamp, checksum, table counts, etc.)

## Restoring from Backup

To restore a backup, use PostgreSQL's `pg_restore`:

```bash
# Restore to existing database
pg_restore -h localhost -p 5432 -U your_user -d target_database \
  --clean --if-exists \
  db/backups/project_chat_dev_2025-01-27T14-30-00Z.dump

# Or restore to new database
createdb target_database
pg_restore -h localhost -p 5432 -U your_user -d target_database \
  db/backups/project_chat_dev_2025-01-27T14-30-00Z.dump
```

## Automated Backups

### Cron Job Setup

Add to crontab for daily production backups:

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /path/to/project_chat && python3 backup_db.py --env prod >> /var/log/backup.log 2>&1
```

### Weekly Backup Rotation

Keep last 7 days of backups:

```bash
# Add to crontab
0 3 * * 0 find /path/to/project_chat/db/backups -name "*.dump" -mtime +7 -delete
```

## Troubleshooting

### Error: `pg_dump: command not found`

**Solution**: Install PostgreSQL client tools:
```bash
# macOS
brew install postgresql

# Ubuntu/Debian
sudo apt-get install postgresql-client
```

### Error: `Database connection failed`

**Solution**: Verify database connection settings in `.env.local` or `.env`:
```bash
# Test connection manually
psql -h 127.0.0.1 -p 5432 -U your_user -d your_database
```

### Error: `Insufficient disk space`

**Solution**: Check available disk space and free up space:
```bash
# Check disk space
df -h

# Check backup directory size
du -sh db/backups/
```

### Error: `Permission denied`

**Solution**: Verify write permissions on backup directory:
```bash
# Check permissions
ls -ld db/backups/

# Fix permissions if needed
chmod 755 db/backups/
```

## Best Practices

1. **Regular Backups**: Schedule daily backups for production databases
2. **Verify Backups**: Regularly verify backup integrity with `--verify`
3. **Test Restores**: Periodically test restoring backups to ensure they work
4. **Backup Retention**: Keep multiple backups (last 7 days, last 4 weeks)
5. **Off-site Storage**: Copy backups to remote storage for disaster recovery
6. **Monitor Disk Space**: Ensure backup directory has sufficient space
7. **Document Restoration**: Document restoration procedures for your team

## Next Steps

- Review [contract documentation](./contracts/backup-script.md) for detailed API
- Review [data model](./data-model.md) for backup file structure
- Review [research findings](./research.md) for implementation details

