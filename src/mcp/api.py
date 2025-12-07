"""
Python API for MCP server.

Provides direct Python interface to MCP server functionality
without requiring stdio communication.
"""
import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from ..models.repository import Repository
from ..models.index import NoteIndex
from ..services.index_builder import IndexBuilder
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
        
        # Create handlers
        self.resources_handler = ResourcesHandler(self.index)
        self.tools_handler = ToolsHandler(self.index, self.repository)
        
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
    
    def read_resource(self, uri: str) -> Optional[str]:
        """
        Read a resource by URI.
        
        Args:
            uri: Resource URI
            
        Returns:
            Resource content or None if not found
        """
        try:
            result = self.resources_handler.read_resource({"uri": uri})
            contents = result.get("contents", [])
            if contents:
                return contents[0].get("text")
        except Exception as e:
            logger.warning(f"Failed to read resource {uri}: {e}")
        return None
    
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