#!/usr/bin/env python3
"""
Database backup script for project_chat.

Creates PostgreSQL database backups for both development and production environments.
Supports automatic environment detection, backup verification, and metadata generation.

Usage:
    python3 backup_db.py [--env ENV] [--output-dir DIR] [--verify FILE] [--list] [--help]

Examples:
    # Backup development database
    python3 backup_db.py --env dev

    # Backup production database
    python3 backup_db.py --env prod

    # Verify a backup file
    python3 backup_db.py --verify db/backups/project_chat_dev_2025-01-27T14-30-00Z.dump

    # List all backups
    python3 backup_db.py --list
"""
import os
import sys
import argparse
import subprocess
import shutil
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


# Load environment variables
def load_environment():
    """Load environment variables from .env.local (preferred) or .env."""
    if os.path.exists(".env.local"):
        load_dotenv(".env.local")
        return ".env.local"
    else:
        load_dotenv()
        return ".env"


def detect_environment(args):
    """
    Detect environment from --env flag, ENV_MODE, or database name variables.
    Returns: ('dev' or 'prod', config_source)
    """
    # If --env flag is provided, use it
    if args.env and args.env != 'auto':
        env_lower = args.env.lower()
        if env_lower in ('dev', 'development'):
            return 'dev'
        elif env_lower in ('prod', 'production'):
            return 'prod'
        else:
            print(f"ERROR: Invalid --env value: {args.env}")
            print("  Must be 'dev', 'prod', or 'auto'")
            sys.exit(1)
    
    # Otherwise, detect from environment variables
    env_mode = os.getenv("ENV_MODE", "").lower()
    if env_mode in ("development", "dev"):
        return 'dev'
    elif env_mode in ("production", "prod"):
        return 'prod'
    
    # Fallback: check for database name variables
    if os.getenv("DEV_DB_NAME"):
        return 'dev'
    elif os.getenv("DB_NAME"):
        return 'prod'
    
    # Default to development if ambiguous
    return 'dev'


def load_database_config(env_type):
    """
    Load database configuration based on environment type.
    Returns: dict with host, port, dbname, user, password
    """
    if env_type == 'dev':
        config = {
            'host': os.getenv("DEV_DB_HOST", os.getenv("DB_HOST", "127.0.0.1")),
            'port': int(os.getenv("DEV_DB_PORT", os.getenv("DB_PORT", "5432"))),
            'dbname': os.getenv("DEV_DB_NAME"),
            'user': os.getenv("DEV_DB_USER", os.getenv("DB_USER", "dev_user")),
            'password': os.getenv("DEV_DB_PASSWORD", os.getenv("DB_PASSWORD", "")),
        }
        if not config['dbname']:
            print("ERROR: Database configuration failed")
            print("  Database name not found in environment variables.")
            print("")
            print("  For development, set DEV_DB_NAME in .env.local")
            print("  For production, set DB_NAME in .env")
            sys.exit(2)
    else:  # prod
        config = {
            'host': os.getenv("DB_HOST", "127.0.0.1"),
            'port': int(os.getenv("DB_PORT", "5432")),
            'dbname': os.getenv("DB_NAME"),
            'user': os.getenv("DB_USER", "thn_user"),
            'password': os.getenv("DB_PASSWORD", ""),
        }
        if not config['dbname']:
            print("ERROR: Database configuration failed")
            print("  Database name not found in environment variables.")
            print("")
            print("  For production, set DB_NAME in .env")
            sys.exit(2)
    
    return config


def validate_backup_directory(output_dir):
    """Validate backup directory exists, is writable, and create if missing."""
    backup_path = Path(output_dir)
    
    # Create directory if it doesn't exist
    if not backup_path.exists():
        try:
            backup_path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created backup directory: {backup_path}")
        except OSError as e:
            print(f"ERROR: Failed to create backup directory: {e}")
            sys.exit(5)
    
    # Check if directory is writable
    if not os.access(backup_path, os.W_OK):
        print(f"ERROR: Backup directory is not writable: {backup_path}")
        sys.exit(5)
    
    return backup_path


def generate_timestamp():
    """Generate ISO 8601 timestamp for backup filename."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")


def generate_backup_filename(database_name, environment, timestamp):
    """Generate backup filename using format: {database_name}_{environment}_{timestamp}.dump"""
    return f"{database_name}_{environment}_{timestamp}.dump"


def check_disk_space(required_bytes, backup_dir):
    """Check if sufficient disk space is available."""
    stat = shutil.disk_usage(backup_dir)
    available_bytes = stat.free
    
    if available_bytes < required_bytes:
        required_gb = required_bytes / (1024 ** 3)
        available_gb = available_bytes / (1024 ** 3)
        print(f"ERROR: Insufficient disk space")
        print(f"  Required: {required_gb:.2f} GB")
        print(f"  Available: {available_gb:.2f} GB")
        print(f"  Location: {backup_dir}")
        sys.exit(5)
    
    return True


def check_pg_dump_available():
    """Check if pg_dump is installed and available in PATH."""
    if not shutil.which("pg_dump"):
        print("ERROR: pg_dump not found")
        print("  PostgreSQL client tools must be installed.")
        print("")
        print("  macOS: brew install postgresql")
        print("  Ubuntu/Debian: sudo apt-get install postgresql-client")
        sys.exit(6)
    return True


def check_pg_restore_available():
    """Check if pg_restore is installed and available in PATH."""
    if not shutil.which("pg_restore"):
        print("ERROR: pg_restore not found")
        print("  PostgreSQL client tools must be installed.")
        print("")
        print("  macOS: brew install postgresql")
        print("  Ubuntu/Debian: sudo apt-get install postgresql-client")
        sys.exit(6)
    return True


def main():
    """Main entry point for backup script."""
    parser = argparse.ArgumentParser(
        description="Backup PostgreSQL databases for project_chat",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Backup development database
  python3 backup_db.py --env dev

  # Backup production database
  python3 backup_db.py --env prod

  # Verify a backup file
  python3 backup_db.py --verify db/backups/project_chat_dev_2025-01-27T14-30-00Z.dump

  # List all backups
  python3 backup_db.py --list

  # Custom backup location
  python3 backup_db.py --env prod --output-dir /backups/production
        """
    )
    
    parser.add_argument(
        '--env',
        choices=['dev', 'prod', 'auto'],
        default='auto',
        help='Target environment: dev, prod, or auto (default: auto)'
    )
    parser.add_argument(
        '--output-dir',
        default='db/backups',
        help='Backup storage directory (default: db/backups)'
    )
    parser.add_argument(
        '--verify',
        metavar='FILE',
        help='Verify integrity of an existing backup file'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all backup files in backup directory'
    )
    
    args = parser.parse_args()
    
    # Handle --verify flag
    if args.verify:
        verify_backup(args.verify)
        return
    
    # Handle --list flag
    if args.list:
        list_backups(args.output_dir)
        return
    
    # Load environment and detect target environment
    config_source = load_environment()
    env_type = detect_environment(args)
    
    # Load database configuration
    db_config = load_database_config(env_type)
    
    # Validate backup directory
    backup_dir = validate_backup_directory(args.output_dir)
    
    # Check PostgreSQL tools are available
    check_pg_dump_available()
    check_pg_restore_available()
    
    # Production environment validation
    if env_type == 'prod':
        if db_config['host'] in ('localhost', '127.0.0.1'):
            print("⚠ WARNING: Connecting to localhost for production backup")
            print("  This may indicate a misconfiguration.")
            print("  Verify DB_HOST is set correctly in your .env file")
    
    # Validate database connection
    try:
        test_conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            dbname=db_config['dbname'],
            user=db_config['user'],
            password=db_config['password'],
        )
        test_conn.close()
        print(f"✓ Database connection validated")
    except psycopg2.OperationalError as e:
        print(f"ERROR: Database connection failed")
        print(f"  {e}")
        print("")
        print("  Troubleshooting:")
        print(f"  1. Verify database '{db_config['dbname']}' exists")
        print(f"  2. Check connection parameters in {config_source}")
        print(f"  3. Test connection: psql -h {db_config['host']} -p {db_config['port']} -U {db_config['user']} -d {db_config['dbname']}")
        sys.exit(3)
    
    # Generate backup filename
    timestamp = generate_timestamp()
    backup_filename = generate_backup_filename(db_config['dbname'], env_type, timestamp)
    backup_path = backup_dir / backup_filename
    metadata_path = backup_dir / f"{backup_filename.replace('.dump', '')}.metadata.json"
    
    # Estimate required disk space (2x database size, minimum 100MB)
    # We'll check after backup, but estimate based on typical compression ratio
    # For now, we'll do a basic check - estimate 500MB minimum
    estimated_space = 500 * 1024 * 1024  # 500MB minimum estimate
    try:
        check_disk_space(estimated_space, str(backup_dir))
    except SystemExit:
        # check_disk_space already printed error and exited
        raise
    
    print(f"Starting backup of {db_config['dbname']} ({env_type})...")
    print(f"Backup file: {backup_path}")
    
    # Create backup using pg_dump
    try:
        pg_dump_cmd = [
            'pg_dump',
            '-h', db_config['host'],
            '-p', str(db_config['port']),
            '-U', db_config['user'],
            '-d', db_config['dbname'],
            '-Fc',  # Custom format
            '-Z', '6',  # Compression level 6
            '--no-owner',  # Don't include ownership commands
            '--no-acl',  # Don't include ACL commands
            '-f', str(backup_path),
        ]
        
        # Set PGPASSWORD environment variable for password
        env = os.environ.copy()
        if db_config['password']:
            env['PGPASSWORD'] = db_config['password']
        
        print("Running pg_dump...")
        result = subprocess.run(
            pg_dump_cmd,
            env=env,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            # Clean up partial backup file
            if backup_path.exists():
                backup_path.unlink()
            
            print(f"ERROR: pg_dump failed")
            print(f"  Exit code: {result.returncode}")
            if result.stderr:
                print(f"  Error: {result.stderr}")
            sys.exit(7)
        
        print("✓ Backup file created")
        
    except subprocess.CalledProcessError as e:
        # Clean up partial backup file
        if backup_path.exists():
            backup_path.unlink()
        
        print(f"ERROR: pg_dump execution failed")
        print(f"  {e}")
        sys.exit(7)
    except Exception as e:
        # Clean up partial backup file
        if backup_path.exists():
            backup_path.unlink()
        
        print(f"ERROR: Unexpected error during backup")
        print(f"  {e}")
        sys.exit(7)
    
    # Calculate SHA256 checksum
    print("Calculating checksum...")
    sha256_hash = hashlib.sha256()
    with open(backup_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256_hash.update(chunk)
    checksum = sha256_hash.hexdigest()
    
    # Get backup file size
    backup_size = backup_path.stat().st_size
    
    # Query database for metadata
    print("Querying database metadata...")
    try:
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            dbname=db_config['dbname'],
            user=db_config['user'],
            password=db_config['password'],
        )
        
        with conn.cursor() as cur:
            # Get PostgreSQL version
            cur.execute("SELECT version()")
            postgresql_version = cur.fetchone()[0]
            
            # Get table counts
            table_counts = {}
            tables = ['conversations', 'messages', 'project_knowledge', 'conversation_index']
            for table in tables:
                try:
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cur.fetchone()[0]
                    table_counts[table] = count
                except psycopg2.Error:
                    # Table might not exist, skip it
                    pass
        
        conn.close()
    except Exception as e:
        print(f"⚠ Warning: Failed to query database metadata: {e}")
        postgresql_version = "unknown"
        table_counts = {}
    
    # Get pg_dump version
    try:
        result = subprocess.run(
            ['pg_dump', '--version'],
            capture_output=True,
            text=True,
            check=True
        )
        pg_dump_version = result.stdout.strip()
    except Exception:
        pg_dump_version = "unknown"
    
    # Create metadata file
    # Use ISO 8601 format for timestamp (with colons and Z)
    iso_timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    metadata = {
        "backup_timestamp": iso_timestamp,
        "environment": env_type,
        "database_name": db_config['dbname'],
        "backup_file": backup_filename,
        "backup_size_bytes": backup_size,
        "checksum_sha256": checksum,
        "table_counts": table_counts,
        "pg_dump_version": pg_dump_version,
        "postgresql_version": postgresql_version,
    }
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("✓ Metadata file created")
    
    # Verify backup integrity
    print("Verifying backup integrity...")
    try:
        result = subprocess.run(
            ['pg_restore', '--list', str(backup_path)],
            capture_output=True,
            text=True,
            check=True
        )
        print("✓ Integrity check passed")
        verified = True
    except subprocess.CalledProcessError:
        print("⚠ Warning: Integrity check failed (backup file may be corrupted)")
        verified = False
    except Exception as e:
        print(f"⚠ Warning: Could not verify integrity: {e}")
        verified = False
    
    # Display success summary
    print("")
    print("=" * 60)
    print("✓ Backup created successfully")
    print("=" * 60)
    print(f"Backup File: {backup_path}")
    print(f"Metadata:    {metadata_path}")
    print(f"Size:        {backup_size / (1024*1024):.2f} MB")
    print(f"Environment: {env_type}")
    print(f"Database:    {db_config['dbname']}")
    if table_counts:
        table_info = ", ".join(f"{count} {table}" for table, count in table_counts.items())
        print(f"Tables:      {len(table_counts)} ({table_info})")
    print(f"Checksum:    {checksum[:16]}...")
    print(f"Verified:    {'✓' if verified else '✗'}")
    print("=" * 60)


def verify_backup(backup_file_path):
    """Verify integrity of a backup file."""
    backup_path = Path(backup_file_path)
    
    if not backup_path.exists():
        print(f"ERROR: Backup file not found: {backup_path}")
        sys.exit(1)
    
    # Find corresponding metadata file
    metadata_path = backup_path.parent / f"{backup_path.stem}.metadata.json"
    
    if not metadata_path.exists():
        print(f"ERROR: Metadata file not found: {metadata_path}")
        print("  Cannot verify backup without metadata file")
        sys.exit(1)
    
    # Load metadata
    try:
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid metadata file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to read metadata file: {e}")
        sys.exit(1)
    
    print(f"Verifying backup: {backup_path.name}")
    print("")
    
    # Verify checksum
    print("Checking checksum...")
    sha256_hash = hashlib.sha256()
    with open(backup_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256_hash.update(chunk)
    current_checksum = sha256_hash.hexdigest()
    stored_checksum = metadata.get('checksum_sha256', '')
    
    if current_checksum != stored_checksum:
        print("✗ Checksum mismatch")
        print(f"  Stored:   {stored_checksum[:16]}...")
        print(f"  Current:  {current_checksum[:16]}...")
        print("  Backup file may be corrupted or modified")
        sys.exit(8)
    else:
        print("✓ Checksum match")
    
    # Verify structure
    print("Verifying backup structure...")
    try:
        result = subprocess.run(
            ['pg_restore', '--list', str(backup_path)],
            capture_output=True,
            text=True,
            check=True
        )
        print("✓ Structure valid (pg_restore --list succeeded)")
        structure_valid = True
    except subprocess.CalledProcessError as e:
        print("✗ Structure validation failed")
        if e.stderr:
            print(f"  Error: {e.stderr}")
        structure_valid = False
        sys.exit(8)
    except Exception as e:
        print(f"✗ Structure validation error: {e}")
        structure_valid = False
        sys.exit(8)
    
    # Display verification summary
    print("")
    print("=" * 60)
    print("✓ Backup verification passed")
    print("=" * 60)
    print(f"File:        {backup_path}")
    print(f"Checksum:    ✓ Match ({current_checksum[:16]}...)")
    print(f"Structure:   ✓ Valid")
    print(f"Size:        {backup_path.stat().st_size / (1024*1024):.2f} MB")
    print(f"Timestamp:   {metadata.get('backup_timestamp', 'unknown')}")
    print(f"Environment: {metadata.get('environment', 'unknown')}")
    print(f"Database:    {metadata.get('database_name', 'unknown')}")
    print("=" * 60)


def list_backups(backup_dir):
    """List all backup files in backup directory."""
    backup_path = Path(backup_dir)
    
    if not backup_path.exists():
        print(f"ERROR: Backup directory not found: {backup_path}")
        sys.exit(1)
    
    # Find all .dump files
    dump_files = sorted(backup_path.glob("*.dump"), key=lambda p: p.stat().st_mtime, reverse=True)
    
    if not dump_files:
        print(f"No backup files found in {backup_path}")
        return
    
    print(f"Backup Files ({backup_path}):")
    print("")
    print(f"{'Timestamp':<20} {'Environment':<12} {'Database':<25} {'Size':<12} {'Status'}")
    print("-" * 80)
    
    for dump_file in dump_files:
        # Try to load metadata
        metadata_path = dump_file.parent / f"{dump_file.stem}.metadata.json"
        
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                timestamp = metadata.get('backup_timestamp', 'unknown')
                # Format timestamp for display (just date/time part)
                if 'T' in timestamp:
                    timestamp = timestamp.split('T')[0] + ' ' + timestamp.split('T')[1].split('.')[0].replace('Z', '')
                
                environment = metadata.get('environment', 'unknown')
                database = metadata.get('database_name', 'unknown')
                size_mb = dump_file.stat().st_size / (1024 * 1024)
                
                # Quick verification check
                try:
                    subprocess.run(
                        ['pg_restore', '--list', str(dump_file)],
                        capture_output=True,
                        check=True
                    )
                    status = "✓ Verified"
                except:
                    status = "⚠ Unverified"
                
                print(f"{timestamp:<20} {environment:<12} {database:<25} {size_mb:>10.2f} MB  {status}")
            except Exception:
                # Metadata file exists but couldn't be read
                size_mb = dump_file.stat().st_size / (1024 * 1024)
                print(f"{'unknown':<20} {'unknown':<12} {dump_file.name:<25} {size_mb:>10.2f} MB  ⚠ No metadata")
        else:
            # No metadata file
            size_mb = dump_file.stat().st_size / (1024 * 1024)
            print(f"{'unknown':<20} {'unknown':<12} {dump_file.name:<25} {size_mb:>10.2f} MB  ⚠ No metadata")
    
    print("")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

