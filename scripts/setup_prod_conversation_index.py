#!/usr/bin/env python3
"""
Production setup script for conversation_index table.

This script helps set up the conversation_index table on production
and optionally indexes existing conversations.

Usage:
    # Just verify the table exists
    python3 setup_prod_conversation_index.py --verify

    # Index all existing conversations
    python3 setup_prod_conversation_index.py --index-all

    # Index specific conversation
    python3 setup_prod_conversation_index.py --index <session_id>
"""
import os
import sys
import argparse
from dotenv import load_dotenv

# Load environment variables
if os.path.exists(".env.local"):
    load_dotenv(".env.local")
load_dotenv()

from brain_core.db import get_conn
from brain_core.conversation_indexer import index_session
from brain_core.ollama_client import check_ollama_health, OllamaError


def verify_table_exists():
    """Verify conversation_index table exists and has correct structure."""
    print("Verifying conversation_index table...")
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Check table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'conversation_index'
                )
            """)
            table_exists = cur.fetchone()[0]
            
            if not table_exists:
                print("❌ conversation_index table does not exist!")
                print("   Run: psql -d your_database -f db/migrations/001_create_conversation_index.sql")
                return False
            
            print("✓ conversation_index table exists")
            
            # Check required columns
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'conversation_index'
                ORDER BY ordinal_position
            """)
            columns = [row[0] for row in cur.fetchall()]
            
            required_columns = [
                'session_id', 'project', 'title', 'tags', 'summary_short',
                'summary_detailed', 'key_entities', 'key_topics', 'memory_snippet',
                'ollama_model', 'version', 'indexed_at'
            ]
            
            missing = [col for col in required_columns if col not in columns]
            if missing:
                print(f"❌ Missing columns: {', '.join(missing)}")
                return False
            
            print(f"✓ All required columns present ({len(columns)} total)")
            
            # Check if embedding column exists (from migration 002)
            if 'embedding' in columns:
                print("✓ Embedding column exists (DAAS feature ready)")
            else:
                print("⚠ Embedding column not found (run migration 002 to add it)")
            
            # Count existing entries
            cur.execute("SELECT COUNT(*) FROM conversation_index")
            count = cur.fetchone()[0]
            print(f"✓ Found {count} indexed conversations")
            
            return True


def find_unindexed_conversations():
    """Find conversations that haven't been indexed yet.
    
    Filters out:
    - Conversations with invalid project values (not in allowed list)
    - Conversations without any messages
    """
    print("\nFinding unindexed conversations...")
    
    valid_projects = ['THN', 'DAAS', 'FF', '700B', 'general']
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Find unindexed conversations with valid projects and messages
            cur.execute("""
                SELECT c.id, c.title, c.project, c.created_at,
                       COUNT(m.id) as message_count
                FROM conversations c
                LEFT JOIN conversation_index ci ON c.id = ci.session_id
                LEFT JOIN messages m ON c.id = m.conversation_id
                WHERE ci.session_id IS NULL
                GROUP BY c.id, c.title, c.project, c.created_at
                HAVING COUNT(m.id) > 0
                ORDER BY c.created_at DESC
            """)
            rows = cur.fetchall()
    
    # Filter for valid projects
    valid_rows = []
    invalid_rows = []
    no_message_rows = []
    
    for row in rows:
        session_id, title, project, created_at, message_count = row
        if project not in valid_projects:
            invalid_rows.append((session_id, title, project))
        elif message_count == 0:
            no_message_rows.append((session_id, title))
        else:
            valid_rows.append(row)
    
    if invalid_rows:
        print(f"\n⚠ Skipping {len(invalid_rows)} conversations with invalid project values:")
        for session_id, title, project in invalid_rows[:5]:  # Show first 5
            title_display = title[:50] if title else "Untitled"
            print(f"  - {session_id} [{project}]: {title_display}")
        if len(invalid_rows) > 5:
            print(f"  ... and {len(invalid_rows) - 5} more")
        print(f"  (Valid projects: {', '.join(valid_projects)})")
    
    if no_message_rows:
        print(f"\n⚠ Skipping {len(no_message_rows)} conversations without messages:")
        for session_id, title in no_message_rows[:5]:  # Show first 5
            title_display = title[:50] if title else "Untitled"
            print(f"  - {session_id}: {title_display}")
        if len(no_message_rows) > 5:
            print(f"  ... and {len(no_message_rows) - 5} more")
    
    if not valid_rows:
        if rows:
            print("\n✓ All valid conversations are already indexed")
        else:
            print("✓ All conversations are already indexed")
        return []
    
    print(f"\n✓ Found {len(valid_rows)} valid unindexed conversations:")
    for row in valid_rows[:10]:  # Show first 10
        session_id, title, project, created_at, message_count = row
        title_display = title[:50] if title else "Untitled"
        print(f"  - {session_id} [{project}]: {title_display}")
    if len(valid_rows) > 10:
        print(f"  ... and {len(valid_rows) - 10} more")
    
    return [str(row[0]) for row in valid_rows]


def index_all_conversations(dry_run=False):
    """Index all conversations that haven't been indexed yet."""
    unindexed = find_unindexed_conversations()
    
    if not unindexed:
        return
    
    if dry_run:
        print(f"\n[DRY RUN] Would index {len(unindexed)} conversations")
        return
    
    # Check Ollama is available
    try:
        check_ollama_health()
        print("✓ Ollama is available")
    except OllamaError as e:
        print(f"❌ Ollama is not available: {e}")
        print("   Make sure Ollama is running and OLLAMA_BASE_URL is correct")
        return
    
    print(f"\nIndexing {len(unindexed)} conversations...")
    print("This may take a while depending on the number of conversations.\n")
    
    success_count = 0
    error_count = 0
    
    for i, session_id in enumerate(unindexed, 1):
        print(f"[{i}/{len(unindexed)}] Indexing {session_id}...", end=" ", flush=True)
        try:
            # Validate conversation before indexing
            with get_conn() as conn:
                with conn.cursor() as cur:
                    # Check project is valid
                    cur.execute("""
                        SELECT project, 
                               (SELECT COUNT(*) FROM messages WHERE conversation_id = %s) as msg_count
                        FROM conversations
                        WHERE id = %s
                    """, (session_id, session_id))
                    row = cur.fetchone()
                    if not row:
                        print(f"✗ Conversation not found")
                        error_count += 1
                        continue
                    project, msg_count = row
                    valid_projects = ['THN', 'DAAS', 'FF', '700B', 'general']
                    if project not in valid_projects:
                        print(f"✗ Invalid project '{project}' (skipping)")
                        error_count += 1
                        continue
                    if msg_count == 0:
                        print(f"✗ No messages found (skipping)")
                        error_count += 1
                        continue
            
            result = index_session(session_id)
            title = result.get('title', 'Untitled')
            print(f"✓ {title[:40]}")
            success_count += 1
        except ValueError as e:
            # Handle "No messages found" and other validation errors
            error_msg = str(e)
            if "No messages found" in error_msg:
                print(f"✗ No messages found")
            else:
                print(f"✗ Validation error: {e}")
            error_count += 1
        except Exception as e:
            print(f"✗ Error: {e}")
            error_count += 1
    
    print(f"\n✓ Indexed {success_count} conversations")
    if error_count > 0:
        print(f"✗ Failed to index {error_count} conversations")


def index_single_conversation(session_id: str):
    """Index a single conversation by session_id."""
    print(f"Indexing conversation {session_id}...")
    
    # Check Ollama is available
    try:
        check_ollama_health()
        print("✓ Ollama is available")
    except OllamaError as e:
        print(f"❌ Ollama is not available: {e}")
        print("   Make sure Ollama is running and OLLAMA_BASE_URL is correct")
        return
    
    try:
        result = index_session(session_id)
        print(f"✓ Successfully indexed: {result.get('title', 'Untitled')}")
        print(f"  Project: {result.get('project')}")
        print(f"  Summary: {result.get('summary_short', 'N/A')[:100]}")
    except Exception as e:
        print(f"✗ Error indexing conversation: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Production setup for conversation_index table"
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verify conversation_index table exists and has correct structure'
    )
    parser.add_argument(
        '--index-all',
        action='store_true',
        help='Index all conversations that haven\'t been indexed yet'
    )
    parser.add_argument(
        '--index',
        metavar='SESSION_ID',
        help='Index a specific conversation by session_id'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be indexed without actually indexing (use with --index-all)'
    )
    
    args = parser.parse_args()
    
    if not any([args.verify, args.index_all, args.index]):
        parser.print_help()
        sys.exit(1)
    
    if args.verify:
        success = verify_table_exists()
        sys.exit(0 if success else 1)
    
    if args.index:
        index_single_conversation(args.index)
    
    if args.index_all:
        index_all_conversations(dry_run=args.dry_run)


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

