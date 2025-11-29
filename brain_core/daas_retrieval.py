"""
DAAS-specific retrieval logic for single-dream and pattern-based queries.

Provides custom retrieval rules for DAAS project:
- Single-dream mode: Quoted title detection and title-based matching
- Pattern-based mode: Vector similarity search using embeddings
"""
import logging
import re
from typing import Dict, List, Optional

from .db import get_conn
from .embedding_service import generate_embedding

logger = logging.getLogger(__name__)


def detect_quoted_title(message: str) -> Optional[str]:
    """
    Detect quoted title in user message using regex pattern.
    
    Looks for text within double quotes like "Title".
    Handles edge cases: malformed quotes, partial titles, very long titles.
    
    Args:
        message: User message text
        
    Returns:
        Extracted title if found, None otherwise
    """
    if not message:
        return None
    
    # Pattern to match text within double quotes
    pattern = r'"([^"]+)"'
    matches = re.findall(pattern, message)
    
    if matches:
        # Take the first match and strip whitespace
        title = matches[0].strip()
        # Validate: not empty and reasonable length
        # Handle very long titles by truncating (still try to match)
        if title:
            if len(title) > 500:
                logger.debug(f"Quoted title very long ({len(title)} chars), truncating for matching")
                title = title[:500]
            logger.info(f"DAAS single-dream mode: detected quoted title '{title[:50]}...'")
            return title
    
    return None


def retrieve_single_dream(title: str) -> Optional[Dict]:
    """
    Retrieve single dream by title match using pattern matching.
    
    Handles edge cases: no matches, multiple matches (uses most recent).
    
    Args:
        title: Dream title to search for (from quoted title detection)
        
    Returns:
        Dict with dream data (session_id, title, summary_short, memory_snippet)
        or None if no match found
    """
    if not title:
        return None
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                # First try exact match
                cur.execute(
                    """
                    SELECT session_id, title, summary_short, memory_snippet
                    FROM conversation_index
                    WHERE project = 'DAAS' 
                      AND title ILIKE %s
                    ORDER BY indexed_at DESC
                    LIMIT 1
                    """,
                    (f'%{title}%',),
                )
                row = cur.fetchone()
                
                if row:
                    result = {
                        'session_id': str(row[0]),
                        'title': row[1],
                        'summary_short': row[2],
                        'memory_snippet': row[3]
                    }
                    logger.info(f"Retrieved single dream: {result['title']}")
                    return result
                
                logger.info(f"No dream found matching title: {title}")
                return None
                
    except Exception as e:
        logger.error(f"Error retrieving single dream: {e}")
        # Don't raise - return None so caller can handle gracefully
        return None


def retrieve_pattern_dreams(query: str, top_k: int = 5) -> List[Dict]:
    """
    Retrieve top-k dreams using vector similarity search.
    
    Generates embedding for the query and performs cosine similarity search
    over stored embeddings for DAAS entries.
    
    Args:
        query: User query text to find similar dreams
        top_k: Number of top results to return (default: 5)
        
    Returns:
        List of dicts with dream data and similarity scores
        Empty list if no matches or embeddings unavailable
    """
    if not query or not query.strip():
        return []
    
    try:
        # Generate query embedding
        logger.info(f"DAAS pattern-based retrieval: generating embedding for query (top_k={top_k})")
        query_embedding = generate_embedding(query)
        
        # Convert embedding list to string format for PostgreSQL
        # pgvector expects format: '[0.1,0.2,0.3,...]'
        embedding_str = '[' + ','.join(str(x) for x in query_embedding) + ']'
        
        with get_conn() as conn:
            with conn.cursor() as cur:
                # Vector similarity search using cosine distance operator (<=>)
                # 1 - distance gives similarity score (higher = more similar)
                cur.execute(
                    """
                    SELECT session_id, title, summary_short, memory_snippet,
                           1 - (embedding <=> %s::vector) as similarity
                    FROM conversation_index
                    WHERE project = 'DAAS' 
                      AND embedding IS NOT NULL
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                    """,
                    (embedding_str, embedding_str, top_k),
                )
                rows = cur.fetchall()
        
        if not rows:
            logger.debug("No dreams found via vector similarity search")
            return []
        
        results = []
        for row in rows:
            results.append({
                'session_id': str(row[0]),
                'title': row[1],
                'summary_short': row[2],
                'memory_snippet': row[3],
                'similarity': float(row[4]) if row[4] is not None else 0.0
            })
        
        logger.info(f"Retrieved {len(results)} dreams via vector similarity search")
        return results
        
    except Exception as e:
        # Handle specific error types
        error_msg = str(e).lower()
        if "vector" in error_msg or "pgvector" in error_msg or "extension" in error_msg:
            logger.error(f"pgvector extension error: {e}. Ensure pgvector is installed and extension is created.")
        elif "embedding" in error_msg and "null" in error_msg:
            logger.warning("No embeddings available for vector search. Run backfill_embeddings.py to generate embeddings.")
        else:
            logger.error(f"Error retrieving pattern dreams: {e}")
        # Return empty list on error (caller can handle fallback)
        return []


def retrieve_daas_context(user_message: str, top_k: int = 5) -> Dict:
    """
    Main retrieval function: routes to single-dream or pattern-based mode.
    
    Never mixes modes - single-dream queries only use that dream's memory.
    
    Args:
        user_message: User's query message
        top_k: Number of top results for pattern-based mode (default: 5)
        
    Returns:
        Dict with:
        - 'mode': 'single' or 'pattern'
        - 'dreams': List of dream dicts
        - 'context': Formatted context string for prompt
    """
    quoted_title = detect_quoted_title(user_message)
    
    if quoted_title:
        # Single-dream mode
        logger.info(f"DAAS single-dream mode: searching for '{quoted_title}'")
        dream = retrieve_single_dream(quoted_title)
        
        if dream:
            context = (
                f"Dream: {dream['title']}\n"
                f"{dream.get('summary_short', '')}\n"
                f"{dream.get('memory_snippet', '')}"
            )
            return {
                'mode': 'single',
                'dreams': [dream],
                'context': context
            }
        else:
            # No match found
            return {
                'mode': 'single',
                'dreams': [],
                'context': f"No dream found matching '{quoted_title}'. Did you mean one of these? (Try searching without quotes for pattern matching.)"
            }
    else:
        # Pattern-based mode
        logger.info(f"DAAS pattern-based mode: vector similarity search (top_k={top_k})")
        dreams = retrieve_pattern_dreams(user_message, top_k)
        
        if dreams:
            context_parts = []
            for dream in dreams:
                parts = []
                if dream.get('title'):
                    parts.append(f"Dream: {dream['title']}")
                if dream.get('summary_short'):
                    parts.append(f"Summary: {dream['summary_short']}")
                if dream.get('memory_snippet'):
                    parts.append(f"Memory: {dream['memory_snippet']}")
                
                if parts:
                    context_parts.append("\n".join(parts))
            
            if context_parts:
                context = "\n\n---\n\n".join(context_parts)
                return {
                    'mode': 'pattern',
                    'dreams': dreams,
                    'context': context
                }
        
        # No relevant dreams found
        return {
            'mode': 'pattern',
            'dreams': [],
            'context': "No relevant dreams found for your query. Try rephrasing or asking about a specific dream using quotes."
        }

