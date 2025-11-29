#!/bin/bash
# Run all database migrations in order
# Usage: ./run_all_migrations.sh <database_name>

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <database_name>"
    echo "Example: $0 ongoing_projects"
    exit 1
fi

DB_NAME="$1"
MIGRATIONS_DIR="$(dirname "$0")"

echo "=========================================="
echo "Running all migrations for database: $DB_NAME"
echo "=========================================="
echo ""

# Migration 000: Initial schema
echo "Running migration 000: Initial schema..."
psql -d "$DB_NAME" -f "$MIGRATIONS_DIR/000_initial_schema.sql"
echo "✓ Migration 000 complete"
echo ""

# Migration 001: Conversation index
echo "Running migration 001: Conversation index..."
psql -d "$DB_NAME" -f "$MIGRATIONS_DIR/001_create_conversation_index.sql"
echo "✓ Migration 001 complete"
echo ""

# Check if pgvector extension exists
echo "Checking for pgvector extension..."
if psql -d "$DB_NAME" -tAc "SELECT 1 FROM pg_extension WHERE extname='vector'" | grep -q 1; then
    echo "✓ pgvector extension already installed"
else
    echo "Installing pgvector extension..."
    psql -d "$DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS vector;"
    echo "✓ pgvector extension installed"
fi
echo ""

# Migration 002: DAAS embeddings
echo "Running migration 002: DAAS embeddings..."
psql -d "$DB_NAME" -f "$MIGRATIONS_DIR/002_daas_embeddings.sql"
echo "✓ Migration 002 complete"
echo ""

echo "=========================================="
echo "All migrations complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Import ChatGPT conversations: python3 import_chatgpt_from_zip.py <zip_file>"
echo "  2. Index conversations: python3 setup_prod_conversation_index.py --index-all"
echo "  3. Generate embeddings: python3 backfill_embeddings.py"

