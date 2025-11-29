#!/usr/bin/env python3
"""
Database initialization script.
Creates a PostgreSQL database based on configuration from .env.local or .env files.
Supports both development and production environments.
"""
import os
import sys
import argparse
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv


def load_environment():
    """Load environment variables from .env.local (preferred) or .env."""
    if os.path.exists(".env.local"):
        load_dotenv(".env.local")
        config_source = ".env.local"
    else:
        load_dotenv()
        config_source = ".env"
    return config_source


def detect_environment(args, config_source):
    """
    Detect environment from --env flag, ENV_MODE, or database name variables.
    Returns: ('dev' or 'prod', config_source)
    """
    # If --env flag is provided, use it
    if args.env:
        if args.env.lower() in ('dev', 'development'):
            return 'dev', config_source
        elif args.env.lower() in ('prod', 'production'):
            return 'prod', config_source
        else:
            print(f"ERROR: Invalid --env value: {args.env}")
            print("  Must be 'dev' or 'prod'")
            sys.exit(1)
    
    # Otherwise, detect from environment variables
    env_mode = os.getenv("ENV_MODE", "").lower()
    if env_mode in ("development", "dev"):
        return 'dev', config_source
    elif env_mode in ("production", "prod"):
        return 'prod', config_source
    
    # Fallback: check for database name variables
    if os.getenv("DEV_DB_NAME"):
        return 'dev', config_source
    elif os.getenv("DB_NAME"):
        return 'prod', config_source
    
    # Default to development if ambiguous
    return 'dev', config_source


def load_database_config(env_type):
    """
    Load database configuration based on environment type.
    Returns: dict with host, port, dbname, user, password
    """
    if env_type == 'dev':
        config = {
            'host': os.getenv("DEV_DB_HOST", os.getenv("DB_HOST", "127.0.0.1")),
            'port': int(os.getenv("DEV_DB_PORT", os.getenv("DB_PORT", "5432"))),
            'dbname': os.getenv("DEV_DB_NAME"),  # Required
            'user': os.getenv("DEV_DB_USER", os.getenv("DB_USER", "dev_user")),
            'password': os.getenv("DEV_DB_PASSWORD", os.getenv("DB_PASSWORD", "")),
        }
        if not config['dbname']:
            print("ERROR: Database initialization failed")
            print("  Database name not found in environment variables.")
            print("")
            print("  For development, set DEV_DB_NAME in .env.local")
            print("  For production, set DB_NAME in .env")
            print("")
            print("  Example (.env.local):")
            print("    ENV_MODE=development")
            print("    DEV_DB_NAME=my_dev_database")
            print("    DEV_DB_USER=my_user")
            print("    DEV_DB_PASSWORD=my_password")
            sys.exit(2)
    else:  # prod
        config = {
            'host': os.getenv("DB_HOST", "127.0.0.1"),
            'port': int(os.getenv("DB_PORT", "5432")),
            'dbname': os.getenv("DB_NAME"),  # Required
            'user': os.getenv("DB_USER"),  # Required
            'password': os.getenv("DB_PASSWORD", ""),  # Required
        }
        if not config['dbname']:
            print("ERROR: Database initialization failed")
            print("  Database name not found in environment variables.")
            print("")
            print("  For production, set DB_NAME in .env")
            print("")
            print("  Example (.env):")
            print("    ENV_MODE=production")
            print("    DB_NAME=my_production_database")
            print("    DB_USER=my_user")
            print("    DB_PASSWORD=my_password")
            sys.exit(2)
        if not config['user']:
            print("ERROR: Database initialization failed")
            print("  Database user not found in environment variables.")
            print("")
            print("  For production, set DB_USER in .env")
            sys.exit(2)
    
    return config


def test_connection(config, verbose=False):
    """
    Test connection to PostgreSQL server.
    Returns: connection object or None
    """
    try:
        if verbose:
            print(f"Testing connection to PostgreSQL at {config['host']}:{config['port']}...")
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            dbname="postgres",  # Connect to default postgres DB
            user=config['user'],
            password=config['password'],
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        if verbose:
            print("✓ Database connection verified")
        return conn
    except psycopg2.OperationalError as e:
        print("ERROR: Database connection failed")
        print(f"  {e}")
        print("")
        print("  Troubleshooting steps:")
        print("  1. Verify PostgreSQL server is running")
        print(f"  2. Check connection details: {config['host']}:{config['port']}")
        print(f"  3. Verify user '{config['user']}' has CREATE DATABASE privileges")
        print("  4. Check firewall/network connectivity")
        sys.exit(3)
    except Exception as e:
        print("ERROR: Unexpected error during connection test")
        print(f"  {e}")
        sys.exit(3)


def check_database_exists(conn, dbname):
    """Check if database exists."""
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM pg_database WHERE datname = %s",
        (dbname,)
    )
    exists = cur.fetchone()
    cur.close()
    return exists is not None


def create_database(conn, dbname, force=False, verbose=False):
    """
    Create database if it doesn't exist.
    If force=True and database exists, drop and recreate it.
    """
    exists = check_database_exists(conn, dbname)
    
    if exists and force:
        # Warn user about data loss
        print(f"⚠ WARNING: This will delete all data in {dbname}")
        response = input("Continue? (y/N): ").strip().lower()
        if response != 'y':
            print("Aborted.")
            sys.exit(0)
        
        # Disconnect all users first
        if verbose:
            print(f"Dropping existing database '{dbname}'...")
        cur = conn.cursor()
        try:
            # Terminate all connections to the database
            cur.execute(
                """
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = %s AND pid <> pg_backend_pid()
                """,
                (dbname,)
            )
            cur.execute(f'DROP DATABASE "{dbname}"')
            if verbose:
                print(f"✓ Database dropped")
        except Exception as e:
            print(f"ERROR: Failed to drop database")
            print(f"  {e}")
            cur.close()
            sys.exit(4)
        cur.close()
        exists = False
    
    if exists:
        print(f"ℹ Database already exists: {dbname}")
        print("")
        print("No action needed. Database is ready.")
        return False  # Database already existed
    
    # Create database
    if verbose:
        print(f"Creating database '{dbname}'...")
    cur = conn.cursor()
    try:
        cur.execute(f'CREATE DATABASE "{dbname}"')
        if verbose:
            print(f"✓ Database created")
        print(f"✓ Database created: {dbname}")
        cur.close()
        return True  # Database was created
    except psycopg2.errors.InsufficientPrivilege as e:
        print("ERROR: Permission denied")
        print(f"  {e}")
        print("")
        print("  The database user does not have CREATE DATABASE privileges.")
        print("  Contact your database administrator or use a user with superuser privileges.")
        cur.close()
        sys.exit(5)
    except Exception as e:
        print("ERROR: Database creation failed")
        print(f"  {e}")
        cur.close()
        sys.exit(4)


def main():
    parser = argparse.ArgumentParser(
        description="Initialize PostgreSQL database from .env/.env.local configuration"
    )
    parser.add_argument(
        '--env',
        choices=['dev', 'prod', 'development', 'production'],
        help="Specify environment explicitly (dev or prod). If not provided, auto-detects from ENV_MODE or database name variables."
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help="Drop and recreate the database if it already exists (destructive)"
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help="Show detailed output for each step"
    )
    
    args = parser.parse_args()
    
    # Load environment
    config_source = load_environment()
    
    # Detect environment
    env_type, config_source = detect_environment(args, config_source)
    env_label = 'development' if env_type == 'dev' else 'production'
    
    if args.verbose:
        print("========================================")
        print("Database Initialization")
        print("========================================")
        print("")
    
    print(f"✓ Environment detected: {env_label}")
    print(f"✓ Configuration loaded from {config_source}")
    
    # Load database configuration
    config = load_database_config(env_type)
    
    # Test connection
    conn = test_connection(config, args.verbose)
    
    # Create database
    created = create_database(conn, config['dbname'], force=args.force, verbose=args.verbose)
    
    conn.close()
    
    if created:
        print("")
        print("Initialization complete!")
    else:
        # Already printed "No action needed" message
        pass


if __name__ == "__main__":
    main()

