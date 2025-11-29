#!/usr/bin/env python3
"""
Fix invalid project values in conversations table.

This script finds conversations with invalid project values and either:
1. Fixes them to 'general' (default)
2. Or deletes them if they have no messages

Usage:
    # Dry run (show what would be fixed)
    python3 fix_invalid_projects.py --dry-run
    
    # Fix invalid projects
    python3 fix_invalid_projects.py --fix
    
    # Delete conversations with invalid projects and no messages
    python3 fix_invalid_projects.py --delete-empty
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

VALID_PROJECTS = ['THN', 'DAAS', 'FF', '700B', 'general']


def find_invalid_projects():
    """Find conversations with invalid project values."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.title, c.project,
                       COUNT(m.id) as message_count
                FROM conversations c
                LEFT JOIN messages m ON c.id = m.conversation_id
                WHERE c.project NOT IN %s
                GROUP BY c.id, c.title, c.project
                ORDER BY c.created_at DESC
            """, (tuple(VALID_PROJECTS),))
            return cur.fetchall()


def find_conversations_without_messages():
    """Find conversations that have no messages."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.title, c.project
                FROM conversations c
                LEFT JOIN messages m ON c.id = m.conversation_id
                WHERE m.id IS NULL
                ORDER BY c.created_at DESC
            """)
            return cur.fetchall()


def fix_invalid_projects(dry_run=False):
    """Fix invalid project values by setting them to 'general'."""
    invalid = find_invalid_projects()
    
    if not invalid:
        print("✓ No conversations with invalid project values found")
        return 0
    
    print(f"Found {len(invalid)} conversations with invalid project values:")
    for row in invalid:
        session_id, title, project, msg_count = row
        title_display = title[:50] if title else "Untitled"
        print(f"  - {session_id} [{project}]: {title_display} ({msg_count} messages)")
    
    if dry_run:
        print("\n[DRY RUN] Would fix these by setting project='general'")
        return 0
    
    print("\nFixing invalid projects...")
    fixed_count = 0
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            for row in invalid:
                session_id, title, project, msg_count = row
                cur.execute("""
                    UPDATE conversations
                    SET project = 'general'
                    WHERE id = %s
                """, (str(session_id),))
                fixed_count += 1
                print(f"  ✓ Fixed {session_id}: '{project}' -> 'general'")
        conn.commit()
    
    print(f"\n✓ Fixed {fixed_count} conversations")
    return fixed_count


def delete_empty_conversations(dry_run=False):
    """Delete conversations that have no messages."""
    empty = find_conversations_without_messages()
    
    if not empty:
        print("✓ No empty conversations found")
        return 0
    
    print(f"Found {len(empty)} conversations without messages:")
    for row in empty[:10]:
        session_id, title, project = row
        title_display = title[:50] if title else "Untitled"
        print(f"  - {session_id} [{project}]: {title_display}")
    if len(empty) > 10:
        print(f"  ... and {len(empty) - 10} more")
    
    if dry_run:
        print("\n[DRY RUN] Would delete these conversations")
        return 0
    
    print("\nDeleting empty conversations...")
    deleted_count = 0
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            for row in empty:
                session_id, title, project = row
                cur.execute("DELETE FROM conversations WHERE id = %s", (str(session_id),))
                deleted_count += 1
                print(f"  ✓ Deleted {session_id}")
        conn.commit()
    
    print(f"\n✓ Deleted {deleted_count} empty conversations")
    return deleted_count


def main():
    parser = argparse.ArgumentParser(
        description="Fix invalid project values in conversations table"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be fixed without making changes'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Fix invalid projects by setting them to "general"'
    )
    parser.add_argument(
        '--delete-empty',
        action='store_true',
        help='Delete conversations that have no messages'
    )
    
    args = parser.parse_args()
    
    if not any([args.fix, args.delete_empty]):
        parser.print_help()
        sys.exit(1)
    
    if args.fix:
        fix_invalid_projects(dry_run=args.dry_run)
    
    if args.delete_empty:
        delete_empty_conversations(dry_run=args.dry_run)


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

