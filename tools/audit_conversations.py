#!/usr/bin/env python3
"""
Conversation Audit Tool

A CLI tool for managing and cleaning up conversation history.
Allows users to list conversations, review message history, edit titles/projects, and delete conversations.
"""

import uuid
import sys
from typing import Optional

import psycopg2
from psycopg2 import OperationalError

from brain_core.db import get_conn
from brain_core.config import DB_CONFIG
from brain_core.chat import normalize_project_tag

# Valid project names
VALID_PROJECTS = ["THN", "DAAS", "FF", "700B", "general"]


def validate_uuid(uuid_str: str) -> uuid.UUID:
    """
    Validate and parse UUID string.
    
    Args:
        uuid_str: String to validate as UUID
        
    Returns:
        Parsed UUID object
        
    Raises:
        ValueError: If string is not a valid UUID format
    """
    try:
        return uuid.UUID(uuid_str)
    except (ValueError, AttributeError) as e:
        raise ValueError(f"Invalid UUID format: {uuid_str}") from e


def validate_project(project: str) -> bool:
    """
    Validate project name.
    
    Args:
        project: Project name to validate
        
    Returns:
        True if valid, False otherwise
    """
    return project.upper() in [p.upper() for p in VALID_PROJECTS]


def display_main_menu() -> str:
    """
    Display main menu and get user selection.
    
    Returns:
        User's menu selection (1-4)
    """
    print("\n" + "=" * 50)
    print("Conversation Audit Tool")
    print("=" * 50)
    print("1. List conversations by project")
    print("2. View conversation by ID")
    print("3. Search conversation by title")
    print("4. Exit")
    print()
    
    while True:
        try:
            choice = input("Select an option (1-4): ").strip()
            if choice in ["1", "2", "3", "4"]:
                return choice
            else:
                print("Invalid option. Please enter 1-4.")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            sys.exit(0)


def handle_db_error(e: Exception, operation: str) -> None:
    """
    Handle database errors with user-friendly messages.
    
    Args:
        e: Exception that occurred
        operation: Description of the operation that failed
    """
    if isinstance(e, OperationalError):
        print(f"Database connection error during {operation}: {e}")
    elif isinstance(e, psycopg2.Error):
        print(f"Database error during {operation}: {e}")
    else:
        print(f"Unexpected error during {operation}: {e}")


def edit_conversation_title(conv_id: uuid.UUID, new_title: str) -> bool:
    """
    Update conversation title.
    
    Args:
        conv_id: Conversation ID (UUID)
        new_title: New title for the conversation
        
    Returns:
        True if successful, False otherwise
    """
    new_title = new_title.strip()
    if not new_title:
        print("Title cannot be empty")
        return False
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE conversations SET title = %s WHERE id = %s",
                    (new_title, str(conv_id)),
                )
                conn.commit()
        
        print("Title updated successfully.")
        return True
    except Exception as e:
        handle_db_error(e, "updating title")
        return False


def edit_conversation_project(conv_id: uuid.UUID, new_project: str) -> bool:
    """
    Update conversation project tag (both conversations and conversation_index tables).
    
    Args:
        conv_id: Conversation ID (UUID)
        new_project: New project name
        
    Returns:
        True if successful, False otherwise
    """
    if not validate_project(new_project):
        print(f"Invalid project. Must be one of: {', '.join(VALID_PROJECTS)}")
        return False
    
    # Normalize project using the same function used throughout the codebase
    # This ensures "general" stays lowercase, while others are uppercase
    new_project = normalize_project_tag(new_project)
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                # Begin transaction
                conn.autocommit = False
                
                try:
                    # Update conversations table
                    cur.execute(
                        "UPDATE conversations SET project = %s WHERE id = %s",
                        (new_project, str(conv_id)),
                    )
                    
                    # Update conversation_index table if entry exists
                    cur.execute(
                        "UPDATE conversation_index SET project = %s WHERE session_id = %s",
                        (new_project, str(conv_id)),
                    )
                    
                    conn.commit()
                    print("Project updated successfully.")
                    return True
                except Exception as e:
                    conn.rollback()
                    raise e
                finally:
                    conn.autocommit = True
                    
    except Exception as e:
        handle_db_error(e, "updating project")
        return False


def delete_conversation(conv_id: uuid.UUID) -> bool:
    """
    Delete conversation and all related data (CASCADE handles messages and conversation_index).
    
    Args:
        conv_id: Conversation ID (UUID)
        
    Returns:
        True if successful, False otherwise
    """
    # Confirmation prompt
    confirm = input("Are you sure you want to delete this conversation? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Deletion cancelled.")
        return False
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                # Delete from conversations (CASCADE handles messages and conversation_index)
                cur.execute(
                    "DELETE FROM conversations WHERE id = %s",
                    (str(conv_id),),
                )
                conn.commit()
        
        print("Conversation deleted successfully.")
        return True
    except Exception as e:
        handle_db_error(e, "deleting conversation")
        return False


def message_review_mode(conv_id: str) -> None:
    """
    Handle message review mode with commands for editing/deleting.
    
    Args:
        conv_id: Conversation ID (UUID string)
    """
    try:
        validated_id = validate_uuid(conv_id)
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    while True:
        try:
            user_input = input("Enter command: ").strip()
            if not user_input:
                continue
            
            command, arg = parse_message_command(user_input)
            
            if command == "/back":
                return
            elif command == "/edit-title":
                try:
                    new_title = input("Enter new title: ").strip()
                    if edit_conversation_title(validated_id, new_title):
                        # Refresh message view
                        view_messages(conv_id)
                except (EOFError, KeyboardInterrupt):
                    print("\nCancelled.")
            elif command == "/edit-project":
                try:
                    new_project = input("Enter new project (THN/DAAS/FF/700B/general): ").strip()
                    if edit_conversation_project(validated_id, new_project):
                        # Refresh message view
                        view_messages(conv_id)
                except (EOFError, KeyboardInterrupt):
                    print("\nCancelled.")
            elif command == "/delete":
                try:
                    if delete_conversation(validated_id):
                        print("Returning to main menu...")
                        return
                except (EOFError, KeyboardInterrupt):
                    print("\nCancelled.")
            elif command == "/messages" and arg:
                # Switch to different conversation
                view_messages(arg)
                validated_id = validate_uuid(arg)
                conv_id = arg
            else:
                print(f"Unknown command: {command}")
                print("Commands: /edit-title, /edit-project, /delete, /back")
        except (EOFError, KeyboardInterrupt):
            print("\nReturning to main menu...")
            return
        except ValueError as e:
            print(f"Error: {e}")


def get_conversation_by_id(conv_id: str) -> None:
    """
    Display conversation details for a specific conversation ID.
    
    Args:
        conv_id: Conversation ID (UUID string)
    """
    try:
        validated_id = validate_uuid(conv_id)
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        c.id,
                        c.title,
                        c.project,
                        COUNT(m.id) as message_count,
                        c.created_at
                    FROM conversations c
                    LEFT JOIN messages m ON m.conversation_id = c.id
                    WHERE c.id = %s
                    GROUP BY c.id, c.title, c.project, c.created_at
                    """,
                    (str(validated_id),),
                )
                row = cur.fetchone()
        
        if not row:
            print(f"\nConversation not found: {conv_id}")
            return
        
        conv_id_db, title, project, msg_count, created_at = row
        print("\nConversation Details")
        print("=" * 60)
        print(f"ID: {conv_id_db}")
        print(f"Title: {title}")
        print(f"Project: {project}")
        print(f"Messages: {msg_count}")
        print(f"Created: {created_at}")
        print()
        print("Enter /messages <id> to review, or press Enter to return to main menu")
        try:
            user_input = input().strip()
            if not user_input:
                return  # User pressed Enter, return to main menu
            
            # Accept both /message and /messages (singular or plural)
            if user_input.startswith("/message"):
                command, conv_id_arg = parse_message_command(user_input)
                if conv_id_arg:
                    view_messages(conv_id_arg)
                    message_review_mode(conv_id_arg)
                    # After returning from message review, return to main menu
                    print("\nReturning to main menu...")
                    return
                else:
                    print("Error: Missing conversation ID. Usage: /messages <id>")
            else:
                # Not a command, just return to main menu
                return
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
        
    except Exception as e:
        handle_db_error(e, "getting conversation by ID")


def search_conversations_by_title(title: str) -> None:
    """
    Search conversations by title (exact or partial match).
    
    Args:
        title: Title or partial title to search for
    """
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        c.id,
                        c.title,
                        c.project,
                        COUNT(m.id) as message_count,
                        c.created_at
                    FROM conversations c
                    LEFT JOIN messages m ON m.conversation_id = c.id
                    WHERE c.title ILIKE %s
                    GROUP BY c.id, c.title, c.project, c.created_at
                    ORDER BY c.created_at DESC
                    """,
                    (f"%{title}%",),
                )
                rows = cur.fetchall()
        
        if not rows:
            print(f"\nNo conversations found matching '{title}'")
            return
        
        print(f"\nSearch Results for: \"{title}\"")
        print("=" * 60)
        for row in rows:
            conv_id, conv_title, project, msg_count, created_at = row
            print(f"ID: {conv_id}")
            print(f"Title: {conv_title}")
            print(f"Project: {project}")
            print(f"Messages: {msg_count}")
            print()
        
        print("Enter /messages <id> to review, or press Enter to return to main menu")
        try:
            user_input = input().strip()
            if not user_input:
                return  # User pressed Enter, return to main menu
            
            # Accept both /message and /messages (singular or plural)
            if user_input.startswith("/message"):
                command, conv_id = parse_message_command(user_input)
                if conv_id:
                    view_messages(conv_id)
                    message_review_mode(conv_id)
                    # After returning from message review, return to main menu
                    print("\nReturning to main menu...")
                    return
                else:
                    print("Error: Missing conversation ID. Usage: /messages <id>")
            else:
                # Not a command, just return to main menu
                return
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
        
    except Exception as e:
        handle_db_error(e, "searching conversations by title")


def view_messages(conv_id: str) -> None:
    """
    Display message history for a conversation.
    
    Args:
        conv_id: Conversation ID (UUID string)
    """
    try:
        validated_id = validate_uuid(conv_id)
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                # Get conversation info
                cur.execute(
                    "SELECT title, project FROM conversations WHERE id = %s",
                    (str(validated_id),),
                )
                conv_info = cur.fetchone()
                
                if not conv_info:
                    print(f"\nConversation not found: {conv_id}")
                    return
                
                title, project = conv_info
                
                # Get messages
                cur.execute(
                    """
                    SELECT role, content, created_at
                    FROM messages
                    WHERE conversation_id = %s
                    ORDER BY created_at ASC
                    LIMIT 50
                    """,
                    (str(validated_id),),
                )
                messages = cur.fetchall()
        
        if not messages:
            print(f"\nNo messages found for conversation: {title}")
            return
        
        print(f"\nMessage History for: {title} ({project})")
        print("=" * 60)
        for idx, (role, content, created_at) in enumerate(messages, 1):
            role_label = "[USER]" if role == "user" else "[ASSISTANT]"
            print(f"\n[{idx}] {role_label}")
            print(content)
            if idx < len(messages):
                print()
        
        print("\n" + "=" * 60)
        print("Commands: /edit-title, /edit-project, /delete, /back")
        # Note: prompt is shown in message_review_mode loop
        
    except Exception as e:
        handle_db_error(e, "viewing messages")


def parse_message_command(user_input: str) -> tuple[str, Optional[str]]:
    """
    Parse command from user input in message review mode.
    
    Args:
        user_input: User input string
        
    Returns:
        Tuple of (command, argument) where argument may be None
    """
    parts = user_input.strip().split(maxsplit=1)
    command = parts[0].lower() if parts else ""
    arg = parts[1] if len(parts) > 1 else None
    
    # Normalize /message and /messages to /messages
    if command in ("/message", "/messages"):
        command = "/messages"
    
    return command, arg


def list_conversations_by_project(project: str) -> None:
    """
    List all conversations for a specific project.
    
    Args:
        project: Project name to filter by
    """
    if not validate_project(project):
        print(f"Invalid project. Must be one of: {', '.join(VALID_PROJECTS)}")
        return
    
    # Normalize project using the same function used throughout the codebase
    # This ensures "general" stays lowercase, while others are uppercase
    normalized_project = normalize_project_tag(project)
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        c.id,
                        c.title,
                        c.project,
                        COUNT(m.id) as message_count,
                        c.created_at
                    FROM conversations c
                    LEFT JOIN messages m ON m.conversation_id = c.id
                    WHERE c.project = %s
                    GROUP BY c.id, c.title, c.project, c.created_at
                    ORDER BY c.created_at DESC
                    """,
                    (normalized_project,),
                )
                rows = cur.fetchall()
        
        if not rows:
            print(f"\nNo conversations found for project {normalized_project}")
            return
        
        print(f"\nConversations for project: {normalized_project}")
        print("=" * 60)
        for row in rows:
            conv_id, title, proj, msg_count, created_at = row
            print(f"ID: {conv_id}")
            print(f"Title: {title}")
            print(f"Project: {proj}")
            print(f"Messages: {msg_count}")
            print()
        
        print("Enter /messages <id> to review, or press Enter to return to main menu")
        try:
            user_input = input().strip()
            if not user_input:
                return  # User pressed Enter, return to main menu
            
            # Accept both /message and /messages (singular or plural)
            if user_input.startswith("/message"):
                command, conv_id = parse_message_command(user_input)
                if conv_id:
                    view_messages(conv_id)
                    message_review_mode(conv_id)
                    # After returning from message review, return to main menu
                    print("\nReturning to main menu...")
                    return
                else:
                    print("Error: Missing conversation ID. Usage: /messages <id>")
            else:
                # Not a command, just return to main menu
                return
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
        
    except Exception as e:
        handle_db_error(e, "listing conversations by project")


def main():
    """Main entry point for the audit tool."""
    try:
        while True:
            choice = display_main_menu()
            
            if choice == "1":
                try:
                    project = input("\nEnter project name (THN/DAAS/FF/700B/general): ").strip()
                    list_conversations_by_project(project)
                    input()  # Wait for Enter to continue
                except (EOFError, KeyboardInterrupt):
                    print("\nCancelled.")
            elif choice == "2":
                try:
                    conv_id = input("\nEnter conversation ID: ").strip()
                    get_conversation_by_id(conv_id)
                    input()  # Wait for Enter to continue
                except (EOFError, KeyboardInterrupt):
                    print("\nCancelled.")
            elif choice == "3":
                try:
                    title = input("\nEnter title (or partial title): ").strip()
                    search_conversations_by_title(title)
                    input()  # Wait for Enter to continue
                except (EOFError, KeyboardInterrupt):
                    print("\nCancelled.")
            elif choice == "4":
                print("Bye.")
                break
                
    except KeyboardInterrupt:
        print("\nExiting.")
        sys.exit(0)
    except Exception as e:
        handle_db_error(e, "main operation")
        sys.exit(1)


if __name__ == "__main__":
    main()

