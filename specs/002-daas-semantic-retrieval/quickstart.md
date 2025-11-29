# Quickstart: DAAS Semantic Dream Retrieval Implementation

## Prerequisites

1. **PostgreSQL with pgvector extension**
   ```bash
   # Install pgvector (varies by OS)
   # macOS: brew install pgvector
   # Ubuntu: apt-get install postgresql-XX-pgvector
   ```

2. **Python dependencies**
   ```bash
   pip install pgvector psycopg2-binary openai python-dotenv
   ```

3. **OpenAI API key** (for embedding generation)
   - Set in `.env`: `OPENAI_API_KEY=sk-...`

## Implementation Steps

### Step 1: Database Schema Migration

```sql
-- Install pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Add embedding column to conversation_index
ALTER TABLE conversation_index 
ADD COLUMN embedding vector(1536);

-- Create vector similarity index (DAAS entries only)
CREATE INDEX idx_conversation_index_embedding 
ON conversation_index 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100)
WHERE project = 'DAAS' AND embedding IS NOT NULL;
```

### Step 2: Create Embedding Service Module

**File**: `brain_core/embedding_service.py`

```python
"""
Embedding generation service using OpenAI API.
"""
from openai import OpenAI
from typing import List, Optional

client = OpenAI()

def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for text using OpenAI.
    
    Args:
        text: Text to embed
        
    Returns:
        List of 1536 float values representing the embedding
    """
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding
```

### Step 3: Create DAAS Retrieval Module

**File**: `brain_core/daas_retrieval.py`

```python
"""
DAAS-specific retrieval logic for single-dream and pattern-based queries.
"""
import re
from typing import List, Dict, Optional, Tuple
from .db import get_conn
from .embedding_service import generate_embedding

def detect_quoted_title(message: str) -> Optional[str]:
    """
    Detect quoted title in user message.
    
    Returns:
        Extracted title if found, None otherwise
    """
    pattern = r'"([^"]+)"'
    matches = re.findall(pattern, message)
    if matches:
        return matches[0].strip()
    return None

def retrieve_single_dream(title: str) -> Optional[Dict]:
    """
    Retrieve single dream by title match.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT session_id, title, summary_short, memory_snippet
                FROM conversation_index
                WHERE project = 'DAAS' 
                  AND title ILIKE %s
                ORDER BY indexed_at DESC
                LIMIT 1
            """, (f'%{title}%',))
            row = cur.fetchone()
            if row:
                return {
                    'session_id': row[0],
                    'title': row[1],
                    'summary_short': row[2],
                    'memory_snippet': row[3]
                }
    return None

def retrieve_pattern_dreams(query: str, top_k: int = 5) -> List[Dict]:
    """
    Retrieve top-k dreams using vector similarity search.
    """
    # Generate query embedding
    query_embedding = generate_embedding(query)
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT session_id, title, summary_short, memory_snippet,
                       1 - (embedding <=> %s::vector) as similarity
                FROM conversation_index
                WHERE project = 'DAAS' 
                  AND embedding IS NOT NULL
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """, (str(query_embedding), str(query_embedding), top_k))
            rows = cur.fetchall()
            
    return [
        {
            'session_id': row[0],
            'title': row[1],
            'summary_short': row[2],
            'memory_snippet': row[3],
            'similarity': float(row[4])
        }
        for row in rows
    ]

def retrieve_daas_context(user_message: str, top_k: int = 5) -> Dict:
    """
    Main retrieval function: routes to single-dream or pattern-based mode.
    
    Returns:
        Dict with 'mode', 'dreams' (list), and 'context' (string)
    """
    quoted_title = detect_quoted_title(user_message)
    
    if quoted_title:
        # Single-dream mode
        dream = retrieve_single_dream(quoted_title)
        if dream:
            return {
                'mode': 'single',
                'dreams': [dream],
                'context': f"Dream: {dream['title']}\n{dream.get('summary_short', '')}\n{dream.get('memory_snippet', '')}"
            }
        else:
            return {
                'mode': 'single',
                'dreams': [],
                'context': f"No dream found matching '{quoted_title}'"
            }
    else:
        # Pattern-based mode
        dreams = retrieve_pattern_dreams(user_message, top_k)
        if dreams:
            context_parts = [f"Relevant dream: {d['title']}\n{d.get('summary_short', '')}\n{d.get('memory_snippet', '')}" 
                           for d in dreams]
            return {
                'mode': 'pattern',
                'dreams': dreams,
                'context': '\n\n---\n\n'.join(context_parts)
            }
        else:
            return {
                'mode': 'pattern',
                'dreams': [],
                'context': "No relevant dreams found for your query."
            }
```

### Step 4: Modify Context Builder

**File**: `brain_core/context_builder.py`

Add DAAS-specific routing at the beginning of `build_project_context()`:

```python
def build_project_context(project: str, user_message: str, ...):
    # DAAS-specific retrieval
    if project == 'DAAS':
        from .daas_retrieval import retrieve_daas_context
        daas_result = retrieve_daas_context(user_message, top_k=5)
        if daas_result['dreams']:
            return {
                'context': daas_result['context'],
                'notes': [d['title'] for d in daas_result['dreams']]
            }
    
    # Existing logic for other projects...
```

### Step 5: Add Embedding Generation to Indexer

**File**: `brain_core/conversation_indexer.py`

Modify `index_session()` to generate and store embedding for DAAS entries:

```python
def index_session(session_id, ...):
    # ... existing indexing logic ...
    
    # Generate embedding for DAAS entries
    if indexed_data['project'] == 'DAAS':
        from .embedding_service import generate_embedding
        from .db import get_conn
        
        # Combine text fields for embedding
        embedding_text = f"{indexed_data['title']} {indexed_data['summary_detailed']} {indexed_data.get('memory_snippet', '')}"
        embedding = generate_embedding(embedding_text)
        
        # Store embedding
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE conversation_index
                    SET embedding = %s::vector
                    WHERE session_id = %s
                """, (str(embedding), str(session_id)))
            conn.commit()
```

### Step 6: Implement Streaming Responses

**File**: `brain_core/chat.py`

Modify `chat_turn()` to support streaming:

```python
def chat_turn(conversation_id, user_text: str, project: str, stream: bool = False):
    # ... existing context building ...
    
    if stream:
        # Streaming mode
        stream_response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            stream=True
        )
        
        full_response = ""
        for chunk in stream_response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                yield content  # Yield chunk for streaming
        
        # Save complete message
        save_message(conversation_id, "assistant", full_response, meta=meta)
        return full_response
    else:
        # Non-streaming mode (existing behavior)
        # ... existing code ...
```

**File**: `chat_cli.py`

Modify main loop to use streaming:

```python
# In main() function, when calling chat_turn:
if hasattr(chat_turn, '__call__'):
    # Check if streaming is supported
    reply = chat_turn(conv_id, user_text, current_project, stream=True)
    
    # Print streaming chunks
    for chunk in reply:
        sys.stdout.write(chunk)
        sys.stdout.flush()
    print()  # Newline after complete
```

### Step 7: Create Backfill Script

**File**: `backfill_embeddings.py`

```python
#!/usr/bin/env python3
"""
Backfill embeddings for existing DAAS conversation_index entries.
"""
import time
from brain_core.db import get_conn
from brain_core.embedding_service import generate_embedding

def backfill_embeddings(batch_size=50, delay=1):
    """Backfill embeddings for DAAS entries missing them."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Find entries needing embeddings
            cur.execute("""
                SELECT session_id, title, summary_detailed, memory_snippet
                FROM conversation_index
                WHERE project = 'DAAS' AND embedding IS NULL
                ORDER BY indexed_at DESC
            """)
            entries = cur.fetchall()
    
    total = len(entries)
    print(f"Found {total} DAAS entries needing embeddings")
    
    processed = 0
    for i in range(0, total, batch_size):
        batch = entries[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1} ({len(batch)} entries)...")
        
        for session_id, title, summary, memory in batch:
            try:
                # Generate embedding
                text = f"{title or ''} {summary or ''} {memory or ''}"
                embedding = generate_embedding(text)
                
                # Store embedding
                with get_conn() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            UPDATE conversation_index
                            SET embedding = %s::vector
                            WHERE session_id = %s
                        """, (str(embedding), str(session_id)))
                    conn.commit()
                
                processed += 1
                print(f"  ✓ {session_id}: {title or 'Untitled'}")
            except Exception as e:
                print(f"  ✗ {session_id}: Error - {e}")
        
        # Delay between batches
        if i + batch_size < total:
            time.sleep(delay)
    
    print(f"\nComplete: {processed}/{total} embeddings generated")

if __name__ == "__main__":
    backfill_embeddings()
```

## Testing

### Test Single-Dream Retrieval
```bash
# In DAAS project
> What does "My Flying Dream" mean from a Jungian perspective?
# Should retrieve only that specific dream
```

### Test Pattern-Based Retrieval
```bash
# In DAAS project
> What patterns do I have with water in my dreams?
# Should retrieve top-k relevant dreams using vector similarity
```

### Test Streaming
```bash
# Send any query and observe progressive text display
> Analyze my recent dreams
# Text should appear incrementally
```

## Configuration

**Environment Variables**:
- `OPENAI_API_KEY`: Required for embedding generation
- `DAAS_VECTOR_TOP_K`: Top-k value for vector search (default: 5)

## Troubleshooting

**pgvector extension not found**:
- Install pgvector for your PostgreSQL version
- Verify: `SELECT * FROM pg_extension WHERE extname = 'vector';`

**Embedding generation fails**:
- Check OpenAI API key is set
- Verify API quota/rate limits
- Check network connectivity

**Vector search returns no results**:
- Verify embeddings exist: `SELECT COUNT(*) FROM conversation_index WHERE project='DAAS' AND embedding IS NOT NULL;`
- Run backfill script if needed
- Check index exists: `\d+ conversation_index` in psql

