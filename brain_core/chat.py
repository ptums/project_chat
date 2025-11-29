# brain_core/chat.py
import datetime
import logging

from .config import client, OPENAI_MODEL, MOCK_MODE
from .db import save_message, load_conversation_messages
from .memory import get_project_context
from .context_builder import build_project_context
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

    # Build project-aware context from conversation_index (if available)
    indexed_context = {}
    try:
        indexed_context = build_project_context(project, user_text)
    except Exception as e:
        # Log but don't fail - fallback to existing behavior
        logger.warning(f"Failed to build indexed context for project {project}: {e}")

    # Only static + snippet context included now
    project_context = get_project_context(project, conversation_id, limit_messages=80)

    # Load conversation history
    history = load_conversation_messages(conversation_id, limit=50)

    # Build messages for OpenAI
    messages = []

    # Add indexed context if available (from conversation_index)
    if indexed_context and indexed_context.get("context"):
        context_msg = (
            f"You are my assistant for project {project}. "
            f"Here is relevant context from prior conversations:\n\n"
            f"{indexed_context['context']}"
        )
        if indexed_context.get("notes"):
            context_msg += "\n\nKey notes:\n" + "\n".join(
                f"- {note}" for note in indexed_context["notes"]
            )
        messages.append({"role": "system", "content": context_msg})

    # Add existing project context (from memory.py)
    if project_context:
        messages.append({"role": "system", "content": project_context})

    base_system = (
        "You are an assistant helping the user with their personal projects "
        "(THN, DAAS, FF, 700B, or general). Be practical and concise."
    )
    messages.append({"role": "system", "content": base_system})
    messages.extend(history)

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
                
                # Accumulate usage data if available
                if hasattr(chunk, 'usage') and chunk.usage:
                    prompt_tokens = getattr(chunk.usage, 'prompt_tokens', prompt_tokens)
                    completion_tokens = getattr(chunk.usage, 'completion_tokens', completion_tokens)
                    total_tokens = getattr(chunk.usage, 'total_tokens', total_tokens)
                
                # Track model from response
                if hasattr(chunk, 'model') and chunk.model:
                    model = chunk.model
            
            # Track usage after streaming completes
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
                except Exception as e:
                    logger.warning(f"Failed to track streaming usage: {e}")
            
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
