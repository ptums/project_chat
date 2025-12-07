"""
MCP tool handlers.

Handles tool invocation requests.
"""
import logging
from typing import Dict, Any

from ..models.index import NoteIndex
from ..services.index_builder import IndexBuilder
from ..models.repository import Repository

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