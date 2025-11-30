"""
Conversation indexer module for organizing and storing conversation metadata.
Uses Ollama to generate structured summaries, tags, and memory snippets.
"""
import json
import logging
import re
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
    Extract JSON object from text that may contain explanatory text or markdown.
    
    Uses multiple extraction strategies:
    1. Search for JSON in markdown code blocks (```json ... ```)
    2. Search for JSON in generic code blocks (``` ... ```)
    3. Search entire text for '{' character (not just at start)
    
    Handles nested objects properly and removes JSON comments.
    
    Args:
        text: Text that may contain JSON mixed with other text or markdown
    
    Returns:
        Extracted JSON string with comments removed
    
    Raises:
        ValueError: If no valid JSON object is found after all strategies
    """
    text = text.strip()
    original_text = text
    
    # Strategy 1: Look for JSON code blocks (```json ... ```)
    json_code_block_pattern = r"```json\s*\n(.*?)\n```"
    json_match = re.search(json_code_block_pattern, text, re.DOTALL)
    if json_match:
        logger.debug("Found JSON in ```json code block")
        text = json_match.group(1).strip()
        # Continue to extraction logic below
    
    # Strategy 2: Look for generic code blocks (``` ... ```) that might contain JSON
    if text == original_text:  # Only if Strategy 1 didn't find anything
        code_block_pattern = r"```[a-z]*\s*\n(.*?)\n```"
        code_match = re.search(code_block_pattern, text, re.DOTALL)
        if code_match:
            potential_json = code_match.group(1).strip()
            # Check if it looks like JSON (starts with { or [)
            if potential_json.startswith("{") or potential_json.startswith("["):
                logger.debug("Found JSON-like content in generic code block")
                text = potential_json
                # Continue to extraction logic below
    
    # Strategy 3: Remove markdown code blocks if present (legacy handling)
    if text.startswith("```"):
        lines = text.split("\n")
        if len(lines) > 2:
            text = "\n".join(lines[1:-1])
    if text.startswith("```json"):
        lines = text.split("\n")
        if len(lines) > 2:
            text = "\n".join(lines[1:-1])
    
    # Strategy 4: Search entire text for '{' character (not just at start)
    # This handles cases where JSON appears after markdown text
    start_idx = text.find("{")
    if start_idx == -1:
        # Try searching for array start as well
        start_idx = text.find("[")
        if start_idx == -1:
            logger.debug("No JSON object or array found in response after all strategies")
            raise ValueError("No JSON object found in response (no opening brace)")
        else:
            logger.debug("Found JSON array, but expecting object - will fail validation")
            # Still raise error since we need an object, not an array
            raise ValueError("No JSON object found in response (found array instead)")
    
    if start_idx > 0:
        logger.debug(f"Found JSON starting at position {start_idx} (after {start_idx} characters of text)")
    
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


def generate_json_from_markdown(markdown_text: str, conversation_metadata: Dict[str, str]) -> Dict[str, Any]:
    """
    Generate valid JSON from markdown-formatted Ollama response when extraction fails.
    
    Parses markdown structure to extract key fields and generates a valid JSON object
    with all required fields. Uses conversation metadata as fallback values.
    
    Args:
        markdown_text: Markdown-formatted response from Ollama
        conversation_metadata: Dict with 'title' and 'project' keys from conversation
    
    Returns:
        Valid JSON object (dict) with all required fields for indexing
    """
    logger.info("Generating JSON from markdown using fallback method")
    
    # Initialize result with defaults
    result = {
        "title": conversation_metadata.get("title", "Untitled Conversation"),
        "project": conversation_metadata.get("project", "general"),
        "tags": [],
        "summary_short": "Conversation indexed (fallback generation)",
        "summary_detailed": "Full details unavailable due to indexing format issue. See conversation for details.",
        "key_entities": {
            "people": [],
            "domains": [],
            "assets": []
        },
        "key_topics": [],
        "memory_snippet": "See conversation for details"
    }
    
    # Parse markdown to extract fields
    lines = markdown_text.split("\n")
    
    # Extract title
    for i, line in enumerate(lines):
        # Look for **Title:**, * Title:, or Title: patterns
        if re.search(r"\*\*Title:\*\*|\* Title:|Title:", line, re.IGNORECASE):
            # Extract text after colon
            match = re.search(r":\s*(.+)", line)
            if match:
                result["title"] = match.group(1).strip().strip("*").strip()
                logger.debug(f"Extracted title from markdown: {result['title']}")
            break
    
    # Extract project
    for i, line in enumerate(lines):
        if re.search(r"\*\*Project:\*\*|\* Project:|Project:", line, re.IGNORECASE):
            match = re.search(r":\s*(.+)", line)
            if match:
                project_text = match.group(1).strip().strip("*").strip()
                # Normalize project tag
                from .chat import normalize_project_tag
                result["project"] = normalize_project_tag(project_text)
                logger.debug(f"Extracted project from markdown: {result['project']}")
            break
    
    # Extract tags
    for i, line in enumerate(lines):
        if re.search(r"\*\*Tags:\*\*|\* Tags:|Tags:", line, re.IGNORECASE):
            # Look for array format [tag1, tag2] or list format
            match = re.search(r"\[([^\]]+)\]", line)
            if match:
                tags_str = match.group(1)
                # Split by comma and clean
                tags = [tag.strip().strip('"').strip("'") for tag in tags_str.split(",")]
                result["tags"] = [tag for tag in tags if tag]
                logger.debug(f"Extracted tags from markdown: {result['tags']}")
            break
    
    # Extract summary_short and summary_detailed
    summary_lines = []
    in_summary = False
    for i, line in enumerate(lines):
        if re.search(r"\*\*Summary[^:]*:\*\*|\* Summary[^:]*:|Summary[^:]*:", line, re.IGNORECASE):
            in_summary = True
            # Get text after colon if present
            match = re.search(r":\s*(.+)", line)
            if match:
                summary_lines.append(match.group(1).strip())
            continue
        if in_summary:
            # Stop at next header or empty line followed by header
            if re.match(r"^\*\*|^\* |^#", line):
                break
            if line.strip():
                summary_lines.append(line.strip())
    
    if summary_lines:
        summary_text = " ".join(summary_lines)
        # Use first sentence for short, all for detailed
        sentences = re.split(r"[.!?]\s+", summary_text)
        if sentences:
            result["summary_short"] = sentences[0] + ("." if not sentences[0].endswith(".") else "")
            result["summary_detailed"] = summary_text
            logger.debug(f"Extracted summary from markdown (length: {len(summary_text)} chars)")
    
    # Extract key_entities (simplified - look for patterns)
    for i, line in enumerate(lines):
        if re.search(r"\*\*Key Entities:\*\*|\* Key Entities:|Key Entities:", line, re.IGNORECASE):
            # Try to extract people, domains, assets from following lines
            for j in range(i + 1, min(i + 10, len(lines))):
                entity_line = lines[j]
                if "people" in entity_line.lower():
                    people_match = re.search(r"\[([^\]]+)\]", entity_line)
                    if people_match:
                        people_str = people_match.group(1)
                        result["key_entities"]["people"] = [p.strip().strip('"').strip("'") for p in people_str.split(",") if p.strip()]
                if "domains" in entity_line.lower():
                    domains_match = re.search(r"\[([^\]]+)\]", entity_line)
                    if domains_match:
                        domains_str = domains_match.group(1)
                        result["key_entities"]["domains"] = [d.strip().strip('"').strip("'") for d in domains_str.split(",") if d.strip()]
                if "assets" in entity_line.lower():
                    assets_match = re.search(r"\[([^\]]+)\]", entity_line)
                    if assets_match:
                        assets_str = assets_match.group(1)
                        result["key_entities"]["assets"] = [a.strip().strip('"').strip("'") for a in assets_str.split(",") if a.strip()]
            break
    
    # Extract key_topics
    for i, line in enumerate(lines):
        if re.search(r"\*\*Key Topics:\*\*|\* Key Topics:|Key Topics:", line, re.IGNORECASE):
            match = re.search(r"\[([^\]]+)\]", line)
            if match:
                topics_str = match.group(1)
                result["key_topics"] = [t.strip().strip('"').strip("'") for t in topics_str.split(",") if t.strip()]
                logger.debug(f"Extracted key_topics from markdown: {result['key_topics']}")
            break
    
    # Extract memory_snippet
    for i, line in enumerate(lines):
        if re.search(r"\*\*Memory[^:]*:\*\*|\* Memory[^:]*:|Memory[^:]*:", line, re.IGNORECASE):
            snippet_lines = []
            for j in range(i + 1, min(i + 5, len(lines))):
                snippet_line = lines[j].strip()
                if snippet_line and not re.match(r"^\*\*|^\* |^#", snippet_line):
                    snippet_lines.append(snippet_line)
                elif snippet_lines:
                    break
            if snippet_lines:
                result["memory_snippet"] = " ".join(snippet_lines)
                logger.debug(f"Extracted memory_snippet from markdown (length: {len(result['memory_snippet'])} chars)")
            break
    
    logger.info(f"Generated JSON from markdown: title='{result['title']}', project='{result['project']}', tags={len(result['tags'])}")
    return result


def build_index_prompt(transcript: str) -> str:
    """
    Build the prompt for Ollama to organize a conversation.
    
    Enhanced with explicit JSON format requirements and multiple emphasis points
    to improve compliance with JSON-only output.
    
    Args:
        transcript: Full conversation transcript from build_transcript()
    
    Returns:
        Prompt string instructing Ollama to return structured JSON
    """
    prompt = f"""You MUST return ONLY valid JSON. No markdown, no explanatory text, no additional formatting.

CRITICAL: Your response must start with '{{' and end with '}}'. Do not include any text before or after the JSON object.

You are a conversation organizer. Analyze the following conversation and extract structured information.

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

IMPORTANT: Return ONLY valid JSON. No markdown formatting, no explanatory text, no code blocks. Just the JSON object starting with '{{' and ending with '}}'.
"""
    return prompt


def index_session(
    session_id: uuid.UUID | str,
    model: str = None,
    version: int = None,
    override_project: str = None,
    preserve_project: bool = False,
) -> Optional[Dict[str, Any]]:
    """
    Index a conversation session using Ollama.
    
    Loads all messages for the session, builds a transcript, sends to Ollama
    for organization, parses the response, and upserts into conversation_index.
    
    Uses multiple strategies to extract JSON:
    1. Primary extraction from response
    2. Fallback generation from markdown if extraction fails
    
    Args:
        session_id: UUID of the conversation session
        model: Ollama model to use (defaults to OLLAMA_MODEL from config)
        version: Index version number (defaults to CONVERSATION_INDEX_VERSION)
        override_project: Override project classification (if conversation is "general")
        preserve_project: If True, don't let Ollama override conversation's project
    
    Returns:
        Dict with indexed data (title, project, tags, etc.) or None if indexing fails completely
    
    Raises:
        OllamaError: If Ollama API call fails (network, timeout, etc.)
        ValueError: If conversation not found or no messages
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
    logger.debug(f"Generated prompt for indexing session {session_id} (length: {len(prompt)} chars)")
    
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
        logger.debug(f"Attempting to extract JSON from Ollama response (length: {len(response_text)} chars)")
        json_text = extract_json_from_text(response_text)
        indexed_data = json.loads(json_text)
        logger.debug("Successfully extracted and parsed JSON from Ollama response")
    except ValueError as e:
        # extract_json_from_text raised an error - log full response for debugging
        response_preview = response_text[:1000] if len(response_text) > 1000 else response_text
        logger.error(f"Failed to extract JSON from Ollama response: {e}")
        logger.error(f"Response text (first 1000 chars): {response_preview}")
        if len(response_text) > 1000:
            logger.error(f"Response text truncated (total length: {len(response_text)} chars)")
        # Try fallback generation before raising error
        logger.info("Attempting fallback JSON generation from markdown...")
        try:
            # Get conversation metadata for fallback
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT project, title FROM conversations WHERE id = %s",
                        (str(session_id),)
                    )
                    conv_row = cur.fetchone()
                    if conv_row:
                        conv_project, conv_title = conv_row
                        conversation_metadata = {
                            "title": conv_title or "Untitled Conversation",
                            "project": conv_project or "general"
                        }
                    else:
                        conversation_metadata = {"title": "Unknown", "project": "general"}
            
            # Try fallback generation
            indexed_data = generate_json_from_markdown(response_text, conversation_metadata)
            logger.info("Successfully generated JSON from markdown using fallback method")
        except Exception as fallback_error:
            logger.error(f"Fallback JSON generation also failed: {fallback_error}")
            # Log what was received vs. expected
            logger.error(f"Expected: Valid JSON object starting with '{{'")
            logger.error(f"Received: {response_preview[:200]}...")
            # Return None instead of raising - graceful degradation
            logger.warning(f"Indexing failed for session {session_id}, but conversation will still be saved")
            return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse extracted JSON: {e}")
        logger.error(f"Extracted JSON text (first 500 chars): {response_text[:500]}")
        # Try fallback generation
        logger.info("Attempting fallback JSON generation from markdown...")
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT project, title FROM conversations WHERE id = %s",
                        (str(session_id),)
                    )
                    conv_row = cur.fetchone()
                    if conv_row:
                        conv_project, conv_title = conv_row
                        conversation_metadata = {
                            "title": conv_title or "Untitled Conversation",
                            "project": conv_project or "general"
                        }
                    else:
                        conversation_metadata = {"title": "Unknown", "project": "general"}
            
            indexed_data = generate_json_from_markdown(response_text, conversation_metadata)
            logger.info("Successfully generated JSON from markdown using fallback method")
        except Exception as fallback_error:
            logger.error(f"Fallback JSON generation also failed: {fallback_error}")
            logger.warning(f"Indexing failed for session {session_id}, but conversation will still be saved")
            return None
    
    # Check if indexing failed (None returned from fallback)
    if indexed_data is None:
        logger.warning(f"Indexing failed for session {session_id} - all extraction methods failed")
        return None
    
    # Validate required fields
    required_fields = [
        "title", "project", "tags", "summary_short", "summary_detailed",
        "key_entities", "key_topics", "memory_snippet"
    ]
    missing_fields = [f for f in required_fields if f not in indexed_data]
    if missing_fields:
        logger.error(f"Generated/extracted JSON missing required fields: {missing_fields}")
        # Try to fill in missing fields with defaults
        for field in missing_fields:
            if field == "tags":
                indexed_data["tags"] = []
            elif field == "key_entities":
                indexed_data["key_entities"] = {"people": [], "domains": [], "assets": []}
            elif field == "key_topics":
                indexed_data["key_topics"] = []
            else:
                indexed_data[field] = f"Missing {field}"
        logger.warning(f"Filled missing fields with defaults, continuing with indexing")
    
    # Validate and prioritize project value
    # Always use the conversation's actual project over Ollama's classification
    # (unless conversation is "general" and Ollama suggests a specific VALID project)
    # If preserve_project is True, never let Ollama override the conversation's project
    valid_projects = ["THN", "DAAS", "FF", "700B", "general"]
    ollama_project = indexed_data.get("project", "general")
    
    # If conversation has a specific project (not "general"), always use it
    if project != "general":
        # Conversation has a specific project tag, use it (not Ollama's classification)
        if ollama_project != project and ollama_project in valid_projects:
            logger.debug(
                f"Ollama classified as '{ollama_project}', but conversation is '{project}'. "
                f"Using conversation project '{project}'."
            )
        elif ollama_project not in valid_projects and ollama_project is not None:
            # Only log warning if Ollama returned something invalid (not None or empty)
            logger.debug(
                f"Ollama returned invalid project '{ollama_project}', "
                f"using conversation project '{project}' (expected behavior)"
            )
        indexed_data["project"] = project
    elif ollama_project not in valid_projects:
        # Conversation is "general" but Ollama returned invalid project
        if ollama_project is not None:
            logger.debug(
                f"Ollama returned invalid project '{ollama_project}' for general conversation, "
                f"using 'general' (expected behavior)"
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

