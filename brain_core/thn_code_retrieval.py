"""
THN code retrieval module for semantic code search.

Provides functions to:
- Retrieve code chunks using vector similarity search
- Filter by repository, language, production targets
- Format code context for LLM prompts
"""
import logging
from typing import Dict, List, Optional, Any

from .db import get_conn
from .embedding_service import generate_embedding

logger = logging.getLogger(__name__)


def retrieve_thn_code(
    query: str,
    top_k: int = 5,
    repository_filter: Optional[List[str]] = None,
    production_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve relevant code chunks for a query using vector similarity search.
    
    Args:
        query: User query text
        top_k: Number of top results to return (default: 5)
        repository_filter: Optional list of repository names to filter by
        production_filter: Optional production machine name to filter by (e.g., "tumultymedia")
    
    Returns:
        List of code chunks with similarity scores
    """
    """
    Retrieve relevant code chunks for a query using vector similarity search.
    
    Args:
        query: User query text
        top_k: Number of top results to return (default: 5)
        repository_filter: Optional list of repository names to filter by
        production_filter: Optional production machine name to filter by
    
    Returns:
        List of code chunks with similarity scores
    """
    if not query or not query.strip():
        return []
    
    try:
        # Generate query embedding
        logger.info(f"THN code retrieval: generating embedding for query (top_k={top_k})")
        query_embedding = generate_embedding(query)
        
        # Convert embedding list to string format for PostgreSQL
        embedding_str = '[' + ','.join(str(x) for x in query_embedding) + ']'
        
        # Build SQL query with filters
        where_clauses = ["embedding IS NOT NULL"]
        params = [embedding_str, embedding_str, top_k]
        param_index = 3
        
        if repository_filter:
            placeholders = ','.join(['%s'] * len(repository_filter))
            where_clauses.append(f"repository_name IN ({placeholders})")
            params.extend(repository_filter)
            param_index += len(repository_filter)
        
        if production_filter:
            where_clauses.append("%s = ANY(production_targets)")
            # Insert production_filter before top_k in params
            # params structure: [embedding_str, embedding_str, ...filters..., top_k]
            # We need to insert before the last element (top_k)
            params.insert(-1, production_filter)
        
        where_clause = " AND ".join(where_clauses)
        
        with get_conn() as conn:
            with conn.cursor() as cur:
                # Vector similarity search using cosine distance operator (<=>)
                sql = f"""
                    SELECT id, repository_name, file_path, language, chunk_text,
                           chunk_metadata, production_targets,
                           1 - (embedding <=> %s::vector) as similarity
                    FROM code_index
                    WHERE {where_clause}
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                """
                cur.execute(sql, params)
                rows = cur.fetchall()
        
        if not rows:
            logger.debug("No code chunks found via vector similarity search")
            return []
        
        results = []
        for row in rows:
            results.append({
                'id': str(row[0]),
                'repository_name': row[1],
                'file_path': row[2],
                'language': row[3],
                'chunk_text': row[4],
                'chunk_metadata': row[5] if row[5] else {},
                'production_targets': row[6] if row[6] else [],
                'similarity': float(row[7]) if row[7] is not None else 0.0
            })
        
        # Log production filter if used
        if production_filter:
            logger.info(f"Retrieved {len(results)} code chunks for production target: {production_filter}")
        else:
            logger.info(f"Retrieved {len(results)} code chunks via vector similarity search")
        return results
        
    except Exception as e:
        error_msg = str(e).lower()
        if "vector" in error_msg or "pgvector" in error_msg or "extension" in error_msg:
            logger.error(f"pgvector extension error: {e}. Ensure pgvector is installed and extension is created.")
        elif "embedding" in error_msg and "null" in error_msg:
            logger.warning("No embeddings available for vector search. Run index_thn_code.py to generate embeddings.")
        else:
            logger.error(f"Error retrieving THN code: {e}")
        return []


def retrieve_code_by_file(
    file_path: str,
    repository_name: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve all code chunks from a specific file.
    
    Args:
        file_path: File path pattern (can use wildcards with ILIKE)
        repository_name: Optional repository name to filter by
    
    Returns:
        List of code chunks from matching files
    """
    if not file_path:
        return []
    
    try:
        where_clauses = ["file_path ILIKE %s"]
        params = [f'%{file_path}%']
        
        if repository_name:
            where_clauses.append("repository_name = %s")
            params.append(repository_name)
        
        where_clause = " AND ".join(where_clauses)
        
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT id, repository_name, file_path, language, chunk_text,
                           chunk_metadata, production_targets
                    FROM code_index
                    WHERE {where_clause}
                    ORDER BY file_path, indexed_at
                    """,
                    params
                )
                rows = cur.fetchall()
        
        results = []
        for row in rows:
            results.append({
                'id': str(row[0]),
                'repository_name': row[1],
                'file_path': row[2],
                'language': row[3],
                'chunk_text': row[4],
                'chunk_metadata': row[5] if row[5] else {},
                'production_targets': row[6] if row[6] else []
            })
        
        logger.info(f"Retrieved {len(results)} code chunks from file pattern: {file_path}")
        return results
        
    except Exception as e:
        logger.error(f"Error retrieving code by file: {e}")
        return []


def get_thn_code_context(user_message: str, top_k: int = 5) -> str:
    """
    Main retrieval function that formats code chunks as context for LLM prompt.
    
    Args:
        user_message: User's query message
        top_k: Number of code chunks to retrieve (default: 5)
    
    Returns:
        Formatted context string combining retrieved code chunks
    """
    try:
        # Retrieve relevant code chunks
        chunks = retrieve_thn_code(user_message, top_k=top_k)
        
        if not chunks:
            return ""
        
        # Format chunks for context
        context_parts = []
        for chunk in chunks:
            parts = []
            
            # Add file path
            parts.append(f"File: {chunk['file_path']}")
            
            # Add function/class name if available
            metadata = chunk.get('chunk_metadata', {})
            if 'function_name' in metadata:
                parts.append(f"Function: {metadata['function_name']}")
            if 'class_name' in metadata:
                parts.append(f"Class: {metadata['class_name']}")
            
            # Add code chunk
            parts.append(f"Code:\n{chunk['chunk_text']}")
            
            # Add production targets if available
            if chunk.get('production_targets'):
                parts.append(f"Production machines: {', '.join(chunk['production_targets'])}")
            
            context_parts.append("\n".join(parts))
        
        context = "\n\n---\n\n".join(context_parts)
        logger.debug(f"Generated code context with {len(chunks)} chunks")
        return context
        
    except Exception as e:
        logger.error(f"Error generating THN code context: {e}")
        return ""


def build_thn_context(user_message: str, conversation_context: Optional[str] = None) -> str:
    """
    Build context string for THN conversations including code retrieval.
    
    Args:
        user_message: User's current message
        conversation_context: Optional existing conversation context
    
    Returns:
        Combined context string with code snippets and conversation context
    """
    try:
        # Get code context
        code_context = get_thn_code_context(user_message, top_k=5)
        
        # Combine with conversation context if provided
        context_parts = []
        if code_context:
            context_parts.append(code_context)
        if conversation_context:
            context_parts.append(conversation_context)
        
        return "\n\n---\n\n".join(context_parts) if context_parts else ""
        
    except Exception as e:
        logger.error(f"Error building THN context: {e}")
        return conversation_context or ""


def identify_code_patterns(code_chunks: List[Dict[str, Any]]) -> List[str]:
    """
    Identify code patterns from retrieved chunks for learning opportunities.
    
    Args:
        code_chunks: List of code chunks with metadata
    
    Returns:
        List of identified patterns (e.g., "async functions", "error handling", "configuration management")
    """
    patterns = []
    
    # Analyze chunks for common patterns
    languages = set()
    has_async = False
    has_error_handling = False
    has_config = False
    
    for chunk in code_chunks:
        languages.add(chunk.get('language', ''))
        metadata = chunk.get('chunk_metadata', {})
        
        if metadata.get('is_async'):
            has_async = True
        
        chunk_text = chunk.get('chunk_text', '').lower()
        if 'try' in chunk_text and 'except' in chunk_text:
            has_error_handling = True
        if 'config' in chunk_text or 'yaml' in chunk_text or 'json' in chunk_text:
            has_config = True
    
    if has_async:
        patterns.append("async/await patterns")
    if has_error_handling:
        patterns.append("error handling patterns")
    if has_config:
        patterns.append("configuration management")
    if 'python' in languages:
        patterns.append("Python best practices")
    if 'bash' in languages:
        patterns.append("shell scripting patterns")
    
    return patterns

