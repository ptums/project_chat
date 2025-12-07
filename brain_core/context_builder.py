"""
Project context builder for injecting conversation memory into chat prompts.
Builds context directly from project_knowledge and conversation_index entries.

For DAAS project, uses custom retrieval rules:
- Single-dream mode: Quoted title detection and title-based matching
- Pattern-based mode: Vector similarity search using embeddings
"""
import logging
import os
import threading
from typing import Dict, List, Optional, Any

from .db import get_conn
from .memory import fetch_project_knowledge

logger = logging.getLogger(__name__)

# MCP client manager (lazy initialization)
_mcp_clients: Dict[str, Any] = {}
_mcp_clients_lock = threading.Lock()


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


def _get_mcp_client(server_name: str, server_config: Dict[str, Any]):
    """
    Get or create MCP client for a server (thread-safe).
    
    Args:
        server_name: Name of the MCP server
        server_config: Server configuration dict
        
    Returns:
        MCPClient instance or None if error
    """
    global _mcp_clients
    
    with _mcp_clients_lock:
        if server_name in _mcp_clients:
            client = _mcp_clients[server_name]
            # Check if client is still valid
            if hasattr(client, '_is_process_alive') and client._is_process_alive():
                return client
            # Remove dead client
            del _mcp_clients[server_name]
        
        # Create new client
        try:
            from .mcp_client import MCPClient
            client = MCPClient(
                server_name=server_name,
                command=server_config["command"],
                args=server_config.get("args", []),
                env=server_config.get("env", {}),
                cwd=server_config.get("cwd")
            )
            
            # Initialize client
            if client.initialize():
                _mcp_clients[server_name] = client
                return client
            else:
                logger.warning(f"Failed to initialize MCP client for '{server_name}'")
                return None
        except Exception as e:
            logger.error(f"Error creating MCP client for '{server_name}': {e}")
            return None


def _get_mcp_resources_for_project(project: str, user_message: str) -> List[Dict[str, Any]]:
    """
    Get relevant MCP resources for a project.
    
    Args:
        project: Project tag
        user_message: User message for keyword matching
        
    Returns:
        List of relevant resource dicts
    """
    try:
        from .mcp_config import get_mcp_config
        
        mcp_config = get_mcp_config()
        server_names = mcp_config.get_servers_for_project(project)
        
        if not server_names:
            return []
        
        relevant_resources = []
        user_words = set(user_message.lower().split())
        
        for server_name in server_names:
            try:
                server_config = mcp_config.get_server_config(server_name)
                if not server_config:
                    continue
                
                client = _get_mcp_client(server_name, server_config)
                if not client:
                    continue
                
                # List resources
                resources = client.list_resources()
                
                # Match resources by keywords
                for resource in resources:
                    resource_name = resource.get("name", "").lower()
                    resource_desc = resource.get("description", "").lower()
                    
                    # Simple keyword matching
                    resource_text = f"{resource_name} {resource_desc}"
                    matches = sum(1 for word in user_words if word in resource_text)
                    
                    if matches > 0:
                        relevant_resources.append({
                            "server": server_name,
                            "resource": resource,
                            "score": matches
                        })
            except Exception as e:
                logger.warning(f"Error getting MCP resources from '{server_name}': {e}")
                continue
        
        # Sort by relevance score and return top 5
        relevant_resources.sort(key=lambda x: x["score"], reverse=True)
        return relevant_resources[:5]
        
    except Exception as e:
        logger.warning(f"Error getting MCP resources for project '{project}': {e}")
        return []


def _get_mcp_context_for_project(project: str, user_message: str) -> Optional[str]:
    """
    Get MCP context string for a project.
    
    Args:
        project: Project tag
        user_message: User message
        
    Returns:
        Context string with MCP resources, or None
    """
    resources = _get_mcp_resources_for_project(project, user_message)
    
    if not resources:
        return None
    
    try:
        from .mcp_config import get_mcp_config
        
        mcp_config = get_mcp_config()
        context_parts = []
        
        for item in resources:
            server_name = item["server"]
            resource = item["resource"]
            uri = resource.get("uri")
            
            if not uri:
                continue
            
            server_config = mcp_config.get_server_config(server_name)
            if not server_config:
                continue
            
            client = _get_mcp_client(server_name, server_config)
            if not client:
                continue
            
            # Read resource content
            content = client.read_resource(uri)
            if content:
                resource_name = resource.get("name", uri)
                context_parts.append(f"From {resource_name}:\n{content[:1000]}...")  # Limit content length
        
        if context_parts:
            return "\n\n---\n\n".join(context_parts)
        
    except Exception as e:
        logger.warning(f"Error building MCP context for project '{project}': {e}")
    
    return None


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
            
            # Get MCP resources for DAAS (e.g., meditation notes)
            mcp_context = None
            try:
                mcp_context = _get_mcp_context_for_project(project, user_message)
            except Exception as e:
                logger.warning(f"MCP context integration failed for DAAS: {e}")
            
            # If we have dreams from DAAS retrieval, use them
            if daas_result.get('dreams'):
                # Build context from DAAS retrieval result
                context_parts = []
                notes = []
                
                # Add MCP resources if available
                if mcp_context:
                    context_parts.append(f"Here are relevant resources:\n\n{mcp_context}")
                    notes.append("MCP resources: Retrieved relevant external resources")
                
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
                    context += "\n\nUse this information to answer my new question in a way that is:\n"
                    context += "- consistent with the project goals and constraints\n"
                    context += "- consistent with prior decisions where appropriate\n"
                    context += "- willing to say \"I don't know\" if something is unclear."
                    context += "- keep it short and concise."
                    context += "- keep it easy to understand."
                    context += "- if you think I made a mistake in my prompt, please share don't agree with me"
                    
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
            
            # Get MCP resources for THN
            mcp_context = None
            try:
                mcp_context = _get_mcp_context_for_project(project, user_message)
            except Exception as e:
                logger.warning(f"MCP context integration failed for THN: {e}")
            
            if code_context:
                # Build context with code and project knowledge
                context_parts = []
                notes = []
                
                # Add MCP resources if available
                if mcp_context:
                    context_parts.append(f"Here are relevant resources:\n\n{mcp_context}")
                    notes.append("MCP resources: Retrieved relevant external resources")
                
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
                context += "\n\nUse this information to answer my question. Focus on the actual code when providing technical guidance."
                context += "\n\nWhen explaining technical concepts:"
                context += "\n- Use the actual code examples from the codebase"
                context += "\n- Explain how the code works, not just what it does"
                context += "\n- Identify patterns and best practices visible in the code"
                context += "\n- If asked for learning projects, suggest practical exercises based on the codebase patterns"
                context += "\n- If asked for lesson plans, structure them around the actual code examples"
                context += "\n\nKeep responses:\n"
                context += "- short and concise\n"
                context += "- easy to understand\n"
                context += "- based on the actual codebase when possible\n"
                context += "- educational and helpful for learning\n"
                context += "- willing to say \"I don't know\" if something is unclear"
                
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
    
    # MCP resource integration for project-specific servers
    mcp_context = None
    try:
        mcp_context = _get_mcp_context_for_project(project, user_message)
    except Exception as e:
        logger.warning(f"MCP context integration failed for project '{project}': {e}")
    
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
    
    # Add MCP resources if available
    if mcp_context:
        context_parts.append(f"Here are relevant resources from external sources:\n\n{mcp_context}")
        notes.append("MCP resources: Retrieved relevant external resources")
    
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
    context += "\n\nUse this information to answer my new question in a way that is:\n"
    context += "- consistent with the project goals and constraints\n"
    context += "- consistent with prior decisions where appropriate\n"
    context += "- willing to say \"I don't know\" if something is unclear."
    context += "- keep it short and concise."
    context += "- keep it easy to understand."
    context += "- if you think I made a mistake in my prompt, please share don't agree with me"
    
    logger.debug(f"Built project context for {project} with {len(top_memories)} memories and {len(knowledge_summaries)} knowledge entries")
    
    return {
        "context": context,
        "notes": notes[:10]  # Limit notes to top 10
    }

