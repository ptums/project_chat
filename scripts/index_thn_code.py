#!/usr/bin/env python3
"""
Script to index THN repositories for code RAG pipeline.

Usage:
    python3 scripts/index_thn_code.py --repository <path> --name <name> [--production-targets <targets>]
    python3 scripts/index_thn_code.py --all
"""
import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from brain_core.thn_code_indexer import index_repository

def main():
    parser = argparse.ArgumentParser(description="Index THN repositories for code RAG pipeline")
    parser.add_argument(
        "--repository",
        type=str,
        help="Path to repository directory to index"
    )
    parser.add_argument(
        "--name",
        type=str,
        help="Repository name identifier"
    )
    parser.add_argument(
        "--production-targets",
        type=str,
        help="Comma-separated list of production machine names (e.g., 'tumultymedia,tumultymedia2')"
    )
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Only index changed files (incremental update)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Index all repositories in ../repos/ directory"
    )
    args = parser.parse_args()
    
    if args.all:
        # TODO: Implement indexing all repositories
        print("Indexing all repositories not yet implemented")
        return
    
    if not args.repository or not args.name:
        parser.print_help()
        return
    
    production_targets = None
    if args.production_targets:
        production_targets = [t.strip() for t in args.production_targets.split(",")]
    
    try:
        result = index_repository(
            args.repository,
            args.name,
            production_targets=production_targets
        )
        print(f"Indexing complete:")
        print(f"  Files processed: {result.get('files_processed', 0)}")
        print(f"  Chunks created: {result.get('chunks_created', 0)}")
        print(f"  Embeddings generated: {result.get('embeddings_generated', 0)}")
        if result.get('errors'):
            print(f"  Errors: {len(result['errors'])}")
    except Exception as e:
        print(f"Error indexing repository: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

