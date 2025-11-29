#!/usr/bin/env python3
"""
Import ChatGPT conversations from a zip file.

This script:
1. Extracts the zip file containing ChatGPT export
2. Finds conversations.json in the extracted files
3. Imports all conversations into the database
4. Handles project inference and conversation/message creation

Usage:
    python3 import_chatgpt_from_zip.py <path_to_zip_file>
    
Example:
    python3 import_chatgpt_from_zip.py chatgpt_export.zip
"""
import os
import sys
import json
import uuid
import zipfile
import tempfile
import shutil
from datetime import datetime, timezone
from pathlib import Path

import psycopg2
from psycopg2.extras import Json

# Import database config from brain_core to ensure consistency
from brain_core.config import DB_CONFIG


def get_conn():
    """Get database connection."""
    try:
        return psycopg2.connect(**DB_CONFIG)
    except psycopg2.OperationalError as e:
        if "does not exist" in str(e):
            print(f"\n❌ Error: Database '{DB_CONFIG['dbname']}' does not exist!")
            print(f"\nTo create the database, run:")
            print(f"  createdb {DB_CONFIG['dbname']}")
            print(f"\nOr set DB_NAME environment variable to an existing database:")
            print(f"  export DB_NAME=your_existing_database")
            print(f"\nCurrent database config:")
            print(f"  Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
            print(f"  Database: {DB_CONFIG['dbname']}")
            print(f"  User: {DB_CONFIG['user']}")
        raise


def infer_project(title: str, all_text: str) -> str:
    """Heuristic to tag old conversations as THN / DAAS / FF / 700B / general."""
    blob = ((title or "") + " " + (all_text or "")).lower()

    if "700b" in blob:
        return "700B"
    if "thn" in blob or "tumulty home network" in blob:
        return "THN"
    if "daas" in blob or "dream to action alignment system" in blob or "dream" in blob:
        return "DAAS"
    if "ff" in blob or "financial freedom" in blob:
        return "FF"

    return "general"


def upsert_conversation(conv_id: uuid.UUID, title: str, project: str, created_at: datetime):
    """Upsert a conversation into the database."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO conversations (id, title, project, created_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    project = EXCLUDED.project,
                    created_at = LEAST(conversations.created_at, EXCLUDED.created_at)
                """,
                (str(conv_id), title, project, created_at),
            )
        conn.commit()


def insert_message(conv_id: uuid.UUID, role: str, content: str, created_at: datetime):
    """Insert a message into the database."""
    msg_id = uuid.uuid4()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO messages (id, conversation_id, role, content, created_at, meta_json)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (str(msg_id), str(conv_id), role, content, created_at, Json({})),
            )
        conn.commit()
    return msg_id


def parse_message_content(msg: dict) -> str:
    """
    Handle typical ChatGPT export content structures.
    Supports various export formats from OpenAI.
    """
    content = msg.get("content") or {}

    # Old format: { "content": { "parts": ["..."] } }
    parts = content.get("parts")
    if isinstance(parts, list) and parts:
        return "\n".join(str(p) for p in parts if p)

    # Newer multi-part structures
    if isinstance(content, dict) and "content_type" in content:
        parts = content.get("parts")
        if isinstance(parts, list) and parts:
            return "\n".join(str(p) for p in parts if p)

    # Direct string content
    if isinstance(content, str):
        return content

    # Fallback: try to stringify
    return json.dumps(content)


def import_conversation(conv: dict, dry_run: bool = False):
    """
    Import a single conversation object from conversations.json
    into our Postgres schema.
    """
    title = conv.get("title") or "Untitled"
    
    # Use OpenAI's create_time if present, else now
    raw_ctime = conv.get("create_time")
    if raw_ctime is not None:
        try:
            created_at = datetime.fromtimestamp(raw_ctime, tz=timezone.utc)
        except Exception:
            created_at = datetime.now(tz=timezone.utc)
    else:
        created_at = datetime.now(tz=timezone.utc)

    mapping = conv.get("mapping") or {}
    if not mapping:
        if not dry_run:
            print(f"⚠️  Skipping conversation '{title}': No mapping data")
        return

    # Gather all messages from mapping, flatten, and sort by time
    msgs = []
    all_text_concat = []

    for node_id, node in mapping.items():
        msg = node.get("message")
        if not msg:
            continue

        author = (msg.get("author") or {}).get("role") or ""
        if author not in ("user", "assistant", "system"):
            # skip tool / other internal roles
            continue

        content_str = parse_message_content(msg)
        all_text_concat.append(content_str)

        ts = msg.get("create_time") or conv.get("create_time") or 0
        try:
            ts_dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        except Exception:
            ts_dt = created_at

        msgs.append(
            {
                "role": author,
                "content": content_str,
                "created_at": ts_dt,
            }
        )

    if not msgs:
        if not dry_run:
            print(f"⚠️  Skipping conversation '{title}': No messages found")
        return

    # Infer project tag from title + concatenated text
    project = infer_project(title, "\n".join(all_text_concat))

    # Use a stable UUID derived from conversation id if present, else random
    conv_id_str = conv.get("id") or str(uuid.uuid4())
    try:
        # Try to parse as UUID if it looks like one
        if len(conv_id_str) == 36:
            conv_id = uuid.UUID(conv_id_str)
        else:
            # Generate deterministic UUID from string
            conv_id = uuid.uuid5(uuid.NAMESPACE_DNS, conv_id_str)
    except Exception:
        conv_id = uuid.uuid4()

    if dry_run:
        first_ts = min(m["created_at"] for m in msgs)
        print(f"  Would import: ID={conv_id} | Title={title!r} | Project={project} | Messages={len(msgs)} | Created={first_ts}")
        return

    # Upsert conversation
    first_ts = min(m["created_at"] for m in msgs)
    upsert_conversation(conv_id, title, project, first_ts)

    # Sort messages chronologically and insert
    msgs.sort(key=lambda m: m["created_at"])
    for m in msgs:
        insert_message(conv_id, m["role"], m["content"], m["created_at"])

    print(f"✓ Imported: ID={conv_id} | Title={title!r} | Project={project} | Messages={len(msgs)}")


def find_conversations_json(extracted_dir: Path) -> Path:
    """Find conversations.json in the extracted directory."""
    # Try common locations
    possible_paths = [
        extracted_dir / "conversations.json",
        extracted_dir / "chatgpt_export" / "conversations.json",
        extracted_dir / "conversations" / "conversations.json",
    ]
    
    # Also search recursively
    for path in extracted_dir.rglob("conversations.json"):
        return path
    
    # Check direct paths
    for path in possible_paths:
        if path.exists():
            return path
    
    return None


def extract_zip(zip_path: Path) -> Path:
    """Extract zip file to temporary directory."""
    temp_dir = tempfile.mkdtemp(prefix="chatgpt_import_")
    print(f"Extracting {zip_path} to temporary directory...")
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    
    return Path(temp_dir)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 import_chatgpt_from_zip.py <path_to_zip_file> [--dry-run]")
        print("\nExample:")
        print("  python3 import_chatgpt_from_zip.py chatgpt_export.zip")
        print("  python3 import_chatgpt_from_zip.py chatgpt_export.zip --dry-run")
        print("\nEnvironment variables:")
        print("  DB_NAME or DEV_DB_NAME - Database name (depends on ENV_MODE)")
        print("  DB_HOST - Database host (default: 127.0.0.1)")
        print("  DB_PORT - Database port (default: 5432)")
        print("  DB_USER - Database user (default: thn_user)")
        print("  DB_PASSWORD - Database password")
        sys.exit(1)
    
    zip_path = Path(sys.argv[1])
    dry_run = "--dry-run" in sys.argv
    
    # Show database config being used
    print("Database configuration:")
    print(f"  Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"  Database: {DB_CONFIG['dbname']}")
    print(f"  User: {DB_CONFIG['user']}")
    print()
    
    # Validate database connection before starting
    if not dry_run:
        try:
            test_conn = get_conn()
            test_conn.close()
            print("✓ Database connection verified\n")
        except psycopg2.OperationalError as e:
            print(f"\n❌ Database connection failed: {e}")
            print(f"\nCurrent database config:")
            print(f"  Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
            print(f"  Database: {DB_CONFIG['dbname']}")
            print(f"  User: {DB_CONFIG['user']}")
            print(f"\nTo create the database, run:")
            print(f"  createdb {DB_CONFIG['dbname']}")
            print(f"\nOr check your .env.local or .env file for correct database settings.")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Unexpected error connecting to database: {e}")
            sys.exit(1)
    
    if not zip_path.exists():
        print(f"❌ Error: Zip file not found: {zip_path}")
        sys.exit(1)
    
    if not zipfile.is_zipfile(zip_path):
        print(f"❌ Error: Not a valid zip file: {zip_path}")
        sys.exit(1)
    
    # Extract zip file
    temp_dir = None
    try:
        temp_dir = extract_zip(zip_path)
        extracted_path = Path(temp_dir)
        
        # Find conversations.json
        conversations_json = find_conversations_json(extracted_path)
        
        if not conversations_json:
            print(f"❌ Error: conversations.json not found in {zip_path}")
            print("   Expected structure: zip_file.zip -> conversations.json")
            print("   Or: zip_file.zip -> chatgpt_export/conversations.json")
            sys.exit(1)
        
        print(f"✓ Found conversations.json at: {conversations_json}")
        
        # Load and parse conversations
        print("Loading conversations...")
        with open(conversations_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        conversations = data if isinstance(data, list) else data.get("conversations", [])
        print(f"✓ Found {len(conversations)} conversations in export.\n")
        
        if dry_run:
            print("DRY RUN MODE - No data will be imported\n")
        
        # Import each conversation
        success_count = 0
        error_count = 0
        
        for i, conv in enumerate(conversations, 1):
            try:
                print(f"[{i}/{len(conversations)}] ", end="")
                import_conversation(conv, dry_run=dry_run)
                success_count += 1
            except Exception as e:
                title = conv.get("title", "Untitled")
                print(f"❌ Failed to import conversation {title!r}: {e}")
                error_count += 1
                if not dry_run:
                    import traceback
                    traceback.print_exc()
        
        # Summary
        print("\n" + "="*60)
        if dry_run:
            print(f"DRY RUN COMPLETE")
            print(f"  Would import: {success_count} conversations")
        else:
            print(f"IMPORT COMPLETE")
            print(f"  ✓ Successfully imported: {success_count} conversations")
            if error_count > 0:
                print(f"  ✗ Failed: {error_count} conversations")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        # Clean up temporary directory
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"\nCleaned up temporary directory")


if __name__ == "__main__":
    main()

