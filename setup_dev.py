#!/usr/bin/env python3
"""
Development environment setup script.
Creates the development database, applies migrations, and loads seed data.
Run this once to set up your development environment.
"""
import os
import sys
import subprocess
import argparse
import psycopg2
from dotenv import load_dotenv

# Load .env.local if it exists (development config)
if os.path.exists(".env.local"):
    load_dotenv(".env.local")
load_dotenv()


def validate_environment():
    """Validate that we're in development mode."""
    env_mode = os.getenv("ENV_MODE", "").lower()
    if env_mode not in ("development", "dev"):
        print("ERROR: Environment validation failed")
        print(f"  ENV_MODE is set to '{env_mode}', but this is a development setup script.")
        print("  Please set ENV_MODE=development in your .env.local file.")
        print("")
        print("For production setup, use: python3 setup_prod.py")
        sys.exit(1)
    
    # Get database config
    db_name = os.getenv("DEV_DB_NAME", "project_chat_dev")
    db_host = os.getenv("DEV_DB_HOST", os.getenv("DB_HOST", "127.0.0.1"))
    db_port = int(os.getenv("DEV_DB_PORT", os.getenv("DB_PORT", "5432")))
    db_user = os.getenv("DEV_DB_USER", os.getenv("DB_USER", "dev_user"))
    db_password = os.getenv("DEV_DB_PASSWORD", os.getenv("DB_PASSWORD", ""))
    
    return {
        'name': db_name,
        'host': db_host,
        'port': db_port,
        'user': db_user,
        'password': db_password
    }


def initialize_database(config, force_recreate=False, verbose=False):
    """Initialize the database using init_db.py."""
    if verbose:
        print("Initializing database...")
    
    # Build command to call init_db.py
    cmd = [sys.executable, "init_db.py", "--env", "dev"]
    if force_recreate:
        cmd.append("--force")
    if verbose:
        cmd.append("--verbose")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=not verbose, text=True)
        if verbose:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("ERROR: Database initialization failed")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        sys.exit(2)


def check_migration_state(config):
    """
    Check which migrations have been applied by checking table/column existence.
    Returns: dict with migration status
    """
    try:
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            dbname=config['name'],
            user=config['user'],
            password=config['password'],
        )
        cur = conn.cursor()
        
        state = {
            'migration_000': False,  # conversations table exists
            'migration_001': False,  # conversation_index table exists
            'migration_002': False,  # embedding column exists
        }
        
        # Check migration 000: conversations table
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'conversations'
            )
        """)
        state['migration_000'] = cur.fetchone()[0]
        
        # Check migration 001: conversation_index table
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'conversation_index'
            )
        """)
        state['migration_001'] = cur.fetchone()[0]
        
        # Check migration 002: embedding column
        if state['migration_001']:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = 'conversation_index'
                    AND column_name = 'embedding'
                )
            """)
            state['migration_002'] = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        return state
    except psycopg2.OperationalError as e:
        print("ERROR: Database connection failed")
        print(f"  {e}")
        print("")
        print("  Troubleshooting steps:")
        print(f"  1. Verify PostgreSQL server is running")
        print(f"  2. Check connection details: {config['host']}:{config['port']}")
        print(f"  3. Verify database '{config['name']}' exists")
        sys.exit(3)
    except Exception as e:
        print("ERROR: Failed to check migration state")
        print(f"  {e}")
        sys.exit(3)


def apply_migrations(config, verbose=False):
    """Apply database migrations using run_all_migrations.sh."""
    if verbose:
        print("Applying migrations...")
    
    migrations_script = "db/migrations/run_all_migrations.sh"
    if not os.path.exists(migrations_script):
        print("ERROR: Migration script not found")
        print(f"  Expected: {migrations_script}")
        sys.exit(3)
    
    # Check current migration state
    state = check_migration_state(config)
    
    # Run migrations
    try:
        result = subprocess.run(
            [migrations_script, config['name']],
            check=True,
            capture_output=not verbose,
            text=True
        )
        
        if verbose:
            print(result.stdout)
        
        # Check final state
        final_state = check_migration_state(config)
        
        applied = []
        if not state['migration_000'] and final_state['migration_000']:
            applied.append("000: Initial schema")
        elif state['migration_000']:
            if verbose:
                print("ℹ Migration 000 already applied (skipped)")
        
        if not state['migration_001'] and final_state['migration_001']:
            applied.append("001: Conversation index")
        elif state['migration_001']:
            if verbose:
                print("ℹ Migration 001 already applied (skipped)")
        
        if not state['migration_002'] and final_state['migration_002']:
            applied.append("002: DAAS embeddings")
        elif state['migration_002']:
            if verbose:
                print("ℹ Migration 002 already applied (skipped)")
        
        for migration in applied:
            print(f"✓ Migration {migration}")
        
        return applied
    except subprocess.CalledProcessError as e:
        print("ERROR: Migration failed")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        print("")
        print("  Troubleshooting steps:")
        print("  1. Check migration files exist in db/migrations/")
        print("  2. Verify database user has ALTER TABLE privileges")
        print("  3. Check for syntax errors in migration files")
        sys.exit(3)


def load_seed_data(config, seed_file, verbose=False):
    """Load seed data from SQL file."""
    if not os.path.exists(seed_file):
        print(f"ERROR: Seed data file not found: {seed_file}")
        sys.exit(4)
    
    if verbose:
        print(f"Loading seed data from {seed_file}...")
    
    try:
        # Read SQL file
        with open(seed_file, 'r') as f:
            sql = f.read()
        
        # Execute SQL
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            dbname=config['name'],
            user=config['user'],
            password=config['password'],
        )
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
        
        if verbose:
            print(f"✓ Seed data loaded from {seed_file}")
        return True
    except psycopg2.Error as e:
        print(f"ERROR: Failed to load seed data from {seed_file}")
        print(f"  {e}")
        print("")
        print("  Troubleshooting steps:")
        print("  1. Verify SQL syntax is correct")
        print("  2. Check that required tables exist (run migrations first)")
        print("  3. Verify database user has INSERT privileges")
        sys.exit(4)
    except Exception as e:
        print(f"ERROR: Unexpected error loading seed data")
        print(f"  {e}")
        sys.exit(4)


def verify_setup(config, skip_seed=False, verbose=False):
    """Verify that setup completed successfully."""
    if verbose:
        print("Verifying setup...")
    
    try:
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            dbname=config['name'],
            user=config['user'],
            password=config['password'],
        )
        cur = conn.cursor()
        
        # Check tables exist
        required_tables = ['conversations', 'messages', 'project_knowledge', 'conversation_index']
        for table in required_tables:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                )
            """, (table,))
            if not cur.fetchone()[0]:
                print(f"ERROR: Required table '{table}' does not exist")
                cur.close()
                conn.close()
                sys.exit(5)
        
        # Check seed data if loaded
        if not skip_seed:
            # Check conversations
            cur.execute("SELECT COUNT(*) FROM conversations")
            conv_count = cur.fetchone()[0]
            if conv_count < 3:
                print(f"WARNING: Expected at least 3 conversations, found {conv_count}")
            
            # Check project knowledge
            cur.execute("SELECT COUNT(*) FROM project_knowledge")
            pk_count = cur.fetchone()[0]
            if pk_count == 0:
                print("WARNING: No project knowledge entries found")
        
        cur.close()
        conn.close()
        
        if verbose:
            print("✓ Setup verification complete")
        return True
    except Exception as e:
        print("ERROR: Setup verification failed")
        print(f"  {e}")
        sys.exit(5)


def main():
    parser = argparse.ArgumentParser(
        description="Set up development environment (database, migrations, seed data)"
    )
    parser.add_argument(
        '--skip-seed',
        action='store_true',
        help="Skip loading development seed data (useful for testing migrations only)"
    )
    parser.add_argument(
        '--force-recreate',
        action='store_true',
        help="Drop and recreate the database if it already exists (destructive)"
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help="Show detailed output for each step"
    )
    
    args = parser.parse_args()
    
    print("========================================")
    print("Development Environment Setup")
    print("========================================")
    print("")
    
    # Step 1: Environment validation
    config = validate_environment()
    print(f"✓ Environment validated (ENV_MODE=development)")
    
    # Step 2: Database initialization
    initialize_database(config, force_recreate=args.force_recreate, verbose=args.verbose)
    print(f"✓ Database initialized: {config['name']}")
    
    # Step 3: Migration application
    applied = apply_migrations(config, verbose=args.verbose)
    if not applied:
        print("ℹ All migrations already applied")
    
    # Step 4: Seed data loading
    # Load project_knowledge first (foundational data for RAG)
    # Then load other seed data (conversations, messages, etc.)
    if not args.skip_seed:
        load_seed_data(config, "db/seeds/project_knowledge_seed.sql", verbose=args.verbose)
        load_seed_data(config, "db/seeds/dev_seed.sql", verbose=args.verbose)
        print("✓ Seed data loaded")
    else:
        print("ℹ Seed data loading skipped (--skip-seed)")
    
    # Step 5: Verification
    verify_setup(config, skip_seed=args.skip_seed, verbose=args.verbose)
    
    print("")
    print("Setup complete! You can now run:")
    print("  python3 chat_cli.py")


if __name__ == "__main__":
    main()

