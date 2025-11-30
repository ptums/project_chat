# chat_cli.py
import datetime
import itertools
import logging
import signal
import sys
import threading
import time
import uuid

from psycopg2 import OperationalError

logger = logging.getLogger(__name__)

from brain_core.db import create_conversation
from brain_core.memory import get_project_context, semantic_search_snippets
from brain_core.chat import chat_turn, normalize_project_tag
from brain_core.usage_tracker import get_session_tracker, get_model_pricing
from brain_core.config import MOCK_MODE
from brain_core.conversation_indexer import (
    index_session,
    list_memories,
    view_memory,
    refresh_memory,
    delete_memory,
)
from brain_core.ollama_client import OllamaError

# ===== Colors & UI =====

RESET = "\033[0m"
BOLD = "\033[1m"

COLOR_CODES = {
    "purple": "\033[95m",
    "green": "\033[92m",
    "orange": "\033[38;5;208m",
    "yellow": "\033[93m",
    "cyan": "\033[96m",
    "grey": "\033[90m",
}

# Project visual theme: color + emoji + label
PROJECT_STYLE = {
    "DAAS":   {"color": "purple", "emoji": "🟣", "label": "DAAS"},
    "THN":    {"color": "green",  "emoji": "🟢", "label": "THN"},
    "FF":     {"color": "orange", "emoji": "🟠", "label": "FF"},
    "700B":   {"color": "yellow", "emoji": "🟡", "label": "700B"},
    "general": {"color": "cyan",  "emoji": "🔵", "label": "GENERAL"},
}


def color_text(text: str, color_name: str, bold: bool = False) -> str:
    code = COLOR_CODES.get(color_name, "")
    if bold:
        return f"{BOLD}{code}{text}{RESET}"
    return f"{code}{text}{RESET}"


def get_project_style(project: str):
    return PROJECT_STYLE.get(project, PROJECT_STYLE["general"])


# ===== Spinner =====


def spinner(stop_event: threading.Event, label: str, color: str):
    """Simple CLI spinner that runs until stop_event is set."""
    spin_chars = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
    while not stop_event.is_set():
        ch = next(spin_chars)
        text = f"{label} {ch}"
        sys.stdout.write("\r" + color_text(text.ljust(60), color))
        sys.stdout.flush()
        time.sleep(0.09)
    # clear line
    sys.stdout.write("\r" + " " * 60 + "\r")
    sys.stdout.flush()


# ===== Helpers =====


def save_current_conversation(conv_id: uuid.UUID, current_project: str, preserve_project: bool = False) -> bool:
    """
    Save current conversation by calling indexing function.
    
    Args:
        conv_id: UUID of the conversation to save
        current_project: Current project context (used as override if conversation is "general")
        preserve_project: If True, don't allow Ollama to override the conversation's project
                         (used when saving before project switch to preserve original project)
    
    Returns:
        True if save succeeded, False if failed
    """
    # T018: Add logging for auto-save operations
    logger.info(f"Auto-save triggered for conversation {conv_id} in project {current_project} (preserve_project={preserve_project})")
    
    style = get_project_style(current_project)
    
    # Run indexing in a thread with spinner
    stop_spinner = threading.Event()
    spinner_thread = threading.Thread(
        target=spinner,
        args=(stop_spinner, "Indexing conversation...", style["color"]),
        daemon=True,
    )
    spinner_thread.start()
    
    indexed_data = None
    error_occurred = False
    error_message = None
    
    try:
        # If preserve_project is True, pass preserve_project flag to prevent Ollama from overriding
        # Otherwise, pass current_project as override when conversation is "general"
        if preserve_project:
            indexed_data = index_session(conv_id, override_project=None, preserve_project=True)
        else:
            indexed_data = index_session(conv_id, override_project=current_project, preserve_project=False)
        
        # Handle case where indexing failed but conversation should still be saved
        if indexed_data is None:
            error_occurred = True
            error_message = "Indexing failed, but conversation saved"
            logger.warning(f"Indexing failed for conversation {conv_id}, but conversation is still saved")
            print(color_text("⚠ Indexing failed, but conversation saved.", "orange"))
        else:
            # Verify it was actually saved
            from brain_core.conversation_indexer import view_memory
            saved_memory = view_memory(conv_id)
            if saved_memory:
                logger.debug(f"Verified saved to DB - Project: {saved_memory['project']}, Title: {saved_memory['title']}")
            else:
                logger.warning("Indexing completed but memory not found in database!")
    except OllamaError as e:
        # T014: Error handling for OllamaError
        error_occurred = True
        error_message = f"Ollama connection error: {str(e)}"
        logger.exception("Ollama error during indexing")
    except ValueError as e:
        # T014: Error handling for ValueError
        error_occurred = True
        error_message = f"Indexing validation error: {str(e)}"
        logger.exception("Validation error during indexing")
    except Exception as e:
        # T014: Error handling for generic Exception
        error_occurred = True
        error_message = f"Unexpected error: {str(e)}"
        logger.exception("Unexpected error during indexing")
    finally:
        # Stop spinner
        stop_spinner.set()
        spinner_thread.join(timeout=0.5)
    
    # Display result
    if error_occurred:
        # T014: Display user-friendly warning message
        print(
            color_text(
                f"⚠ Save failed: {error_message}",
                "orange",
                bold=True,
            )
        )
        logger.warning(f"Auto-save failed for conversation {conv_id}: {error_message}")
        return False
    elif indexed_data is None:
        # Indexing failed but conversation is still saved
        logger.warning(f"Indexing failed for conversation {conv_id}, but conversation is still saved")
        return True  # Conversation is saved, just not indexed
    else:
        # Show more details about what was indexed
        indexed_project = indexed_data.get('project', current_project)
        print(
            color_text(
                f"✓ Indexed: {indexed_data.get('title', 'Untitled')} "
                f"[{indexed_project}]",
                style["color"],
                bold=True,
            )
        )
        logger.info(f"Successfully saved conversation {conv_id} for project {indexed_project}")
        return True


def debug_project_context(project: str, conversation_id: uuid.UUID):
    """Print out the current project context (/context)."""
    ctx = get_project_context(project, conversation_id, limit_messages=80)
    if not ctx:
        print(color_text(f"[context] No project context found for {project}", "grey"))
        return
    print(color_text(f"[context] Project={project}", "grey"))
    print(color_text("-" * 60, "grey"))
    print(ctx)
    print(color_text("-" * 60, "grey"))


def run_search_command(project: str, query: str):
    """Run a text-only deep search over messages (/search)."""
    style = get_project_style(project)
    header = f"[search:{style['label']}] {query}"
    print(color_text(header, style["color"], bold=True))
    print(color_text("-" * 60, "grey"))

    hits = semantic_search_snippets(project, query, limit=10)
    if not hits:
        print(color_text("No matches found.", "grey"))
        print(color_text("-" * 60, "grey"))
        return

    for idx, (proj, snippet) in enumerate(hits, start=1):
        proj_style = get_project_style(proj if proj in PROJECT_STYLE else "general")
        proj_tag = color_text(f"[{proj_style['label']}]", proj_style["color"], bold=True)
        print(f"{color_text(str(idx) + '.', style['color'], bold=True)} {proj_tag} {snippet}")

    print(color_text("-" * 60, "grey"))


def read_large_text_block(end_token: str = "EOF") -> str:
    """
    Read large text block from stdin until EOF (Ctrl+D) or end token.
    Uses sys.stdin.readline() in a loop to read line by line. readline() can
    handle much longer lines than input() and doesn't have the same terminal
    buffer limitations. Continues reading until end token is found on its own line.
    
    Args:
        end_token: Token that signals end of input (default: "EOF")
        
    Returns:
        Complete text block as string, or empty string if cancelled
        
    Raises:
        KeyboardInterrupt: If user cancels with Ctrl+C
    """
    lines: list[str] = []
    try:
        # Use readline() in unbuffered mode if possible to avoid truncation
        # readline() can handle much longer lines than input()
        while True:
            try:
                # Read a line - readline() returns empty string on EOF
                # This can handle very long lines (much longer than input() limit)
                line = sys.stdin.readline()
                
                # EOF reached (empty string from readline means EOF)
                if not line:
                    break
                
                # Validate UTF-8 encoding
                try:
                    line.encode('utf-8').decode('utf-8')
                except (UnicodeDecodeError, UnicodeEncodeError):
                    print(
                        color_text(
                            "Error: Invalid UTF-8 encoding detected. Please ensure your input is valid UTF-8 text.",
                            "orange",
                            bold=True,
                        )
                    )
                    return ""
                
                # Check if this line is the end token
                # Strip whitespace (including newline/carriage return) for comparison
                stripped_line = line.rstrip('\n\r\t ')
                if stripped_line == end_token:
                    # Found the end token on its own line, stop reading
                    break
                
                # Accumulate the line (remove trailing newline, we'll add it back when joining)
                lines.append(line.rstrip('\n\r'))
                
            except EOFError:
                # EOF reached
                break
            except KeyboardInterrupt:
                # User cancelled with Ctrl+C
                print("\n" + color_text("Input cancelled.", "grey"))
                return ""
                
    except KeyboardInterrupt:
        # User cancelled with Ctrl+C
        print("\n" + color_text("Input cancelled.", "grey"))
        return ""
    except Exception as e:
        # Handle encoding or other errors
        print(color_text(f"Error reading input: {e}", "orange", bold=True))
        return ""
    
    # Join all lines, preserving original line structure
    result = '\n'.join(lines)
    return result


def read_multiline_block_vim() -> str:
    """
    Read large text block using vim/vi editor.
    Opens a temporary file in vim, user edits and saves, then content is read.
    This bypasses all terminal line length limits.
    
    Returns:
        Complete text block as string, or empty string if cancelled/error
    """
    import tempfile
    import subprocess
    import os
    
    # Create temporary file
    temp_fd, temp_path = tempfile.mkstemp(suffix='.txt', prefix='chat_input_')
    
    try:
        # Close the file descriptor (vim will open it)
        os.close(temp_fd)
        
        # Try to find vim or vi
        editor = None
        for ed in ['vim', 'vi', 'nano']:
            try:
                subprocess.run([ed, '--version'], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL,
                             timeout=1)
                editor = ed
                break
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        
        if not editor:
            print(color_text("Error: No suitable editor (vim/vi/nano) found.", "orange", bold=True))
            os.unlink(temp_path)
            return ""
        
        print(
            color_text(
                f"Opening {editor} for input. Paste your text, save and quit (:wq in vim, Ctrl+X in nano).",
                "grey",
            )
        )
        sys.stdout.flush()
        
        # Open editor
        try:
            subprocess.run([editor, temp_path], check=True)
        except subprocess.CalledProcessError:
            print(color_text("Editor was cancelled or exited with error.", "orange", bold=True))
            os.unlink(temp_path)
            return ""
        except KeyboardInterrupt:
            print(color_text("\nEditor cancelled.", "grey"))
            os.unlink(temp_path)
            return ""
        
        # Read the file content
        try:
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            print(color_text("Error: File contains invalid UTF-8 text.", "orange", bold=True))
            os.unlink(temp_path)
            return ""
        
        # Strip trailing whitespace but preserve structure
        # Don't strip leading/trailing completely as user might want that
        content = content.rstrip()
        
        # Show content size for user feedback
        if content:
            char_count = len(content)
            print(
                color_text(
                    f"Read {char_count:,} characters from editor.",
                    "grey",
                )
            )
        
        return content
        
    finally:
        # Clean up temp file
        try:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        except Exception:
            pass  # Ignore cleanup errors


def read_multiline_block(end_token: str = "EOF", use_vim: bool = False) -> str:
    """
    Multi-line paste mode:
    - User types /paste (or /block)
    - Then pastes any number of lines
    - Ends the block with a line containing only end_token (default: EOF)
    
    If use_vim is True, opens vim/vi editor instead of reading from stdin.
    This bypasses terminal line length limits.
    
    This function now uses read_large_text_block() for large text support.
    """
    if use_vim:
        return read_multiline_block_vim()
    
    print(
        color_text(
            f"(paste mode) Paste your block now. End with a line containing only {end_token}",
            "grey",
        )
    )
    # Flush stdout to ensure prompt is displayed before reading
    sys.stdout.flush()
    return read_large_text_block(end_token=end_token)


def read_file_content(filepath: str) -> tuple[str | None, str | None]:
    """
    Read content from a file.
    
    Args:
        filepath: Path to the file to read
        
    Returns:
        Tuple of (content, error_message). If successful, content is the file text
        and error_message is None. If error, content is None and error_message
        describes the error.
    """
    import os
    
    try:
        # Expand user home directory if path starts with ~
        expanded_path = os.path.expanduser(filepath)
        
        # Check if file exists
        if not os.path.exists(expanded_path):
            return None, f"File not found: {filepath}"
        
        # Check if it's a file (not a directory)
        if not os.path.isfile(expanded_path):
            return None, f"Path is not a file: {filepath}"
        
        # Read file content
        with open(expanded_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return content, None
        
    except PermissionError:
        return None, f"Permission denied: {filepath}"
    except UnicodeDecodeError:
        return None, f"File is not valid UTF-8 text: {filepath}"
    except Exception as e:
        return None, f"Error reading file: {e}"


def handle_command(text: str, current_project: str, conversation_id: uuid.UUID):
    """
    Handle slash commands. Returns:
      (new_project, handled, message_to_show, special)

    special:
      - None        → just print message_to_show (if any)
      - "context"   → run /context
      - "search"    → run /search
      - "multiline" → enter paste mode (/paste)
      - "readfile"  → read file and process content
    """
    raw = text.strip()
    if not raw.startswith("/"):
        return current_project, False, "", None

    parts = raw[1:].split()
    cmd = parts[0].lower() if parts else ""
    arg = " ".join(parts[1:]) if len(parts) > 1 else ""

    # project change
    if cmd in ("project", "tag"):
        if not arg:
            return current_project, True, "Usage: /project THN|DAAS|FF|700B|general", None
        new_project = normalize_project_tag(arg)
        # Return special flag "project_switch" to trigger save and title prompt flow
        return new_project, True, "", "project_switch"

    if cmd in ("thn", "daas", "ff", "700b", "general"):
        new_project = normalize_project_tag(cmd)
        # Return special flag "project_switch" to trigger save and title prompt flow
        return new_project, True, "", "project_switch"

    # context
    if cmd in ("context", "ctx"):
        return current_project, True, "", "context"

    # search
    if cmd in ("search", "s"):
        if not arg:
            return current_project, True, "Usage: /search your query", None
        return current_project, True, arg, "search"

    # multiline paste mode
    if cmd in ("paste", "block", "ml"):
        # Check if user wants vim mode (e.g., /paste vim or /paste --vim)
        use_vim = len(parts) > 1 and parts[1].lower() in ("vim", "vi", "--vim", "--vi", "-v")
        return current_project, True, "vim" if use_vim else "", "multiline"

    # read file
    if cmd in ("readfile", "read", "file"):
        if not arg:
            return current_project, True, "Usage: /readfile <filename>", None
        return current_project, True, arg, "readfile"

    # save/index conversation
    if cmd in ("save", "index"):
        # Optional: allow specifying a different session_id
        # For now, just use current conversation_id
        return current_project, True, "", "save"

    # memory management
    if cmd == "memory":
        if not arg:
            return current_project, True, "Usage: /memory [list|view <id>|refresh <id>|delete <id>]", None
        subcmd = arg.split()[0].lower() if arg.split() else ""
        subarg = " ".join(arg.split()[1:]) if len(arg.split()) > 1 else ""
        return current_project, True, f"{subcmd}|{subarg}", "memory"

    # unknown command
    return current_project, True, f"Unknown command: {cmd}", None


def print_banner():
    bar = "=" * 52
    title = "AI Brain local storage (project_chat)"
    print(color_text(bar, "cyan", bold=True))
    print(color_text(f"= {title.ljust(48)}=", "cyan", bold=True))
    print(color_text(bar, "cyan", bold=True))
    print()


def display_usage_summary():
    """Display usage summary for the current session."""
    import logging
    logger = logging.getLogger(__name__)
    
    tracker = get_session_tracker()
    summary = tracker.get_summary()
    
    # Debug logging to help diagnose usage tracking issues
    logger.debug(f"Usage summary: api_call_count={summary['api_call_count']}, total_tokens={summary['total_tokens']}, total_cost={summary['total_cost']}")
    
    # Check if mock mode was used
    if MOCK_MODE:
        summary["has_mock_mode"] = True
    
    # Handle no API calls
    if summary["api_call_count"] == 0:
        # Debug: Log if we expected API calls but got zero
        logger.debug("Usage summary shows zero API calls. This may indicate a tracking issue if API calls were actually made.")
        if summary["has_mock_mode"]:
            print(color_text("\nMock mode used - no API calls made.", "grey"))
        else:
            print(color_text("\nNo API calls made during this session.", "grey"))
        return
    
    # Format and display summary
    print(color_text("\n" + "=" * 70, "grey"))
    print(color_text("Session Usage Summary", "cyan", bold=True))
    print(color_text("=" * 70, "grey"))
    
    # Token counts
    print(f"Total Prompt Tokens:    {summary['total_prompt_tokens']:,}")
    print(f"Total Completion Tokens: {summary['total_completion_tokens']:,}")
    print(f"Total Tokens:            {summary['total_tokens']:,}")
    
    # Cost
    if summary["total_cost"] > 0:
        # Format cost with appropriate precision
        if summary["total_cost"] < 0.01:
            cost_str = f"${summary['total_cost']:.4f}"
        elif summary["total_cost"] < 1.0:
            cost_str = f"${summary['total_cost']:.3f}"
        else:
            cost_str = f"${summary['total_cost']:.2f}"
        print(f"Estimated Cost:         {cost_str}")
    else:
        # Check if any models had unknown pricing
        unknown_models = [
            model for model in summary["models_used"]
            if get_model_pricing(model) is None
        ]
        if unknown_models:
            print(
                color_text(
                    f"Estimated Cost:         Unknown (models: {', '.join(unknown_models)})",
                    "orange",
                )
            )
        else:
            print("Estimated Cost:         $0.00")
    
    # API call count
    print(f"API Calls:              {summary['api_call_count']}")
    
    # Models used
    if len(summary["models_used"]) == 1:
        print(f"Model:                  {summary['models_used'][0]}")
    else:
        print(f"Models Used:            {', '.join(summary['models_used'])}")
    
    print(color_text("=" * 70, "grey"))


def print_help_line():
    """Print available commands in a vertical list."""
    commands = [
        "/thn /daas /ff /700b /general /project TAG",
        "/context",
        "/search QUERY",
        "/paste [vim] (/block)",
        "/readfile <file>",
        "/save",
        "/memory [list|view <id>|refresh <id>|delete <id>]",
        "/exit",
    ]
    print(color_text("Commands:", "grey"))
    for cmd in commands:
        print(color_text(f"  {cmd}", "grey"))
    print()


def show_project_memory_blurb(project: str, limit: int = 3):
    """
    Show a truncated blurb of recent indexed memories for the project.
    
    Args:
        project: Project tag to show memories for
        limit: Number of recent memories to show (default: 3)
    """
    try:
        memories = list_memories(project=project, limit=limit)
        if not memories:
            return
        
        print(color_text("Recent project context:", "grey"))
        for mem in memories:
            title = mem["title"] or "Untitled"
            # Get memory snippet if available, otherwise use short summary
            mem_detail = view_memory(mem["session_id"])
            if mem_detail and mem_detail.get("memory_snippet"):
                snippet = mem_detail["memory_snippet"]
            elif mem_detail and mem_detail.get("summary_short"):
                snippet = mem_detail["summary_short"]
            else:
                snippet = None
            
            # Truncate snippet to ~100 characters
            if snippet:
                snippet = snippet[:100] + "..." if len(snippet) > 100 else snippet
                print(color_text(f"  • {title}: {snippet}", "grey"))
            else:
                print(color_text(f"  • {title}", "grey"))
        print()
    except Exception as e:
        # Silently fail - don't interrupt conversation startup
        logger.debug(f"Failed to load project memory blurb: {e}")


# ===== Main loop =====

# Module-level variables for signal handler access
_current_conv_id = None
_current_project_context = None
_is_streaming = False  # Flag to track if we're currently streaming
_interrupt_streaming = False  # Flag to signal streaming should be interrupted


def _signal_handler(signum, frame):
    """
    Handle Ctrl+C: 
    - If streaming: Set interrupt flag (streaming loop will check and raise KeyboardInterrupt)
    - If not streaming: Save conversation and exit
    """
    global _is_streaming, _interrupt_streaming
    
    if _is_streaming:
        # During streaming, set flag to interrupt
        # The streaming loop will check this flag and raise KeyboardInterrupt
        _interrupt_streaming = True
    else:
        # Not streaming, so exit the program
        print("\n" + color_text("Exiting.", "grey"))
        # Save conversation if conv_id and current_project are available
        # Preserve the conversation's actual project - don't let Ollama reclassify it
        if _current_conv_id and _current_project_context:
            try:
                save_current_conversation(_current_conv_id, _current_project_context, preserve_project=True)
            except Exception as e:
                logger.warning(f"Failed to save conversation on exit: {e}")
                print(color_text("⚠ Save failed during exit, but continuing...", "orange"))
        display_usage_summary()
        
        # Show model used in exit message
        tracker = get_session_tracker()
        summary = tracker.get_summary()
        if summary["models_used"]:
            models_str = ", ".join(sorted(summary["models_used"]))
            print(color_text(f"Bye. (Model: {models_str})", "grey"))
        else:
            print(color_text("Bye.", "grey"))
        sys.exit(0)


def main():
    # Declare global streaming flags for entire function
    global _is_streaming, _interrupt_streaming
    
    # Initialize usage tracker and set mock mode flag if applicable
    tracker = get_session_tracker()
    if MOCK_MODE:
        tracker.has_mock_mode = True
    
    print_banner()
    # T010-T011: Make title mandatory
    while True:
        title = input("Conversation title (required): ").strip()
        if not title:
            print(color_text("A title is required", "orange", bold=True))
            continue
        break

    initial_project_input = (
        input("Project tag [general/THN/DAAS/FF/700B] (default: general): ")
        .strip()
        or "general"
    )
    initial_project = normalize_project_tag(initial_project_input)

    try:
        conv_id = create_conversation(title=title, project=initial_project)
    except OperationalError as e:
        print(color_text(f"DB connection error: {e}", "orange", bold=True))
        sys.exit(1)

    current_project = initial_project
    style = get_project_style(current_project)
    
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, _signal_handler)
    
    # Update module-level variables for signal handler access
    global _current_conv_id, _current_project_context
    _current_conv_id = conv_id
    _current_project_context = current_project

    header = f"Started conversation {conv_id} [project={style['label']}] {style['emoji']}"
    print("\n" + color_text(header, style["color"], bold=True))
    
    # Show recent project memory blurbs
    show_project_memory_blurb(current_project, limit=3)
    
    print_help_line()

    while True:
        # Update module-level variables for signal handler access
        _current_conv_id = conv_id
        _current_project_context = current_project
        
        style = get_project_style(current_project)
        user_label = color_text(
            f"You ({style['label']}) {style['emoji']}:", style["color"], bold=True
        )
        ai_label = color_text(
            f"AI ({style['label']}) {style['emoji']}:", style["color"], bold=True
        )

        try:
            user_text = input(f"{user_label} ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n" + color_text("Exiting.", "grey"))
            # T009: Save before exit on Ctrl+C (handled by signal handler, but also here for EOFError)
            # T016: Handle save failures gracefully (warn but continue)
            # Preserve the conversation's actual project - don't let Ollama reclassify it
            try:
                save_current_conversation(conv_id, current_project, preserve_project=True)
            except Exception as e:
                logger.warning(f"Failed to save conversation on exit: {e}")
                print(color_text("⚠ Save failed during exit, but continuing...", "orange"))
            display_usage_summary()
            
            # Show model used in exit message
            tracker = get_session_tracker()
            summary = tracker.get_summary()
            if summary["models_used"]:
                models_str = ", ".join(sorted(summary["models_used"]))
                print(color_text(f"Bye. (Model: {models_str})", "grey"))
            else:
                print(color_text("Bye.", "grey"))
            break

        if not user_text:
            continue

        # Check for /exit BEFORE processing commands or sending to API
        if user_text.lower() in ("/exit", "/quit"):
            # T008: Save before exit
            # T016: Handle save failures gracefully (warn but continue)
            # Preserve the conversation's actual project - don't let Ollama reclassify it
            try:
                save_current_conversation(conv_id, current_project, preserve_project=True)
            except Exception as e:
                logger.warning(f"Failed to save conversation on exit: {e}")
                print(color_text("⚠ Save failed during exit, but continuing...", "orange"))
            display_usage_summary()
            
            # Show model used in exit message
            tracker = get_session_tracker()
            summary = tracker.get_summary()
            if summary["models_used"]:
                models_str = ", ".join(sorted(summary["models_used"]))
                print(color_text(f"Bye. (Model: {models_str})", "grey"))
            else:
                print(color_text("Bye.", "grey"))
            break

        # Check if input was truncated (common with large pastes)
        # If input contains newlines or is suspiciously cut off, suggest using /paste
        # Note: input() has line length limits, so large pastes should use /paste mode
        if "\n" in user_text:
            # User pasted multiline text - this might be truncated
            # Check if it looks incomplete (ends mid-word or abruptly)
            if len(user_text) > 500 and (user_text[-1].isalnum() or user_text.endswith("...")):
                print(
                    color_text(
                        "Note: Large paste detected. For best results with very large text blocks, "
                        "use /paste mode to ensure no truncation.",
                        "grey",
                    )
                )

        # commands
        new_project, handled, msg, special = handle_command(
            user_text, current_project, conv_id
        )

        if handled:
            # Handle project switch flow (T003-T007)
            if special == "project_switch":
                # STEP 1: Save current conversation
                # T015: Handle save failures gracefully (warn but continue)
                # When saving before project switch, preserve the conversation's actual project
                # Don't pass override_project to prevent Ollama from reclassifying "general" conversations
                save_success = save_current_conversation(conv_id, current_project, preserve_project=True)
                if not save_success:
                    logger.warning("Save failed during project switch, but continuing with switch")
                
                # STEP 2: Prompt for new title
                target_project = new_project  # Target project from handle_command
                style = get_project_style(target_project)
                while True:
                    try:
                        new_title = input(f"Conversation title for {style['label']} (required): ").strip()
                        if not new_title:
                            print(color_text("A title is required", "orange", bold=True))
                            continue
                        break
                    except (EOFError, KeyboardInterrupt):
                        # T017: Handle cancellation gracefully
                        print("\n" + color_text("Title input cancelled. Project switch aborted.", "orange", bold=True))
                        logger.info("Project switch cancelled by user during title input")
                        continue
                
                # STEP 3: Switch to new project context
                try:
                    new_conv_id = create_conversation(title=new_title, project=target_project)
                    conv_id = new_conv_id
                    current_project = target_project
                    # Update module-level variables for signal handler
                    _current_conv_id = conv_id
                    _current_project_context = current_project
                    style = get_project_style(current_project)
                    print(color_text(f"Switched active project context to {style['label']} {style['emoji']}", style["color"], bold=True))
                except OperationalError as e:
                    print(color_text(f"DB connection error: {e}", "orange", bold=True))
                    print(color_text("Project switch failed. Continuing with current conversation.", "orange"))
                    continue
                
                # STEP 4: Continue conversation with new conversation_id
                continue
            
            current_project = new_project
            style = get_project_style(current_project)

            if special == "context":
                debug_project_context(current_project, conv_id)
            elif special == "search":
                run_search_command(current_project, msg)
            elif special == "save":
                # Use the helper function for consistency
                save_current_conversation(conv_id, current_project)
            elif special == "memory":
                # Parse memory subcommand
                parts = msg.split("|")
                if len(parts) != 2:
                    print(color_text("Usage: /memory [list|view <id>|refresh <id>|delete <id>]", "orange"))
                    continue
                subcmd, subarg = parts[0], parts[1]
                style = get_project_style(current_project)
                
                if subcmd == "list":
                    # Debug: Show what project we're querying
                    print(color_text(f"Querying memories for project: {current_project}", "grey"))
                    memories = list_memories(project=current_project, limit=20)
                    if not memories:
                        print(color_text(f"No indexed memories found for {current_project}", "grey"))
                        # Debug: Check if there are any memories at all
                        all_memories = list_memories(project=None, limit=5)
                        if all_memories:
                            print(color_text(f"Found {len(all_memories)} memories in database (different project):", "grey"))
                            for mem in all_memories:
                                print(f"  Project: {mem['project']}, Title: {mem['title'] or 'Untitled'}")
                    else:
                        print(color_text(f"Indexed memories for {current_project}:", style["color"], bold=True))
                        print(color_text("-" * 80, "grey"))
                        for mem in memories:
                            title = mem["title"] or "Untitled"
                            date_str = mem["indexed_at"].strftime("%Y-%m-%d %H:%M") if mem["indexed_at"] else "N/A"
                            session_id = mem["session_id"]
                            # Show full UUID on its own line for easy copy/paste
                            print(f"  {session_id}")
                            print(f"    Title: {title[:60]}")
                            print(f"    Date:  {date_str}")
                            print()
                        print(color_text("-" * 80, "grey"))
                
                elif subcmd == "view":
                    if not subarg:
                        print(color_text("Usage: /memory view <session_id>", "orange"))
                        continue
                    try:
                        mem = view_memory(subarg)
                        if not mem:
                            print(color_text(f"Memory not found for session {subarg}", "orange"))
                        else:
                            print(color_text(f"Memory: {mem['title'] or 'Untitled'}", style["color"], bold=True))
                            print(color_text("-" * 60, "grey"))
                            print(f"Session ID: {mem['session_id']}")
                            print(f"Project: {mem['project']}")
                            print(f"Indexed: {mem['indexed_at']}")
                            print(f"Version: {mem['version']}")
                            print(f"Model: {mem['ollama_model']}")
                            if mem.get("summary_short"):
                                print(f"\nSummary: {mem['summary_short']}")
                            if mem.get("memory_snippet"):
                                print(f"\nMemory Snippet: {mem['memory_snippet']}")
                            if mem.get("tags"):
                                tags_str = ", ".join(mem["tags"]) if isinstance(mem["tags"], list) else str(mem["tags"])
                                print(f"\nTags: {tags_str}")
                            print(color_text("-" * 60, "grey"))
                    except Exception as e:
                        print(color_text(f"Error viewing memory: {e}", "orange", bold=True))
                
                elif subcmd == "refresh":
                    if not subarg:
                        print(color_text("Usage: /memory refresh <session_id>", "orange"))
                        continue
                    
                    # Run refresh with spinner
                    stop_spinner = threading.Event()
                    spinner_thread = threading.Thread(
                        target=spinner,
                        args=(stop_spinner, "Refreshing memory...", style["color"]),
                        daemon=True,
                    )
                    spinner_thread.start()
                    
                    indexed_data = None
                    error_occurred = False
                    error_message = None
                    
                    try:
                        indexed_data = refresh_memory(subarg)
                    except OllamaError as e:
                        error_occurred = True
                        error_message = f"Ollama connection error: {str(e)}"
                        logger.exception("Ollama error during memory refresh")
                    except ValueError as e:
                        error_occurred = True
                        error_message = f"Validation error: {str(e)}"
                        logger.exception("Validation error during memory refresh")
                    except Exception as e:
                        error_occurred = True
                        error_message = f"Unexpected error: {str(e)}"
                        logger.exception("Unexpected error during memory refresh")
                    finally:
                        # Stop spinner
                        stop_spinner.set()
                        spinner_thread.join(timeout=0.5)
                    
                    # Display result
                    if error_occurred:
                        print(
                            color_text(
                                f"✗ Refresh failed: {error_message}",
                                "orange",
                                bold=True,
                            )
                        )
                    else:
                        print(
                            color_text(
                                f"✓ Refreshed: {indexed_data.get('title', 'Untitled')}",
                                style["color"],
                                bold=True,
                            )
                        )
                
                elif subcmd == "delete":
                    if not subarg:
                        print(color_text("Usage: /memory delete <session_id>", "orange"))
                        continue
                    try:
                        deleted = delete_memory(subarg)
                        if deleted:
                            print(color_text(f"✓ Deleted memory for session {subarg}", style["color"], bold=True))
                        else:
                            print(color_text(f"Memory not found for session {subarg}", "orange"))
                    except Exception as e:
                        print(color_text(f"Error deleting memory: {e}", "orange", bold=True))
                
                else:
                    print(color_text(f"Unknown memory command: {subcmd}", "orange"))
            elif special == "multiline":
                # Enter paste mode: treat whole block as one message
                # Check if vim mode was requested
                use_vim = (msg == "vim")
                block_text = read_multiline_block(end_token="EOF", use_vim=use_vim)
                if not block_text:
                    if use_vim:
                        print(color_text("No content saved from editor.", "grey"))
                    else:
                        print(color_text("Paste cancelled or empty block.", "grey"))
                    continue

                # Provide feedback for large inputs and warn about very large inputs
                char_count = len(block_text)
                if char_count > 1000:
                    print(
                        color_text(
                            f"Received {char_count:,} characters. Processing...",
                            "grey",
                        )
                    )
                
                # Warn about very large inputs that might cause API issues
                # OpenAI has token limits, very large inputs may need chunking
                if char_count > 50000:
                    print(
                        color_text(
                            f"Warning: Very large input ({char_count:,} chars). "
                            "This may take a long time or hit API limits.",
                            "orange",
                        )
                    )
                    response = input("Continue? (y/N): ").strip().lower()
                    if response != 'y':
                        print(color_text("Cancelled.", "grey"))
                        continue

                thinking_label = f"{style['emoji']} Thinking for {style['label']}"
                stop_event = threading.Event()
                spinner_thread = threading.Thread(
                    target=spinner,
                    args=(stop_event, thinking_label, style["color"]),
                    daemon=True,
                )

                spinner_thread.start()
                try:
                    # Set streaming flag so signal handler knows we're streaming
                    _is_streaming = True
                    
                    # Spinner runs while we wait for API response
                    # Get the generator first (this starts the API call)
                    stream_gen = chat_turn(conv_id, block_text, current_project, stream=True)
                    
                    # Stop spinner and clear it when we get first chunk
                    first_chunk_received = False
                    reply = ""
                    try:
                        _interrupt_streaming = False  # Reset interrupt flag
                        import time
                        # More aggressive throttling: slower display for readability
                        min_delay = 0.03  # 30ms minimum delay per character
                        last_write_time = time.time()
                        
                        for chunk in stream_gen:
                            # Check if user pressed Ctrl+C
                            if _interrupt_streaming:
                                _interrupt_streaming = False
                                raise KeyboardInterrupt("Streaming interrupted by user")
                            
                            # Stop spinner on first chunk
                            if not first_chunk_received:
                                stop_event.set()
                                spinner_thread.join()
                                # Clear spinner line
                                sys.stdout.write("\r" + " " * 80 + "\r")
                                sys.stdout.flush()
                                # Start AI response line
                                print(f"\n{ai_label} ", end="", flush=True)
                                first_chunk_received = True
                            
                            # Write character by character with delay for natural typing effect
                            for char in chunk:
                                # Check again before each character (more responsive)
                                if _interrupt_streaming:
                                    _interrupt_streaming = False
                                    raise KeyboardInterrupt("Streaming interrupted by user")
                                
                                current_time = time.time()
                                elapsed = current_time - last_write_time
                                
                                # Wait if needed to maintain minimum delay
                                if elapsed < min_delay:
                                    time.sleep(min_delay - elapsed)
                                
                                sys.stdout.write(char)
                                sys.stdout.flush()
                                last_write_time = time.time()
                                reply += char
                        
                        print()  # Newline after streaming completes
                    except KeyboardInterrupt:
                        stop_event.set()
                        spinner_thread.join()
                        _is_streaming = False  # Reset streaming flag
                        print(color_text("\n\nStreaming stopped. You can continue with a new message.", "orange", bold=True))
                        # Save partial response if any was received
                        if reply:
                            try:
                                from brain_core.db import save_message
                                import datetime
                                meta = {
                                    "model": "streaming",
                                    "created_at": datetime.datetime.utcnow().isoformat() + "Z",
                                    "interrupted": True,
                                    "partial": True,
                                }
                                save_message(conv_id, "assistant", reply, meta=meta)
                                print(color_text(f"Partial response saved ({len(reply)} chars).", "grey"))
                            except Exception as e:
                                logger.warning(f"Failed to save partial response: {e}")
                                print(color_text(f"Partial response received ({len(reply)} chars) but not saved.", "grey"))
                        continue
                    finally:
                        _is_streaming = False  # Always reset streaming flag when done
                except KeyboardInterrupt:
                    stop_event.set()
                    spinner_thread.join()
                    print(color_text("\n\nAPI call interrupted. This may indicate:", "orange", bold=True))
                    print(color_text("  - Input is too large for API", "orange"))
                    print(color_text("  - Network timeout", "orange"))
                    print(color_text("  - API rate limit", "orange"))
                    print(color_text("\nTry breaking the input into smaller chunks.", "orange"))
                    continue
                except Exception as e:
                    stop_event.set()
                    spinner_thread.join()
                    print(color_text(f"\n\nError processing request: {e}", "orange", bold=True))
                    print(color_text("The input may be too large or there may be a network issue.", "orange"))
                    continue
                finally:
                    stop_event.set()
                    spinner_thread.join()
                    if reply:
                        print()  # Ensure newline after response
            elif special == "readfile":
                # Read file and process content
                filepath = msg.strip()
                file_content, error_msg = read_file_content(filepath)
                
                if error_msg:
                    print(color_text(error_msg, "orange", bold=True))
                    continue
                
                if not file_content:
                    print(color_text("File is empty.", "grey"))
                    continue
                
                # Provide feedback for large files
                char_count = len(file_content)
                print(
                    color_text(
                        f"Read {char_count:,} characters from {filepath}",
                        "grey",
                    )
                )
                
                # Warn about very large files
                if char_count > 50000:
                    print(
                        color_text(
                            f"Warning: Very large file ({char_count:,} chars). "
                            "This may take a long time or hit API limits.",
                            "orange",
                        )
                    )
                    response = input("Continue? (y/N): ").strip().lower()
                    if response != 'y':
                        print(color_text("Cancelled.", "grey"))
                        continue
                
                thinking_label = f"{style['emoji']} Thinking for {style['label']}"
                stop_event = threading.Event()
                spinner_thread = threading.Thread(
                    target=spinner,
                    args=(stop_event, thinking_label, style["color"]),
                    daemon=True,
                )

                spinner_thread.start()
                try:
                    # Set streaming flag so signal handler knows we're streaming
                    _is_streaming = True
                    _interrupt_streaming = False  # Reset interrupt flag
                    
                    # Spinner runs while we wait for API response
                    # Get the generator first (this starts the API call)
                    stream_gen = chat_turn(conv_id, file_content, current_project, stream=True)
                    
                    # Stop spinner and clear it when we get first chunk
                    first_chunk_received = False
                    reply = ""
                    try:
                        import time
                        # More aggressive throttling: slower display for readability
                        min_delay = 0.03  # 30ms minimum delay per character
                        last_write_time = time.time()
                        
                        for chunk in stream_gen:
                            # Check if user pressed Ctrl+C
                            if _interrupt_streaming:
                                _interrupt_streaming = False
                                raise KeyboardInterrupt("Streaming interrupted by user")
                            
                            # Stop spinner on first chunk
                            if not first_chunk_received:
                                stop_event.set()
                                spinner_thread.join()
                                # Clear spinner line
                                sys.stdout.write("\r" + " " * 80 + "\r")
                                sys.stdout.flush()
                                # Start AI response line
                                print(f"\n{ai_label} ", end="", flush=True)
                                first_chunk_received = True
                            
                            # Write character by character with delay for natural typing effect
                            for char in chunk:
                                # Check again before each character (more responsive)
                                if _interrupt_streaming:
                                    _interrupt_streaming = False
                                    raise KeyboardInterrupt("Streaming interrupted by user")
                                
                                current_time = time.time()
                                elapsed = current_time - last_write_time
                                
                                # Wait if needed to maintain minimum delay
                                if elapsed < min_delay:
                                    time.sleep(min_delay - elapsed)
                                
                                sys.stdout.write(char)
                                sys.stdout.flush()
                                last_write_time = time.time()
                                reply += char
                        
                        print()  # Newline after streaming completes
                    except KeyboardInterrupt:
                        stop_event.set()
                        spinner_thread.join()
                        _is_streaming = False  # Reset streaming flag
                        print(color_text("\n\nStreaming stopped. You can continue with a new message.", "orange", bold=True))
                        # Save partial response if any was received
                        if reply:
                            try:
                                from brain_core.db import save_message
                                import datetime
                                meta = {
                                    "model": "streaming",
                                    "created_at": datetime.datetime.utcnow().isoformat() + "Z",
                                    "interrupted": True,
                                    "partial": True,
                                }
                                save_message(conv_id, "assistant", reply, meta=meta)
                                print(color_text(f"Partial response saved ({len(reply)} chars).", "grey"))
                            except Exception as e:
                                logger.warning(f"Failed to save partial response: {e}")
                                print(color_text(f"Partial response received ({len(reply)} chars) but not saved.", "grey"))
                        continue
                    finally:
                        _is_streaming = False  # Always reset streaming flag when done
                except KeyboardInterrupt:
                    stop_event.set()
                    spinner_thread.join()
                    print(color_text("\n\nAPI call interrupted. This may indicate:", "orange", bold=True))
                    print(color_text("  - Input is too large for API", "orange"))
                    print(color_text("  - Network timeout", "orange"))
                    print(color_text("  - API rate limit", "orange"))
                    print(color_text("\nTry breaking the input into smaller chunks.", "orange"))
                    continue
                except Exception as e:
                    stop_event.set()
                    spinner_thread.join()
                    print(color_text(f"\n\nError processing request: {e}", "orange", bold=True))
                    print(color_text("The input may be too large or there may be a network issue.", "orange"))
                    continue
                finally:
                    stop_event.set()
                    spinner_thread.join()
                    if reply:
                        print()  # Ensure newline after response
            elif msg:
                print(color_text(msg, style["color"], bold=True))
            continue

        # normal chat turn with spinner (single-line or large input)
        # Provide feedback for large inputs
        char_count = len(user_text)
        if char_count > 1000:
            print(
                color_text(
                    f"Detected large input ({char_count:,} characters). Processing...",
                    "grey",
                )
            )

        thinking_label = f"{style['emoji']} Thinking for {style['label']}"
        stop_event = threading.Event()
        spinner_thread = threading.Thread(
            target=spinner,
            args=(stop_event, thinking_label, style["color"]),
            daemon=True,
        )

        spinner_thread.start()
        try:
            # Set streaming flag so signal handler knows we're streaming
            _is_streaming = True
            
            # Spinner runs while we wait for API response
            # Get the generator first (this starts the API call)
            stream_gen = chat_turn(conv_id, user_text, current_project, stream=True)
            
            # Set streaming flag so signal handler knows we're streaming
            _is_streaming = True
            _interrupt_streaming = False  # Reset interrupt flag
            
            # Stop spinner and clear it when we get first chunk
            first_chunk_received = False
            reply = ""
            try:
                import time
                # More aggressive throttling: slower display for readability
                min_delay = 0.03  # 30ms minimum delay per character
                last_write_time = time.time()
                
                for chunk in stream_gen:
                    # Check if user pressed Ctrl+C
                    if _interrupt_streaming:
                        _interrupt_streaming = False
                        raise KeyboardInterrupt("Streaming interrupted by user")
                    
                    # Stop spinner on first chunk
                    if not first_chunk_received:
                        stop_event.set()
                        spinner_thread.join()
                        # Clear spinner line
                        sys.stdout.write("\r" + " " * 80 + "\r")
                        sys.stdout.flush()
                        # Start AI response line
                        print(f"\n{ai_label} ", end="", flush=True)
                        first_chunk_received = True
                    
                    # Write character by character with delay for natural typing effect
                    for char in chunk:
                        # Check again before each character (more responsive)
                        if _interrupt_streaming:
                            _interrupt_streaming = False
                            raise KeyboardInterrupt("Streaming interrupted by user")
                        
                        current_time = time.time()
                        elapsed = current_time - last_write_time
                        
                        # Wait if needed to maintain minimum delay
                        if elapsed < min_delay:
                            time.sleep(min_delay - elapsed)
                        
                        sys.stdout.write(char)
                        sys.stdout.flush()
                        last_write_time = time.time()
                        reply += char
                
                print()  # Newline after streaming completes
            except KeyboardInterrupt:
                stop_event.set()
                spinner_thread.join()
                _is_streaming = False  # Reset streaming flag
                print(color_text("\n\nStreaming stopped. You can continue with a new message.", "orange", bold=True))
                # Save partial response if any was received
                if reply:
                    try:
                        from brain_core.db import save_message
                        import datetime
                        meta = {
                            "model": "streaming",
                            "created_at": datetime.datetime.utcnow().isoformat() + "Z",
                            "interrupted": True,
                            "partial": True,
                        }
                        save_message(conv_id, "assistant", reply, meta=meta)
                        print(color_text(f"Partial response saved ({len(reply)} chars).", "grey"))
                    except Exception as e:
                        logger.warning(f"Failed to save partial response: {e}")
                        print(color_text(f"Partial response received ({len(reply)} chars) but not saved.", "grey"))
                continue
            finally:
                _is_streaming = False  # Always reset streaming flag when done
        except Exception as e:
            stop_event.set()
            spinner_thread.join()
            print(color_text(f"\n\nError: {e}", "orange", bold=True))
            continue
        finally:
            stop_event.set()
            spinner_thread.join()
            if reply:
                print()  # Ensure newline after response


if __name__ == "__main__":
    main()
