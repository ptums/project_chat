#!/usr/bin/env python3
"""
Backfill embeddings for existing DAAS conversation_index entries.

Generates embeddings for DAAS entries that are missing them.
Processes in batches to respect OpenAI rate limits (3000 req/min).
"""
import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables
if os.path.exists(".env.local"):
    load_dotenv(".env.local")
load_dotenv()

from brain_core.db import get_conn
from brain_core.embedding_service import generate_embedding

BATCH_SIZE = 50
BATCH_DELAY = 1  # seconds between batches


def find_entries_needing_embeddings():
    """Find DAAS entries missing embeddings."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT session_id, title, summary_detailed, memory_snippet
                FROM conversation_index
                WHERE project = 'DAAS' AND embedding IS NULL
                ORDER BY indexed_at DESC
            """)
            return cur.fetchall()


def generate_and_store_embedding(session_id, title, summary_detailed, memory_snippet):
    """Generate embedding for an entry and store it."""
    # Combine text fields for embedding
    embedding_text_parts = []
    if title:
        embedding_text_parts.append(title)
    if summary_detailed:
        embedding_text_parts.append(summary_detailed)
    if memory_snippet:
        embedding_text_parts.append(memory_snippet)
    
    if not embedding_text_parts:
        print(f"  ⚠ {session_id}: No text content, skipping")
        return False
    
    embedding_text = " ".join(embedding_text_parts)
    
    try:
        # Generate embedding
        embedding = generate_embedding(embedding_text)
        
        # Convert to PostgreSQL format
        embedding_str = '[' + ','.join(str(x) for x in embedding) + ']'
        
        # Store in database
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE conversation_index
                    SET embedding = %s::vector
                    WHERE session_id = %s
                """, (embedding_str, str(session_id)))
            conn.commit()
        
        return True
    except Exception as e:
        print(f"  ✗ {session_id}: Error - {e}")
        return False


def main():
    """Main backfill workflow."""
    print("=" * 60)
    print("DAAS Embeddings Backfill")
    print("=" * 60)
    print()
    
    # Find entries needing embeddings
    entries = find_entries_needing_embeddings()
    total = len(entries)
    
    if total == 0:
        print("No DAAS entries need embeddings. All up to date!")
        return
    
    print(f"Found {total} DAAS entries needing embeddings")
    print(f"Processing in batches of {BATCH_SIZE} with {BATCH_DELAY}s delay")
    print()
    
    processed = 0
    failed = 0
    
    for i in range(0, total, BATCH_SIZE):
        batch = entries[i:i+BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
        
        print(f"Batch {batch_num}/{total_batches} ({len(batch)} entries)...")
        
        for session_id, title, summary_detailed, memory_snippet in batch:
            title_display = title or "Untitled"
            if len(title_display) > 50:
                title_display = title_display[:47] + "..."
            
            if generate_and_store_embedding(session_id, title, summary_detailed, memory_snippet):
                print(f"  ✓ {title_display}")
                processed += 1
            else:
                failed += 1
        
        # Delay between batches (except after last batch)
        if i + BATCH_SIZE < total:
            print(f"  Waiting {BATCH_DELAY}s before next batch...")
            time.sleep(BATCH_DELAY)
        print()
    
    # Summary
    print("=" * 60)
    print(f"Backfill complete: {processed} succeeded, {failed} failed")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBackfill interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        sys.exit(1)

