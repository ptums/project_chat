#!/usr/bin/env python3
"""
Backfill embeddings for existing code chunks in code_index table.

This script processes code chunks that don't have embeddings yet,
generating embeddings in batches to respect OpenAI rate limits.

Usage:
    python3 scripts/backfill_thn_embeddings.py [--repository <name>] [--dry-run]
"""
import argparse
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from brain_core.db import get_conn
from brain_core.embedding_service import generate_embedding
from psycopg2.extras import Json

def find_chunks_needing_embeddings(repository_name: str = None):
    """
    Find code chunks that need embeddings generated.
    
    Args:
        repository_name: Optional repository name to filter by
    
    Returns:
        List of tuples: (chunk_id, chunk_text, chunk_metadata, file_path)
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            if repository_name:
                cur.execute(
                    """
                    SELECT id, chunk_text, chunk_metadata, file_path
                    FROM code_index
                    WHERE embedding IS NULL
                      AND repository_name = %s
                    ORDER BY indexed_at ASC
                    """,
                    (repository_name,)
                )
            else:
                cur.execute(
                    """
                    SELECT id, chunk_text, chunk_metadata, file_path
                    FROM code_index
                    WHERE embedding IS NULL
                    ORDER BY indexed_at ASC
                    """
                )
            return cur.fetchall()

def generate_and_store_embedding(chunk_id, chunk_text, chunk_metadata, file_path):
    """
    Generate embedding for a code chunk and update the database.
    
    Args:
        chunk_id: UUID of the chunk
        chunk_text: Code chunk text
        chunk_metadata: Chunk metadata dict
        file_path: File path for context
    """
    try:
        # Build context for embedding
        context_parts = []
        if file_path:
            context_parts.append(f"File: {file_path}")
        if chunk_metadata:
            if 'function_name' in chunk_metadata:
                context_parts.append(f"Function: {chunk_metadata['function_name']}")
            if 'class_name' in chunk_metadata:
                context_parts.append(f"Class: {chunk_metadata['class_name']}")
        
        context = "\n".join(context_parts)
        if context:
            combined_text = f"{context}\n\n{chunk_text}"
        else:
            combined_text = chunk_text
        
        # Generate embedding
        embedding = generate_embedding(combined_text)
        
        # Convert to string format
        embedding_str = '[' + ','.join(str(x) for x in embedding) + ']'
        
        # Update database
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE code_index
                    SET embedding = %s::vector
                    WHERE id = %s
                    """,
                    (embedding_str, str(chunk_id))
                )
                conn.commit()
        
        return True
    except Exception as e:
        print(f"Error generating embedding for chunk {chunk_id}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Backfill embeddings for THN code chunks")
    parser.add_argument(
        "--repository",
        type=str,
        help="Repository name to filter by (optional)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be processed without generating embeddings"
    )
    
    args = parser.parse_args()
    
    # Find chunks needing embeddings
    chunks = find_chunks_needing_embeddings(args.repository)
    
    if not chunks:
        print("No chunks found needing embeddings.")
        return
    
    print(f"Found {len(chunks)} chunks needing embeddings")
    
    if args.dry_run:
        print("\nDry run - would process:")
        for chunk_id, chunk_text, chunk_metadata, file_path in chunks[:10]:
            print(f"  - {chunk_id}: {file_path} ({len(chunk_text)} chars)")
        if len(chunks) > 10:
            print(f"  ... and {len(chunks) - 10} more")
        return
    
    # Process in batches
    batch_size = 50
    delay_seconds = 1
    processed = 0
    errors = 0
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        print(f"\nProcessing batch {i // batch_size + 1} ({len(batch)} chunks)")
        
        for chunk_id, chunk_text, chunk_metadata, file_path in batch:
            success = generate_and_store_embedding(
                chunk_id,
                chunk_text,
                chunk_metadata,
                file_path
            )
            if success:
                processed += 1
            else:
                errors += 1
        
        # Delay between batches (except for last batch)
        if i + batch_size < len(chunks):
            time.sleep(delay_seconds)
    
    print(f"\nBackfill complete:")
    print(f"  Processed: {processed}")
    print(f"  Errors: {errors}")

if __name__ == "__main__":
    main()

