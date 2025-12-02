#!/usr/bin/env python3
"""
Batch reindex script for conversation_index table.

Finds all conversations that either:
- Have no row in conversation_index, or
- Have conversation_index.version < CURRENT_VERSION

Then indexes each session using Ollama.
"""
import sys
import uuid
import logging
from brain_core.db import get_conn
from brain_core.conversation_indexer import index_session
from brain_core.config import CONVERSATION_INDEX_VERSION, OLLAMA_MODEL
from brain_core.ollama_client import OllamaError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def find_sessions_to_index(current_version: int):
    """
    Find all conversation sessions that need indexing.
    
    Returns:
        List of (session_id, project, title) tuples
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Find conversations missing from index or with outdated version
            cur.execute(
                """
                SELECT c.id, c.project, c.title
                FROM conversations c
                LEFT JOIN conversation_index ci ON c.id = ci.session_id
                WHERE ci.session_id IS NULL
                   OR ci.version < %s
                ORDER BY c.created_at DESC
                """,
                (current_version,),
            )
            rows = cur.fetchall()
    return rows


def main():
    """Main reindex workflow."""
    print(f"Reindexing conversations to version {CONVERSATION_INDEX_VERSION}")
    print(f"Using Ollama model: {OLLAMA_MODEL}")
    print("-" * 60)
    
    # Find sessions to index
    sessions = find_sessions_to_index(CONVERSATION_INDEX_VERSION)
    
    if not sessions:
        print("No sessions need indexing.")
        return
    
    print(f"Found {len(sessions)} session(s) to index.\n")
    
    success_count = 0
    error_count = 0
    
    for idx, (session_id, project, title) in enumerate(sessions, start=1):
        session_id_uuid = uuid.UUID(session_id) if isinstance(session_id, str) else session_id
        print(f"[{idx}/{len(sessions)}] Indexing session {session_id_uuid} ({project}): {title}")
        
        try:
            indexed_data = index_session(session_id_uuid)
            print(f"  ✓ Success: {indexed_data.get('title', 'Untitled')}")
            success_count += 1
        except OllamaError as e:
            print(f"  ✗ Ollama error: {e}")
            error_count += 1
        except ValueError as e:
            print(f"  ✗ Validation error: {e}")
            error_count += 1
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
            error_count += 1
            logger.exception(f"Error indexing session {session_id_uuid}")
        
        print()  # Blank line between sessions
    
    # Summary
    print("-" * 60)
    print(f"Summary: {success_count} succeeded, {error_count} failed")
    
    if error_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()

