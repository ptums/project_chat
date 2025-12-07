"""
Python API for MCP server.

Provides direct Python interface to MCP server functionality
without requiring stdio communication.
"""
import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..models.repository import Repository
from ..models.index import NoteIndex
from ..services.index_builder import IndexBuilder
from ..services.project_filter import ProjectDirectoryMapper
from ..services.note_saver import ConversationNote, NoteSaver
from .resources import ResourcesHandler
from .tools import ToolsHandler

logger = logging.getLogger(__name__)


class MCPApi:
    """Python API for accessing MCP server functionality."""
    
    def __init__(self, gitlab_url: Optional[str] = None, repo_path: Optional[str] = None, branch: Optional[str] = None):
        """
        Initialize MCP API.
        
        Args:
            gitlab_url: GitLab repository URL (defaults to env var or default)
            repo_path: Local repository path (defaults to env var or default)
            branch: Git branch (defaults to env var or 'main')
        """
        # Get configuration from parameters or environment
        self.gitlab_url = gitlab_url or os.environ.get("GITLAB_URL", "http://192.168.119.200:8201/tumultymedia/meditations")
        repo_path_str = repo_path or os.environ.get("REPO_PATH", "/tmp/meditation-mcp-repo")
        self.repo_path = Path(repo_path_str)
        self.branch = branch or os.environ.get("BRANCH", "main")
        
        # Create repository model
        self.repository = Repository(
            url=self.gitlab_url,
            local_path=self.repo_path,
            branch=self.branch
        )
        
        # Create note index
        self.index = NoteIndex()
        
        # Create project directory mapper
        self.project_mapper = ProjectDirectoryMapper()
        
        # Create handlers
        self.resources_handler = ResourcesHandler(self.index)
        self.tools_handler = ToolsHandler(self.index, self.repository)
        
        # Create note saver
        self.note_saver = NoteSaver(self.repository, self.index)
        
        # Build initial index if repository exists
        if self.repository.local_path.exists() and (self.repository.local_path / ".git").exists():
            logger.info("Building initial index from existing repository...")
            builder = IndexBuilder(self.repository, self.index)
            try:
                note_count = builder.rebuild_index()
                logger.info(f"Indexed {note_count} notes")
            except Exception as e:
                logger.warning(f"Failed to build initial index: {e}")
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """
        List all available resources.
        
        Returns:
            List of resource dictionaries
        """
        result = self.resources_handler.list_resources({})
        return result.get("resources", [])
    
    def read_resource(self, identifier: str, project: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Read a resource by URI, slug, or title.
        
        Args:
            identifier: Resource URI (meditation://note/...), slug, or title
            project: Optional project name to filter search
            
        Returns:
            Dict with 'content' and 'note' info, or None if not found
        """
        # Check if it's a URI
        if identifier.startswith("meditation://"):
            try:
                result = self.resources_handler.read_resource({"uri": identifier})
                contents = result.get("contents", [])
                if contents:
                    note = self.index.get_by_uri(identifier)
                    return {
                        "content": contents[0].get("text"),
                        "note": note.to_dict() if note else None
                    }
            except Exception as e:
                logger.warning(f"Failed to read resource {identifier}: {e}")
            return None
        
        # Search by slug or title
        identifier_lower = identifier.lower()
        matching_notes = []
        
        # Get notes to search (project-filtered or all)
        if project:
            directory = self.project_mapper.get_directory(project)
            notes_to_search = self.index.get_by_project(directory)
        else:
            notes_to_search = self.index.all_notes()
        
        for note in notes_to_search:
            # Check slug
            if note.slug.lower() == identifier_lower:
                matching_notes = [note]
                break
            # Check title (partial match)
            if identifier_lower in note.title.lower():
                matching_notes.append(note)
        
        if not matching_notes:
            return None
        
        # If multiple matches, prefer exact slug match, then exact title match
        if len(matching_notes) > 1:
            exact_slug = next((n for n in matching_notes if n.slug.lower() == identifier_lower), None)
            if exact_slug:
                matching_notes = [exact_slug]
            else:
                exact_title = next((n for n in matching_notes if n.title.lower() == identifier_lower), None)
                if exact_title:
                    matching_notes = [exact_title]
        
        # Use first match
        note = matching_notes[0]
        return {
            "content": note.content,
            "note": note.to_dict()
        }
    
    def search_notes(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search notes.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            Search results
        """
        return self.tools_handler.search_notes({"query": query, "limit": limit})
    
    def sync_repository(self) -> Dict[str, Any]:
        """
        Sync repository from GitLab.
        
        Returns:
            Sync result
        """
        return self.tools_handler.sync_repository({})
    
    def list_resources_by_project(self, project: str) -> List[Dict[str, Any]]:
        """
        List all resources filtered by project directory.
        
        Args:
            project: Project name (DAAS, THN, FF, General, 700B)
            
        Returns:
            List of resource dictionaries with uri, name, description, mimeType
        """
        # Get directory name for project
        directory = self.project_mapper.get_directory(project)
        
        # Get notes for this project directory
        notes = self.index.get_by_project(directory)
        
        # Convert to resource format
        resources = []
        for note in notes:
            resources.append({
                "uri": note.uri,
                "name": note.title,
                "description": note.title,
                "mimeType": "text/markdown"
            })
        
        return resources
    
    def get_project_notes(self, project: str, user_message: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get relevant notes for a project based on user message.
        
        Args:
            project: Project name
            user_message: User message for keyword matching
            limit: Maximum number of notes to return
            
        Returns:
            List of note dictionaries with uri, title, content snippet
        """
        # Get directory name for project
        directory = self.project_mapper.get_directory(project)
        
        # Search notes in this project directory
        notes = self.index.search_by_project(directory, user_message, limit=limit)
        
        # Convert to dict format
        result = []
        for note in notes:
            # Include snippet of content (first 200 chars)
            content_snippet = note.content[:200] + "..." if len(note.content) > 200 else note.content
            result.append({
                "uri": note.uri,
                "title": note.title,
                "content_snippet": content_snippet,
                "file_path": note.file_path
            })
        
        return result
    
    def save_conversation(
        self, 
        project: str, 
        messages: List[Dict[str, Any]], 
        title: Optional[str] = None,
        gitlab_username: Optional[str] = None,
        gitlab_password: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Save a conversation as a note in the project directory.
        
        Args:
            project: Project name
            messages: List of message dicts with role, content, timestamp
            title: Optional title for the note
            gitlab_username: Optional GitLab username for authentication
            gitlab_password: Optional GitLab password or token for authentication
            
        Returns:
            Dict with success status, file_path, and message
        """
        # Generate title if not provided
        if not title:
            # Try to extract from first user message
            first_user_msg = next((msg for msg in messages if msg.get("role") == "user"), None)
            if first_user_msg:
                content = first_user_msg.get("content", "")
                # Use first 50 chars as title
                title = content[:50].strip()
                if len(content) > 50:
                    title += "..."
            else:
                # Fallback to timestamp-based title
                title = f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Get created_at from first message or use now
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
        
        # Save using NoteSaver
        success, file_path, error = self.note_saver.save_conversation(
            conversation_note,
            gitlab_username=gitlab_username,
            gitlab_password=gitlab_password
        )
        
        if success:
            return {
                "success": True,
                "file_path": file_path,
                "message": f"Note saved: {file_path}" + (f" (Warning: {error})" if error else "")
            }
        else:
            return {
                "success": False,
                "file_path": None,
                "message": error or "Failed to save note"
            }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get server status.
        
        Returns:
            Status information
        """
        return {
            "initialized": True,
            "repository_url": self.gitlab_url,
            "repository_path": str(self.repo_path),
            "branch": self.branch,
            "note_count": self.index.count(),
            "last_sync": self.repository.last_sync.isoformat() if self.repository.last_sync else None,
            "sync_error": self.repository.sync_error
        }


# Global API instance (lazy initialization)
_api_instance: Optional[MCPApi] = None


def get_mcp_api() -> MCPApi:
    """
    Get global MCP API instance.
    
    Returns:
        MCPApi instance
    """
    global _api_instance
    if _api_instance is None:
        _api_instance = MCPApi()
    return _api_instance