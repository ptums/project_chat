"""
Conversation indexer module for organizing and storing conversation metadata.
Uses Ollama to generate structured summaries, tags, and memory snippets.
"""
import json
import logging
import uuid
from typing import List, Dict, Any, Optional

from psycopg2.extras import Json as PsycopgJson

from .config import OLLAMA_MODEL, CONVERSATION_INDEX_VERSION, OLLAMA_BASE_URL, OLLAMA_TIMEOUT
from .db import get_conn
from .ollama_client import generate_with_ollama, OllamaError, check_ollama_health

logger = logging.getLogger(__name__)


def build_transcript(messages: List[Dict[str, str]]) -> str:
    """
    Build a plain text transcript from message list.
    
    Args:
        messages: List of dicts with 'role' and 'content' keys
    
    Returns:
        Formatted transcript string with "role: content" lines
    """
    lines = []
    for msg in messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        lines.append(f"{role}: {content}")
    
    return "\n".join(lines)


def extract_json_from_text(text: str) -> str:
    """
    Extract JSON object from text that may contain explanatory text.
    
    Looks for the first '{' and finds the matching closing '}' to extract
    the JSON object, handling nested objects properly. Also removes JSON comments.
    
    Args:
        text: Text that may contain JSON mixed with other text
    
    Returns:
        Extracted JSON string with comments removed
    
    Raises:
        ValueError: If no valid JSON object is found
    """
    text = text.strip()
    
    # Remove markdown code blocks if present
    if text.startswith("```"):
        lines = text.split("\n")
        if len(lines) > 2:
            text = "\n".join(lines[1:-1])
    if text.startswith("```json"):
        lines = text.split("\n")
        if len(lines) > 2:
            text = "\n".join(lines[1:-1])
    
    # Find the first '{' character
    start_idx = text.find("{")
    if start_idx == -1:
        raise ValueError("No JSON object found in response (no opening brace)")
    
    # Find the matching closing '}' by counting braces
    brace_count = 0
    end_idx = start_idx
    
    for i in range(start_idx, len(text)):
        if text[i] == "{":
            brace_count += 1
        elif text[i] == "}":
            brace_count -= 1
            if brace_count == 0:
                end_idx = i
                break
    
    if brace_count != 0:
        raise ValueError("No complete JSON object found (unmatched braces)")
    
    # Extract the JSON portion
    json_text = text[start_idx:end_idx + 1]
    
    # Remove JSON comments (both // and /* */ style)
    # This handles cases where Ollama adds comments like: "project": "DAAS", // comment
    lines = json_text.split("\n")
    cleaned_lines = []
    in_string = False
    escape_next = False
    
    for line in lines:
        cleaned_line = []
        i = 0
        while i < len(line):
            char = line[i]
            
            # Track string boundaries (handle escaped quotes)
            if escape_next:
                cleaned_line.append(char)
                escape_next = False
                i += 1
                continue
            
            if char == "\\":
                cleaned_line.append(char)
                escape_next = True
                i += 1
                continue
            
            if char == '"':
                in_string = not in_string
                cleaned_line.append(char)
                i += 1
                continue
            
            # If we're inside a string, keep everything
            if in_string:
                cleaned_line.append(char)
                i += 1
                continue
            
            # Outside strings, check for comments
            # Single-line comment //
            if char == "/" and i + 1 < len(line) and line[i + 1] == "/":
                # Found // comment, skip rest of line
                break
            
            # Multi-line comment /*
            if char == "/" and i + 1 < len(line) and line[i + 1] == "*":
                # Skip until */
                i += 2
                while i < len(line) - 1:
                    if line[i] == "*" and line[i + 1] == "/":
                        i += 2
                        break
                    i += 1
                continue
            
            cleaned_line.append(char)
            i += 1
        
        cleaned_line_str = "".join(cleaned_line).rstrip()
        if cleaned_line_str:  # Only add non-empty lines
            cleaned_lines.append(cleaned_line_str)
    
    json_text = "\n".join(cleaned_lines)
    return json_text.strip()


def build_index_prompt(transcript: str) -> str:
    """
    Build the prompt for Ollama to organize a conversation.
    
    Args:
        transcript: Full conversation transcript from build_transcript()
    
    Returns:
        Prompt string instructing Ollama to return structured JSON
    """
    prompt = f"""You are a conversation organizer. Analyze the following conversation and extract structured information.

Conversation transcript:
{transcript}

Please return a JSON object with the following structure:
{{
  "title": "A short, descriptive title for this conversation (max 100 characters)",
  "project": "One of: THN, DAAS, FF, 700B, or general",
  "tags": ["tag1", "tag2", "tag3"],
  "summary_short": "A 1-2 sentence summary of the conversation",
  "summary_detailed": "A multi-paragraph detailed summary covering key points, decisions, and context",
  "key_entities": {{
    "people": ["person1", "person2"],
    "domains": ["domain1", "domain2"],
    "assets": ["asset1", "asset2"]
  }},
  "key_topics": ["topic1", "topic2", "topic3"],
  "memory_snippet": "A concise memory blurb (2-3 sentences) that would help future conversations understand the context and decisions made here"
}}

Return ONLY valid JSON, no additional text or markdown formatting.
"""
    return prompt


def index_session(
    session_id: uuid.UUID | str,
    model: str = None,
    version: int = None,
    override_project: str = None,
    preserve_project: bool = False,
) -> Dict[str, Any]:
    """
    Index a conversation session using Ollama.
    
    Loads all messages for the session, builds a transcript, sends to Ollama
    for organization, parses the response, and upserts into conversation_index.
    
    Args:
        session_id: UUID of the conversation session
        model: Ollama model to use (defaults to OLLAMA_MODEL from config)
        version: Index version number (defaults to CONVERSATION_INDEX_VERSION)
    
    Returns:
        Dict with indexed data (title, project, tags, etc.)
    
    Raises:
        OllamaError: If Ollama API call fails
        ValueError: If JSON parsing fails or required fields are missing
    """
    if model is None:
        model = OLLAMA_MODEL
    if version is None:
        version = CONVERSATION_INDEX_VERSION
    
    # Convert session_id to UUID if string
    if isinstance(session_id, str):
        session_id = uuid.UUID(session_id)
    
    logger.info(f"Indexing session {session_id} with model {model}")
    
    # Load all messages for this session
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Get conversation project
            cur.execute(
                """
                SELECT project, title
                FROM conversations
                WHERE id = %s
                """,
                (str(session_id),),
            )
            conv_row = cur.fetchone()
            if not conv_row:
                raise ValueError(f"Conversation {session_id} not found")
            project, conv_title = conv_row
            # Normalize project to ensure it matches expected format
            from .chat import normalize_project_tag
            project = normalize_project_tag(project)
            
            # If override_project is provided and conversation is "general", use override
            project_was_overridden = False
            if override_project and project == "general":
                override_project = normalize_project_tag(override_project)
                if override_project != "general":
                    logger.info(f"Overriding project from 'general' to '{override_project}' based on CLI context")
                    project = override_project
                    project_was_overridden = True
            
            logger.debug(f"Conversation {session_id} has project: {project}")
            
            # If we overrode the project, update the conversation in the database
            if project_was_overridden:
                cur.execute(
                    "UPDATE conversations SET project = %s WHERE id = %s",
                    (project, str(session_id))
                )
                conn.commit()
                logger.info(f"Updated conversation {session_id} project to '{project}' in database")
            
            # Load all messages (no limit for indexing)
            cur.execute(
                """
                SELECT role, content
                FROM messages
                WHERE conversation_id = %s
                ORDER BY created_at ASC
                """,
                (str(session_id),),
            )
            rows = cur.fetchall()
    
    if not rows:
        raise ValueError(f"No messages found for conversation {session_id}")
    
    # Build transcript
    messages = [{"role": role, "content": content} for role, content in rows]
    transcript = build_transcript(messages)
    
    # Build prompt
    prompt = build_index_prompt(transcript)
    
    # Check Ollama health before starting long operation
    if not check_ollama_health(OLLAMA_BASE_URL):
        raise OllamaError(
            f"Ollama is not accessible at {OLLAMA_BASE_URL}. "
            f"Ensure Ollama is running: `ollama serve` or check {OLLAMA_BASE_URL}/api/tags"
        )
    
    # Call Ollama with longer timeout for indexing operations
    try:
        logger.debug(f"Calling Ollama to organize conversation {session_id} (timeout: {OLLAMA_TIMEOUT}s)")
        response_text = generate_with_ollama(
            model, prompt, base_url=OLLAMA_BASE_URL, timeout=OLLAMA_TIMEOUT
        )
    except OllamaError as e:
        logger.error(f"Ollama indexing failed for session {session_id}: {e}")
        raise
    
    # Parse JSON response
    try:
        # Extract JSON from response (may have explanatory text before/after)
        json_text = extract_json_from_text(response_text)
        indexed_data = json.loads(json_text)
    except ValueError as e:
        # extract_json_from_text raised an error
        logger.error(f"Failed to extract JSON from Ollama response: {e}")
        logger.error(f"Response text: {response_text[:500]}")
        raise ValueError(f"Invalid JSON response from Ollama: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse extracted JSON: {e}")
        logger.error(f"Extracted JSON text: {response_text[:500]}")
        raise ValueError(f"Invalid JSON response from Ollama: {e}")
    
    # Validate required fields
    required_fields = [
        "title", "project", "tags", "summary_short", "summary_detailed",
        "key_entities", "key_topics", "memory_snippet"
    ]
    missing_fields = [f for f in required_fields if f not in indexed_data]
    if missing_fields:
        raise ValueError(
            f"Ollama response missing required fields: {missing_fields}. "
            f"Response: {indexed_data}"
        )
    
    # Validate and prioritize project value
    # Always use the conversation's actual project over Ollama's classification
    # (unless conversation is "general" and Ollama suggests a specific VALID project)
    # If preserve_project is True, never let Ollama override the conversation's project
    valid_projects = ["THN", "DAAS", "FF", "700B", "general"]
    ollama_project = indexed_data.get("project", "general")
    
    if ollama_project not in valid_projects:
        logger.warning(
            f"Ollama returned invalid project '{ollama_project}', "
            f"using conversation project '{project}' instead"
        )
        indexed_data["project"] = project
    elif project != "general":
        # Conversation has a specific project tag, use it (not Ollama's classification)
        if ollama_project != project:
            logger.debug(
                f"Ollama classified as '{ollama_project}', but conversation is '{project}'. "
                f"Using conversation project '{project}'."
            )
        indexed_data["project"] = project
    else:
        # Conversation is "general"
        if preserve_project:
            # Don't allow Ollama to override - preserve "general"
            if ollama_project != "general":
                logger.debug(
                    f"Conversation is 'general' and preserve_project=True. "
                    f"Ollama classified as '{ollama_project}', but preserving 'general'."
                )
            indexed_data["project"] = project  # Keep as "general"
        else:
            # Allow Ollama's classification if it's more specific AND valid
            if ollama_project != "general" and ollama_project in valid_projects:
                logger.debug(
                    f"Conversation was 'general', but Ollama classified as '{ollama_project}'. "
                    f"Using Ollama's classification."
                )
                indexed_data["project"] = ollama_project
            else:
                # Ollama returned invalid project or "general", use conversation's project
                if ollama_project not in valid_projects:
                    logger.warning(
                        f"Ollama returned invalid project '{ollama_project}' for general conversation, "
                        f"using 'general' instead"
                    )
                indexed_data["project"] = project
    
    # Upsert into conversation_index
    logger.info(f"Saving indexed data to conversation_index: session_id={session_id}, project={indexed_data['project']}")
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO conversation_index (
                    session_id, project, title, tags, summary_short,
                    summary_detailed, key_entities, key_topics, memory_snippet,
                    ollama_model, version, indexed_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (session_id)
                DO UPDATE SET
                    project = EXCLUDED.project,
                    title = EXCLUDED.title,
                    tags = EXCLUDED.tags,
                    summary_short = EXCLUDED.summary_short,
                    summary_detailed = EXCLUDED.summary_detailed,
                    key_entities = EXCLUDED.key_entities,
                    key_topics = EXCLUDED.key_topics,
                    memory_snippet = EXCLUDED.memory_snippet,
                    ollama_model = EXCLUDED.ollama_model,
                    version = EXCLUDED.version,
                    indexed_at = NOW()
                """,
                (
                    str(session_id),
                    indexed_data["project"],
                    indexed_data["title"],
                    PsycopgJson(indexed_data["tags"]),
                    indexed_data["summary_short"],
                    indexed_data["summary_detailed"],
                    PsycopgJson(indexed_data["key_entities"]),
                    PsycopgJson(indexed_data["key_topics"]),
                    indexed_data["memory_snippet"],
                    model,
                    version,
                ),
            )
            # Log the rowcount to verify the insert/update happened
            logger.info(f"Upsert executed, rowcount: {cur.rowcount}")
        conn.commit()
        logger.info(f"Transaction committed for session_id={session_id}")
    
    # Generate and store embedding for DAAS entries
    if indexed_data["project"] == "DAAS":
        try:
            from .embedding_service import generate_embedding
            
            # Combine text fields for embedding generation
            embedding_text_parts = []
            if indexed_data.get("title"):
                embedding_text_parts.append(indexed_data["title"])
            if indexed_data.get("summary_detailed"):
                embedding_text_parts.append(indexed_data["summary_detailed"])
            if indexed_data.get("memory_snippet"):
                embedding_text_parts.append(indexed_data["memory_snippet"])
            
            if embedding_text_parts:
                embedding_text = " ".join(embedding_text_parts)
                logger.debug(f"Generating embedding for DAAS entry {session_id}")
                embedding = generate_embedding(embedding_text)
                
                # Convert embedding list to string format for PostgreSQL
                # pgvector expects format: '[0.1,0.2,0.3,...]'
                embedding_str = '[' + ','.join(str(x) for x in embedding) + ']'
                
                # Store embedding in conversation_index
                with get_conn() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            UPDATE conversation_index
                            SET embedding = %s::vector
                            WHERE session_id = %s
                            """,
                            (embedding_str, str(session_id)),
                        )
                    conn.commit()
                
                logger.debug(f"Stored embedding for DAAS entry {session_id}")
        except Exception as e:
            logger.warning(f"Failed to generate/store embedding for DAAS entry {session_id}: {e}")
            # Don't fail the indexing if embedding generation fails
            # The entry will still be indexed, just without embedding
    
    logger.info(f"Successfully indexed session {session_id}")
    return indexed_data


def list_memories(project: str = None, limit: int = 50) -> List[Dict[str, Any]]:
    """
    List conversation index entries.
    
    Args:
        project: Filter by project (optional)
        limit: Max number of entries to return
    
    Returns:
        List of dicts with session_id, title, project, indexed_at, version
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            if project:
                cur.execute(
                    """
                    SELECT session_id, title, project, indexed_at, version
                    FROM conversation_index
                    WHERE project = %s
                    ORDER BY indexed_at DESC
                    LIMIT %s
                    """,
                    (project, limit),
                )
            else:
                cur.execute(
                    """
                    SELECT session_id, title, project, indexed_at, version
                    FROM conversation_index
                    ORDER BY indexed_at DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
            rows = cur.fetchall()
    
    return [
        {
            "session_id": str(row[0]),
            "title": row[1],
            "project": row[2],
            "indexed_at": row[3],
            "version": row[4],
        }
        for row in rows
    ]


def view_memory(session_id: uuid.UUID | str) -> Dict[str, Any] | None:
    """
    View detailed information for a specific memory entry.
    
    Args:
        session_id: UUID of the conversation session
    
    Returns:
        Dict with all indexed fields, or None if not found
    """
    if isinstance(session_id, str):
        session_id = uuid.UUID(session_id)
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT session_id, project, title, tags, summary_short,
                       summary_detailed, key_entities, key_topics, memory_snippet,
                       ollama_model, version, indexed_at
                FROM conversation_index
                WHERE session_id = %s
                """,
                (str(session_id),),
            )
            row = cur.fetchone()
    
    if not row:
        return None
    
    return {
        "session_id": str(row[0]),
        "project": row[1],
        "title": row[2],
        "tags": row[3],
        "summary_short": row[4],
        "summary_detailed": row[5],
        "key_entities": row[6],
        "key_topics": row[7],
        "memory_snippet": row[8],
        "ollama_model": row[9],
        "version": row[10],
        "indexed_at": row[11],
    }


def refresh_memory(session_id: uuid.UUID | str) -> Dict[str, Any]:
    """
    Refresh/reindex a specific memory entry.
    
    Args:
        session_id: UUID of the conversation session
    
    Returns:
        Dict with updated indexed data
    
    Raises:
        ValueError: If session not found or indexing fails
    """
    return index_session(session_id)


def delete_memory(session_id: uuid.UUID | str) -> bool:
    """
    Delete a memory entry from conversation_index.
    
    Args:
        session_id: UUID of the conversation session
    
    Returns:
        True if deleted, False if not found
    """
    if isinstance(session_id, str):
        session_id = uuid.UUID(session_id)
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM conversation_index
                WHERE session_id = %s
                """,
                (str(session_id),),
            )
            deleted = cur.rowcount > 0
        conn.commit()
    
    return deleted

