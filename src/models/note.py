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