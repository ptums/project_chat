"""
MCP resource handlers.

Handles resources/list and resources/read requests.
"""
import logging
from typing import Dict, Any, List

from ..models.index import NoteIndex

logger = logging.getLogger(__name__)


class ResourcesHandler:
    """Handler for MCP resource operations."""
    
    def __init__(self, index: NoteIndex):
        """
        Initialize resources handler.
        
        Args:
            index: NoteIndex instance
        """
        self.index = index
    
    def list_resources(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle resources/list request.
        
        Args:
            params: Request parameters (optional 'project' filter)
            
        Returns:
            Resources list response
        """
        resources = []
        
        # Check if project filter is provided
        project = params.get("project")
        
        if project:
            # Filter by project directory
            from ..services.project_filter import ProjectDirectoryMapper
            mapper = ProjectDirectoryMapper()
            directory = mapper.get_directory(project)
            notes = self.index.get_by_project(directory)
        else:
            # Return all notes
            notes = self.index.all_notes()
        
        for note in notes:
            resources.append({
                "uri": note.uri,
                "name": note.title,
                "description": note.title,
                "mimeType": "text/markdown"
            })
        
        logger.debug(f"Listed {len(resources)} resources" + (f" for project {project}" if project else ""))
        return {
            "resources": resources
        }
    
    def read_resource(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle resources/read request.
        
        Args:
            params: Request parameters with 'uri' field
            
        Returns:
            Resource content response
        """
        uri = params.get("uri")
        if not uri:
            raise ValueError("Missing 'uri' parameter")
        
        note = self.index.get_by_uri(uri)
        if not note:
            raise ValueError(f"Resource not found: {uri}")
        
        logger.debug(f"Read resource: {uri}")
        return {
            "contents": [{
                "uri": uri,
                "mimeType": "text/markdown",
                "text": note.content
            }]
        }