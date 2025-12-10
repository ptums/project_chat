# brain_core/chat.py
import datetime
import logging

from .config import client, OPENAI_MODEL, MOCK_MODE
from .db import save_message, load_conversation_messages
from .memory import get_project_context
from .context_builder import build_project_context, build_project_system_prompt
from .usage_tracker import (
    get_session_tracker,
    calculate_cost,
    get_model_pricing,
)

logger = logging.getLogger(__name__)


def normalize_project_tag(tag: str) -> str:
    tag = (tag or "").strip().upper()
    if tag in ("THN", "DAAS", "FF", "700B"):
        return tag
    return "general"


def chat_turn(conversation_id, user_text: str, project: str, stream: bool = False):
    # Save user message
    save_message(conversation_id, "user", user_text)

    # Load conversation history first to check if this is the first message
    history = load_conversation_messages(conversation_id, limit=50)
    
    # Extract note reads from history (system messages with note_read meta)
    note_reads = []
    other_messages = []
    for msg in history:
        meta = msg.get("meta", {})
        if meta.get("note_read") and msg.get("role") == "system":
            note_reads.append(msg)
        else:
            other_messages.append(msg)
    
    # Check if this is the first user message (no user/assistant messages in history)
    is_first_message = len(other_messages) == 0

    # Build project-aware context from conversation_index (if available)
    # Skip RAG generation for THN if not first message to save tokens
    indexed_context = {}
    if not (project.upper() == "THN" and not is_first_message):
        try:
            indexed_context = build_project_context(project, user_text)
        except Exception as e:
            # Log but don't fail - fallback to existing behavior
            logger.warning(f"Failed to build indexed context for project {project}: {e}")

    # Only static + snippet context included now
    project_context = get_project_context(project, conversation_id, limit_messages=80)
    
    # Build messages for OpenAI
    messages = []

    # Message order: system prompt → RAG context → note reads → history
    
    # 1. System prompt (base + project extension + RAG for THN on first message only) - FIRST
    # For THN, RAG context is included directly in the system prompt only on first message
    include_rag = project.upper() == "THN" and is_first_message
    system_prompt = build_project_system_prompt(project, user_text if include_rag else "")
    
    # Log RAG inclusion status for verification
    if project.upper() == "THN":
        if include_rag:
            logger.info(f"THN RAG included in system prompt (first message, length: {len(system_prompt)} chars)")
        else:
            logger.debug(f"THN RAG skipped (not first message, is_first_message={is_first_message})")
    else:
        logger.debug(f"System prompt for project {project} (length: {len(system_prompt)} chars)")
    
    # Uncomment the line below to see the full system prompt in logs:
    # logger.info(f"System prompt content:\n{system_prompt}")
    messages.append({"role": "system", "content": system_prompt})

    # 2. Project context from RAG (if available and not THN) - SECOND
    # THN RAG is now included in system prompt above, so skip here
    if project.upper() != "THN" and indexed_context and indexed_context.get("context"):
        # RAG content is self-explanatory, no verbose wrapper needed
        context_msg = indexed_context['context']
        if indexed_context.get("notes"):
            context_msg += "\n\nKey sources:\n" + "\n".join(
                f"- {note}" for note in indexed_context["notes"]
            )
        messages.append({"role": "system", "content": context_msg})

    # Add existing project context (from memory.py) - also RAG context
    if project_context:
        messages.append({"role": "system", "content": project_context})
    
    # Add note reads first (most recent first) so they're fresh in context
    if note_reads:
        # Get the most recent note read (last in list since history is chronological)
        most_recent_note = note_reads[-1]
        note_content = most_recent_note.get("content", "")
        # Extract just the note content (skip the header)
        if "[Note loaded:" in note_content:
            note_parts = note_content.split("\n\n", 1)
            if len(note_parts) > 1:
                note_content = note_parts[1]  # Get content after header
        messages.append({
            "role": "system",
            "content": f"The user has loaded a note for discussion. Here is the note content:\n\n{note_content}\n\nYou can now reference and discuss this note naturally in the conversation."
        })
    
    # Add other conversation messages
    messages.extend(other_messages)

    # Query OpenAI
    if stream:
        # Streaming mode: yield chunks as they arrive
        full_response = ""
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            stream=True,
        )
        
        # Track usage for streaming (accumulate from chunks)
        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0
        model = OPENAI_MODEL
        
        try:
            for chunk in response:
                # Yield content chunks
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content
                
                # Check if this is the final chunk (has finish_reason)
                # OpenAI sends usage data in the final chunk when streaming completes
                is_final_chunk = (
                    chunk.choices and 
                    len(chunk.choices) > 0 and 
                    hasattr(chunk.choices[0], 'finish_reason') and 
                    chunk.choices[0].finish_reason is not None
                )
                
                # Accumulate usage data if available
                # OpenAI streaming API sends usage in the final chunk (may not have content)
                # The usage object is directly on the chunk
                if hasattr(chunk, 'usage') and chunk.usage is not None:
                    # Extract usage data from chunk
                    usage_obj = chunk.usage
                    if hasattr(usage_obj, 'prompt_tokens') and usage_obj.prompt_tokens is not None:
                        prompt_tokens = usage_obj.prompt_tokens
                    if hasattr(usage_obj, 'completion_tokens') and usage_obj.completion_tokens is not None:
                        completion_tokens = usage_obj.completion_tokens
                    if hasattr(usage_obj, 'total_tokens') and usage_obj.total_tokens is not None:
                        total_tokens = usage_obj.total_tokens
                    logger.debug(f"Usage data received in chunk: prompt={prompt_tokens}, completion={completion_tokens}, total={total_tokens}, is_final={is_final_chunk}")
                elif is_final_chunk:
                    # Log if final chunk but no usage data (this might indicate an issue)
                    logger.debug(f"Final chunk detected (finish_reason={chunk.choices[0].finish_reason}) but no usage data found")
                
                # Track model from response (may be in any chunk)
                if hasattr(chunk, 'model') and chunk.model:
                    model = chunk.model
            
            # Track usage after streaming completes
            # Log if usage tracking will happen
            if not MOCK_MODE:
                if total_tokens > 0:
                    logger.debug(f"Recording usage: prompt={prompt_tokens}, completion={completion_tokens}, total={total_tokens}, model={model}")
                else:
                    # This is expected in some cases - OpenAI may not always send usage in streaming mode
                    # Log at debug level instead of warning to avoid noise
                    logger.debug("Streaming completed but no usage data was captured. This may be normal for some API configurations.")
            
            # Record usage if we have valid token data
            if not MOCK_MODE and total_tokens > 0 and prompt_tokens > 0:
                try:
                    cost = calculate_cost(prompt_tokens, completion_tokens, model)
                    tracker = get_session_tracker()
                    tracker.record_usage(
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        total_tokens=total_tokens,
                        model=model,
                        cost=cost,
                    )
                except Exception as e:
                    logger.warning(f"Failed to track streaming usage: {e}")
                    logger.debug(f"Usage tracking error details: prompt_tokens={prompt_tokens}, completion_tokens={completion_tokens}, total_tokens={total_tokens}, model={model}", exc_info=True)
            
            # Save complete response after streaming
            meta = {
                "model": "mock" if MOCK_MODE else model,
                "created_at": datetime.datetime.utcnow().isoformat() + "Z",
                "mock_mode": MOCK_MODE,
            }
            save_message(conversation_id, "assistant", full_response, meta=meta)
            
            # Return full response for compatibility
            return full_response
            
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            # Try to record usage even if streaming was interrupted
            if not MOCK_MODE and total_tokens > 0:
                try:
                    cost = calculate_cost(prompt_tokens, completion_tokens, model)
                    tracker = get_session_tracker()
                    tracker.record_usage(
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        total_tokens=total_tokens,
                        model=model,
                        cost=cost,
                    )
                    logger.debug(f"Recorded usage after streaming error: prompt={prompt_tokens}, completion={completion_tokens}, total={total_tokens}")
                except Exception as usage_error:
                    logger.warning(f"Failed to track usage after streaming error: {usage_error}")
            # Save partial response if any was accumulated
            if full_response:
                meta = {
                    "model": "mock" if MOCK_MODE else OPENAI_MODEL,
                    "created_at": datetime.datetime.utcnow().isoformat() + "Z",
                    "mock_mode": MOCK_MODE,
                    "error": str(e),
                }
                save_message(conversation_id, "assistant", full_response, meta=meta)
            raise
    else:
        # Non-streaming mode (existing behavior)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
        )
        answer = response.choices[0].message.content

        # Track usage (only for successful API calls, not mock mode)
        # Handle failed/interrupted calls by only tracking when response is successful
        if not MOCK_MODE:
            try:
                # Check if usage data is available
                if hasattr(response, 'usage') and response.usage:
                    usage = response.usage
                    prompt_tokens = getattr(usage, 'prompt_tokens', 0)
                    completion_tokens = getattr(usage, 'completion_tokens', 0)
                    total_tokens = getattr(usage, 'total_tokens', 0)
                    model = getattr(response, 'model', OPENAI_MODEL)
                    
                    # Validate usage data before tracking
                    if prompt_tokens >= 0 and completion_tokens >= 0 and total_tokens >= 0:
                        # Calculate cost
                        cost = calculate_cost(prompt_tokens, completion_tokens, model)
                        
                        # Record in session tracker
                        tracker = get_session_tracker()
                        tracker.record_usage(
                            prompt_tokens=prompt_tokens,
                            completion_tokens=completion_tokens,
                            total_tokens=total_tokens,
                            model=model,
                            cost=cost,
                        )
                # If usage data is missing, skip tracking (graceful degradation)
                # This handles edge case where usage might not be available
            except Exception as e:
                # Log error but don't fail the API call
                # This handles any unexpected errors in usage tracking
                logger.warning(f"Failed to track usage: {e}")

        # Save assistant reply
        meta = {
            "model": "mock" if MOCK_MODE else OPENAI_MODEL,
            "created_at": datetime.datetime.utcnow().isoformat() + "Z",
            "mock_mode": MOCK_MODE,
        }
        save_message(conversation_id, "assistant", answer, meta=meta)

        return answer
