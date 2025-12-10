"""
Project context builder for injecting conversation memory into chat prompts.
Builds context directly from project_knowledge and conversation_index entries.

For DAAS project, uses custom retrieval rules:
- Single-dream mode: Quoted title detection and title-based matching
- Pattern-based mode: Vector similarity search using embeddings
"""
import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any

from .db import get_conn
from .memory import fetch_project_knowledge

logger = logging.getLogger(__name__)

# Module-level cache for base system prompt
_base_system_prompt_cache: Optional[str] = None


def load_base_system_prompt() -> str:
    """
    Load the base system prompt from brain_core/base_system_prompt.txt.
    
    Uses module-level caching to avoid repeated file I/O. If the file is missing
    or unreadable, falls back to a minimal default prompt and logs a warning.
    
    Returns:
        Base system prompt as string
        
    Raises:
        None - always returns a valid string (either from file or fallback)
    """
    global _base_system_prompt_cache
    
    # Return cached value if available
    if _base_system_prompt_cache is not None:
        return _base_system_prompt_cache
    
    # Determine file path relative to this module
    module_dir = Path(__file__).parent
    prompt_file = module_dir / "base_system_prompt.txt"
    
    try:
        # Load prompt from file
        prompt_content = prompt_file.read_text(encoding='utf-8').strip()
        
        if prompt_content:
            # Cache and return
            _base_system_prompt_cache = prompt_content
            logger.info(f"Loaded base system prompt from {prompt_file}")
            return _base_system_prompt_cache
        else:
            # File exists but is empty
            logger.warning(f"Base system prompt file {prompt_file} is empty, using fallback")
            return _get_fallback_prompt()
            
    except FileNotFoundError:
        logger.warning(f"Base system prompt file {prompt_file} not found, using fallback")
        return _get_fallback_prompt()
    except IOError as e:
        logger.warning(f"Could not read base system prompt file {prompt_file}: {e}, using fallback")
        return _get_fallback_prompt()
    except Exception as e:
        logger.error(f"Unexpected error loading base system prompt: {e}, using fallback")
        return _get_fallback_prompt()


def _get_fallback_prompt() -> str:
    """
    Get a minimal fallback system prompt when the file cannot be loaded.
    
    Returns:
        Minimal fallback prompt string
    """
    return (
        "You are a helpful, accurate, and context-aware AI assistant. "
        "Your goal is to support the user by providing clear, concise, and reliable responses. "
        "You should always be conversational, honest, direct, and thoughtful."
    )


def build_project_system_prompt(project: str) -> str:
    """
    Build the complete system prompt for a given project.
    
    Loads the base system prompt and appends project-specific extension if
    the project is not "general". The extension includes overview and rules
    from project_knowledge table.
    
    Args:
        project: Project tag (THN, DAAS, FF, 700B, or "general")
        
    Returns:
        Composed system prompt string (base + project extension if applicable)
    """
    base_prompt = load_base_system_prompt()
    
    # Only add project extension if project is not "general"
    if project and project.lower() != "general":
        # Get project overview from project_knowledge table
        project_overview = _get_project_overview(project)
        
        if project_overview:
            # Start building project extension
            project_extension_parts = [
                f"\n\nIn this current conversation is tagged as project {project.upper()}.",
                f"\n\nHere's a general overview of the project {project.upper()}: {project_overview}"
            ]
            
            # Get and parse project rules
            rules_text = _get_project_rules(project)
            if rules_text:
                parsed_rules = _parse_rules_text(rules_text)
                if parsed_rules:
                    # Format rules as numbered markdown list
                    project_extension_parts.append("\n\n---")
                    project_extension_parts.append(f"\n\n### Project {project.upper()} rules:\n")
                    for i, rule in enumerate(parsed_rules, start=1):
                        project_extension_parts.append(f"{i}. {rule}\n")
                    logger.debug(f"Added {len(parsed_rules)} rules for {project.upper()}")
            
            project_extension = "".join(project_extension_parts)
            logger.debug(f"Added project extension for {project.upper()}")
            return base_prompt + project_extension
        else:
            logger.debug(f"No project overview found for {project.upper()}, using base prompt only")
    
    # Return base prompt only for general or if overview not found
    return base_prompt


def _get_project_overview(project: str) -> Optional[str]:
    """
    Get the overview summary for a project from project_knowledge table.
    
    Updated to query overview column directly (new table structure).
    
    Args:
        project: Project tag (THN, DAAS, FF, 700B)
        
    Returns:
        Overview summary string, or None if not found
    """
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                # Query overview column directly (new structure after migration)
                cur.execute(
                    """
                    SELECT overview
                    FROM project_knowledge
                    WHERE project = %s
                    LIMIT 1
                    """,
                    (project.upper(),),
                )
                row = cur.fetchone()
                if row:
                    return row[0]
    except Exception as e:
        logger.debug(f"Could not fetch project overview for {project}: {e}")
    
    return None


def _get_project_rules(project: str) -> Optional[str]:
    """
    Get the rules text for a project from project_knowledge table.
    
    Args:
        project: Project tag (THN, DAAS, FF, 700B)
        
    Returns:
        Rules text as string, or None if not found or empty
    """
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT rules
                    FROM project_knowledge
                    WHERE project = %s
                    LIMIT 1
                    """,
                    (project.upper(),),
                )
                row = cur.fetchone()
                if row and row[0]:
                    rules_text = row[0].strip()
                    if rules_text:
                        logger.debug(f"Retrieved rules for {project.upper()}")
                        return rules_text
    except Exception as e:
        logger.debug(f"Could not fetch project rules for {project}: {e}")
    
    return None


def _parse_rules_text(rules_text: str) -> List[str]:
    """
    Parse rules text into list of individual rules.
    
    Handles various formats:
    - Numbered list: "1. Rule one\n2. Rule two\n3. Rule three"
    - Newline-separated: "Rule one\nRule two\nRule three"
    
    Args:
        rules_text: Raw rules text from database
        
    Returns:
        List of rule strings (cleaned and filtered)
    """
    if not rules_text or not rules_text.strip():
        return []
    
    rules = []
    
    # Try splitting by numbered patterns first (1., 2., etc.)
    # Pattern matches: number followed by period/dot, optional space
    numbered_pattern = r'^\s*\d+\.\s*(.+)$'
    
    lines = rules_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Try to match numbered pattern
        match = re.match(numbered_pattern, line)
        if match:
            # Extract rule text after number
            rule_text = match.group(1).strip()
            if rule_text:
                rules.append(rule_text)
        else:
            # If no numbered pattern, treat entire line as rule (if not empty)
            if line:
                rules.append(line)
    
    # Filter out empty rules
    rules = [r for r in rules if r.strip()]
    
    if rules:
        logger.debug(f"Parsed {len(rules)} rules from rules text")
    else:
        logger.debug("No rules found after parsing")
    
    return rules


def extract_json_from_text(text: str) -> str:
    """
    Extract JSON object from text that may contain explanatory text.
    
    Looks for the first '{' and finds the matching closing '}' to extract
    the JSON object, handling nested objects properly.
    
    Args:
        text: Text that may contain JSON mixed with other text
    
    Returns:
        Extracted JSON string
    
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
    
    # Remove JSON comments (both // single-line and /* */ multi-line)
    # JSON doesn't support comments, but Ollama sometimes adds them
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




def build_project_context(
    project: str,
    user_message: str,
    limit_memories: int = 200,
    top_n: int = 5,
) -> Dict[str, Any]:
    """
    Build project-aware context from project_knowledge and conversation_index entries.
    
    For DAAS project: Uses custom retrieval rules (single-dream or pattern-based).
    For other projects: Uses keyword-based relevance scoring.
    
    Fetches stable project overview from project_knowledge table, queries indexed
    memories from conversation_index for the project, applies simple relevance scoring,
    selects top N relevant entries, and formats them directly into context.
    Follows strategic ordering: project_knowledge summaries (stable overview) FIRST,
    then conversation_index memories (specific conversation details) SECOND.
    
    Args:
        project: Project tag (THN, DAAS, FF, 700B, general)
        user_message: Current user message to match against (used for relevance scoring)
        limit_memories: Max number of indexed entries to consider (default: 200)
        top_n: Number of top relevant entries to use (default: 5)
    
    Returns:
        Dict with 'context' (string) and 'notes' (list of strings)
        Returns empty dict if no relevant data found
    """
    
    # DAAS-specific retrieval: custom rules for dream analysis
    if project == 'DAAS':
        try:
            from .daas_retrieval import retrieve_daas_context
            from .config import DAAS_VECTOR_TOP_K
            
            # Use configured top_k
            top_k = DAAS_VECTOR_TOP_K
            
            daas_result = retrieve_daas_context(user_message, top_k=top_k)
            
            # Get project-scoped meditation notes for DAAS
            mcp_notes_context = None
            try:
                from src.mcp.api import get_mcp_api
                api = get_mcp_api()
                project_notes = api.get_project_notes(project, user_message, limit=5)
                if project_notes:
                    notes_parts = []
                    for note in project_notes:
                        notes_parts.append(f"From {note['title']} ({note['uri']}):\n{note['content_snippet']}")
                    if notes_parts:
                        mcp_notes_context = "\n\n---\n\n".join(notes_parts)
            except Exception as e:
                logger.debug(f"MCP notes not available for DAAS: {e}")
            
            # If we have dreams from DAAS retrieval, use them
            if daas_result.get('dreams'):
                # Build context from DAAS retrieval result
                context_parts = []
                notes = []
                
                # Add MCP meditation notes if available
                if mcp_notes_context:
                    context_parts.append(f"Here are relevant meditation notes from this project:\n\n{mcp_notes_context}")
                    notes.append("MCP notes: Retrieved relevant project-scoped meditation notes")
                
                # Add project knowledge if available
                knowledge_summaries = fetch_project_knowledge(project)
                if knowledge_summaries:
                    project_summary = "\n\n".join(knowledge_summaries)
                    context_parts.append(f"Here is a general summary of the DAAS project:\n{project_summary}")
                    notes.extend([f"Project knowledge: {s[:100]}..." if len(s) > 100 else f"Project knowledge: {s}" for s in knowledge_summaries])
                
                # Add DAAS retrieval context
                if daas_result.get('context'):
                    if daas_result['mode'] == 'single':
                        context_parts.append(f"Here is the specific dream you asked about:\n\n{daas_result['context']}")
                        notes.append(f"Single dream: {daas_result['dreams'][0].get('title', 'Unknown')}")
                    else:
                        context_parts.append(f"Here are relevant dreams from your dream history:\n\n{daas_result['context']}")
                        notes.extend([f"Dream: {d.get('title', 'Unknown')}" for d in daas_result['dreams'][:5]])
                
                if context_parts:
                    context = "\n\n".join(context_parts)
                    context += "\n\nUse this information naturally in our conversation. Recall and reference "
                    context += "relevant details from these notes and dreams as we discuss topics."
                    
                    logger.debug(f"Built DAAS context using {daas_result['mode']} mode with {len(daas_result['dreams'])} dreams")
                    return {
                        "context": context,
                        "notes": notes[:10]
                    }
            else:
                # No dreams found, but still include project knowledge if available
                knowledge_summaries = fetch_project_knowledge(project)
                if knowledge_summaries:
                    project_summary = "\n\n".join(knowledge_summaries)
                    context = f"Here is a general summary of the DAAS project:\n{project_summary}\n\n{daas_result.get('context', '')}"
                    return {
                        "context": context,
                        "notes": [f"Project knowledge: {s[:100]}..." if len(s) > 100 else f"Project knowledge: {s}" for s in knowledge_summaries[:5]]
                    }
                else:
                    # Return empty or error message
                    return {
                        "context": daas_result.get('context', ''),
                        "notes": []
                    }
                    
        except Exception as e:
            logger.error(f"DAAS retrieval failed, falling back to default keyword search: {e}")
            # Fall through to default behavior (keyword-based search)
    
    # THN-specific retrieval: code RAG pipeline
    if project == 'THN':
        try:
            from .thn_code_retrieval import get_thn_code_context
            
            # Retrieve relevant code chunks
            code_context = get_thn_code_context(user_message, top_k=5)
            
            # Get project-scoped meditation notes for THN
            mcp_notes_context = None
            try:
                from src.mcp.api import get_mcp_api
                api = get_mcp_api()
                project_notes = api.get_project_notes(project, user_message, limit=5)
                if project_notes:
                    notes_parts = []
                    for note in project_notes:
                        notes_parts.append(f"From {note['title']} ({note['uri']}):\n{note['content_snippet']}")
                    if notes_parts:
                        mcp_notes_context = "\n\n---\n\n".join(notes_parts)
            except Exception as e:
                logger.debug(f"MCP notes not available for THN: {e}")
            
            if code_context:
                # Build context with code and project knowledge
                context_parts = []
                notes = []
                
                # Add MCP meditation notes if available
                if mcp_notes_context:
                    context_parts.append(f"Here are relevant meditation notes from this project:\n\n{mcp_notes_context}")
                    notes.append("MCP notes: Retrieved relevant project-scoped meditation notes")
                
                # Add project knowledge if available
                knowledge_summaries = fetch_project_knowledge(project)
                if knowledge_summaries:
                    project_summary = "\n\n".join(knowledge_summaries)
                    context_parts.append(f"Here is a general summary of the THN project:\n{project_summary}")
                    notes.extend([f"Project knowledge: {s[:100]}..." if len(s) > 100 else f"Project knowledge: {s}" for s in knowledge_summaries])
                
                # Add code context
                context_parts.append(f"Here is relevant code from the THN codebase:\n\n{code_context}")
                notes.append("THN code retrieval: Retrieved relevant code snippets")
                
                # Also include conversation memories (fallback to default behavior for memories)
                # But prioritize code context
                context = "\n\n".join(context_parts)
                context += "\n\nUse this information naturally in our conversation. Recall and reference "
                context += "relevant code and notes as we discuss topics. Focus on actual code when "
                context += "providing technical guidance. Use actual code examples, explain "
                context += "how code works, identify patterns, and suggest practical exercises."
                
                logger.debug(f"Built THN context with code retrieval")
                return {
                    "context": context,
                    "notes": notes[:10]
                }
            else:
                # No code found, but still include project knowledge if available
                knowledge_summaries = fetch_project_knowledge(project)
                if knowledge_summaries:
                    project_summary = "\n\n".join(knowledge_summaries)
                    context = f"Here is a general summary of the THN project:\n{project_summary}"
                    return {
                        "context": context,
                        "notes": [f"Project knowledge: {s[:100]}..." if len(s) > 100 else f"Project knowledge: {s}" for s in knowledge_summaries[:5]]
                    }
                else:
                    # No code or knowledge, fall through to default
                    logger.debug("No THN code or knowledge found, using default context")
                    
        except Exception as e:
            logger.error(f"THN code retrieval failed, falling back to default keyword search: {e}")
            # Fall through to default behavior (keyword-based search)
    
    # Get project-scoped meditation notes (if MCP available)
    mcp_notes_context = None
    try:
        from src.mcp.api import get_mcp_api
        api = get_mcp_api()
        # Get relevant notes for this project
        project_notes = api.get_project_notes(project, user_message, limit=5)
        if project_notes:
            # Format notes for context
            notes_parts = []
            for note in project_notes:
                notes_parts.append(f"From {note['title']} ({note['uri']}):\n{note['content_snippet']}")
            if notes_parts:
                mcp_notes_context = "\n\n---\n\n".join(notes_parts)
    except Exception as e:
        logger.debug(f"MCP notes not available for project {project}: {e}")
    
    # Default behavior for non-DAAS/THN projects or fallback
    # Fetch project_knowledge summaries (stable overview) - FIRST
    knowledge_summaries = fetch_project_knowledge(project)
    
    # Query conversation_index for this project
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT session_id, title, tags, summary_short, summary_detailed,
                       key_topics, memory_snippet, indexed_at
                FROM conversation_index
                WHERE project = %s
                ORDER BY indexed_at DESC
                LIMIT %s
                """,
                (project, limit_memories),
            )
            rows = cur.fetchall()
    
    top_memories = []
    if rows:
        # Simple relevance scoring: count word matches in tags, key_topics, summary_detailed
        user_words = set(user_message.lower().split())
        
        scored_memories = []
        for row in rows:
            (session_id, title, tags, summary_short, summary_detailed,
             key_topics, memory_snippet, indexed_at) = row
            
            # Extract text fields for matching
            text_fields = []
            if tags:
                if isinstance(tags, list):
                    text_fields.extend([str(t).lower() for t in tags])
                elif isinstance(tags, dict):
                    text_fields.extend([str(v).lower() for v in tags.values() if v])
            
            if key_topics:
                if isinstance(key_topics, list):
                    text_fields.extend([str(t).lower() for t in key_topics])
                elif isinstance(key_topics, dict):
                    text_fields.extend([str(v).lower() for v in key_topics.values() if v])
            
            if summary_detailed:
                text_fields.append(summary_detailed.lower())
            
            # Count word matches
            all_text = " ".join(text_fields)
            match_count = sum(1 for word in user_words if word in all_text)
            
            scored_memories.append((match_count, row))
        
        # Sort by relevance (descending) and take top N
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        top_memories = [row for _, row in scored_memories[:top_n]]
    
    # If no project_knowledge and no memories, return empty
    if not knowledge_summaries and not top_memories:
        logger.debug(f"No context data found for project {project}")
        return {}
    
    # Build context directly from project_knowledge and selected memories
    context_parts = []
    notes = []
    
    # Add MCP meditation notes if available
    if mcp_notes_context:
        context_parts.append(f"Here are relevant meditation notes from this project:\n\n{mcp_notes_context}")
        notes.append("MCP notes: Retrieved relevant project-scoped meditation notes")
    
    # Add project_knowledge overview (stable foundation) - uses summary column
    if knowledge_summaries:
        # Combine all summaries into a single project overview
        project_summary = "\n\n".join(knowledge_summaries)
        context_parts.append(f"Here is a general summary of the project:\n{project_summary}")
        # Add summaries as notes
        notes.extend([f"Project knowledge: {s[:100]}..." if len(s) > 100 else f"Project knowledge: {s}" for s in knowledge_summaries])
    
    # Add relevant conversation memories (specific details) - SECOND
    if top_memories:
        memories_text = []
        for row in top_memories:
            (session_id, title, tags, summary_short, summary_detailed,
             key_topics, memory_snippet, indexed_at) = row
            
            mem_parts = []
            if title:
                mem_parts.append(f"Title: {title}")
            if summary_short:
                mem_parts.append(f"Summary: {summary_short}")
            if memory_snippet:
                mem_parts.append(f"Memory: {memory_snippet}")
            if key_topics:
                topics_str = ", ".join(key_topics) if isinstance(key_topics, list) else str(key_topics)
                mem_parts.append(f"Topics: {topics_str}")
            
            if mem_parts:
                memories_text.append("\n".join(mem_parts))
                # Add to notes
                if summary_short:
                    notes.append(f"Previous conversation: {summary_short[:80]}..." if len(summary_short) > 80 else f"Previous conversation: {summary_short}")
        
        if memories_text:
            memories_block = "\n\n---\n\n".join(memories_text)
            context_parts.append(f"Here are relevant memories from past conversations in this project:\n\n{memories_block}")
    
    # Combine into final context
    if not context_parts:
        logger.debug(f"No context data found for project {project}")
        return {}
    
    context = "\n\n".join(context_parts)
    
    # Add instruction text about how to use this information
    context += "\n\nUse this information in our conversation. This is a natural dialogue - "
    context += "recall and reference relevant information from these notes and prior conversations "
    context += "as topics come up."
    
    logger.debug(f"Built project context for {project} with {len(top_memories)} memories and {len(knowledge_summaries)} knowledge entries")
    
    return {
        "context": context,
        "notes": notes[:10]  # Limit notes to top 10
    }

