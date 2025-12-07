"""
Note entity for meditation notes.

Represents a single meditation note parsed from Obsidian markdown.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class Note:
    """A meditation note parsed from Obsidian markdown."""
    
    slug: str
    title: str
    content: str
    frontmatter: Dict[str, Any]
    file_path: str
    last_modified: Optional[datetime] = None
    
    @property
    def uri(self) -> str:
        """Generate MCP resource URI for this note."""
        return f"meditation://note/{self.slug}"
    
    @property
    def project_directory(self) -> str:
        """
        Extract project directory from file_path.
        
        Returns:
            Project directory name (e.g., "daas" from "daas/morning-meditation.md")
            Returns empty string if file_path doesn't contain a directory
        """
        if not self.file_path:
            return ""
        
        # Split path and get first component (directory)
        parts = self.file_path.split("/")
        if len(parts) > 1:
            return parts[0]
        
        # If no directory separator, return empty string
        return ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert note to dictionary for JSON serialization."""
        return {
            "slug": self.slug,
            "title": self.title,
            "content": self.content,
            "frontmatter": self.frontmatter,
            "file_path": self.file_path,
            "uri": self.uri,
            "last_modified": self.last_modified.isoformat() if self.last_modified else None
        }