"""
MCP tool handlers.

Handles tool invocation requests.
"""
import logging
from typing import Dict, Any

from ..models.index import NoteIndex
from ..services.index_builder import IndexBuilder
from ..models.repository import Repository
from ..services.note_saver import ConversationNote, NoteSaver

logger = logging.getLogger(__name__)


class ToolsHandler:
    """Handler for MCP tool operations."""
    
    def __init__(self, index: NoteIndex, repository: Repository):
        """
        Initialize tools handler.
        
        Args:
            index: NoteIndex instance
            repository: Repository instance
        """
        self.index = index
        self.repository = repository
        self.note_saver = NoteSaver(repository, index)
    
    def search_notes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle search_notes tool invocation.
        
        Args:
            params: Tool parameters with 'query' and optional 'limit'
            
        Returns:
            Search results response
        """
        query = params.get("query", "")
        limit = params.get("limit", 10)
        
        if not query:
            return {
                "content": [{
                    "type": "text",
                    "text": "No search query provided"
                }]
            }
        
        # Search notes
        matches = self.index.search(query, limit=limit)
        
        if not matches:
            return {
                "content": [{
                    "type": "text",
                    "text": f"No notes found matching '{query}'"
                }]
            }
        
        # Format results
        results_text = f"Found {len(matches)} note(s) matching '{query}':\n\n"
        for note in matches:
            results_text += f"## {note.title}\n"
            results_text += f"URI: {note.uri}\n"
            # Include snippet of content
            content_snippet = note.content[:200] + "..." if len(note.content) > 200 else note.content
            results_text += f"\n{content_snippet}\n\n"
        
        logger.debug(f"Searched for '{query}', found {len(matches)} results")
        return {
            "content": [{
                "type": "text",
                "text": results_text
            }]
        }
    
    def sync_repository(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle sync_repository tool invocation.
        
        Args:
            params: Tool parameters (unused)
            
        Returns:
            Sync result response
        """
        from ..services.index_builder import IndexBuilder
        
        logger.info("Syncing repository...")
        
        # Create index builder and sync
        builder = IndexBuilder(self.repository, self.index)
        success, note_count, error = builder.sync_and_rebuild()
        
        if success:
            message = f"Repository synced successfully. Indexed {note_count} notes."
            logger.info(message)
            return {
                "content": [{
                    "type": "text",
                    "text": message
                }]
            }
        else:
            error_message = f"Sync failed: {error}"
            logger.error(error_message)
            return {
                "content": [{
                    "type": "text",
                    "text": error_message
                }],
                "isError": True
            }
    
    def save_conversation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle save_conversation tool invocation.
        
        Args:
            params: Tool parameters with 'project', 'messages', optional 'title'
            
        Returns:
            Save result response
        """
        project = params.get("project")
        messages = params.get("messages", [])
        title = params.get("title")
        
        if not project:
            return {
                "content": [{
                    "type": "text",
                    "text": "Missing 'project' parameter"
                }],
                "isError": True
            }
        
        if not messages:
            return {
                "content": [{
                    "type": "text",
                    "text": "No messages to save"
                }],
                "isError": True
            }
        
        # Generate title if not provided
        if not title:
            first_user_msg = next((msg for msg in messages if msg.get("role") == "user"), None)
            if first_user_msg:
                content = first_user_msg.get("content", "")
                title = content[:50].strip()
                if len(content) > 50:
                    title += "..."
            else:
                from datetime import datetime
                title = f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Get created_at from first message
        from datetime import datetime
        created_at = None
        if messages:
            first_msg = messages[0]
            timestamp = first_msg.get("timestamp")
            if timestamp:
                try:
                    if isinstance(timestamp, str):
                        created_at = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    else:
                        created_at = timestamp
                except Exception:
                    pass
        
        if not created_at:
            created_at = datetime.now()
        
        # Create ConversationNote
        conversation_note = ConversationNote(
            title=title,
            project=project,
            messages=messages,
            created_at=created_at
        )
        
        # Get optional credentials
        gitlab_username = params.get("gitlab_username")
        gitlab_password = params.get("gitlab_password")
        
        # Save
        success, file_path, error = self.note_saver.save_conversation(
            conversation_note,
            gitlab_username=gitlab_username,
            gitlab_password=gitlab_password
        )
        
        if success:
            message = f"Conversation saved as note: {file_path}"
            if error:
                message += f" (Warning: {error})"
            logger.info(message)
            return {
                "content": [{
                    "type": "text",
                    "text": message
                }]
            }
        else:
            error_message = f"Failed to save conversation: {error}"
            logger.error(error_message)
            return {
                "content": [{
                    "type": "text",
                    "text": error_message
                }],
                "isError": True
            }