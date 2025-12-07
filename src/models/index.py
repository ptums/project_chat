"""
NoteIndex entity for fast O(1) note lookups.

Maintains in-memory index of notes by slug and URI.
"""
from typing import Dict, Optional
from .note import Note
from ..services.project_filter import ProjectDirectoryMapper


class NoteIndex:
    """In-memory index for fast note lookups."""
    
    def __init__(self):
        """Initialize empty index."""
        self._by_slug: Dict[str, Note] = {}
        self._by_uri: Dict[str, Note] = {}
        self._by_file_path: Dict[str, Note] = {}
    
    def add(self, note: Note):
        """Add note to index."""
        self._by_slug[note.slug] = note
        self._by_uri[note.uri] = note
        self._by_file_path[note.file_path] = note
    
    def get_by_slug(self, slug: str) -> Optional[Note]:
        """Get note by slug."""
        return self._by_slug.get(slug)
    
    def get_by_uri(self, uri: str) -> Optional[Note]:
        """Get note by URI."""
        return self._by_uri.get(uri)
    
    def get_by_file_path(self, file_path: str) -> Optional[Note]:
        """Get note by file path."""
        return self._by_file_path.get(file_path)
    
    def remove(self, note: Note):
        """Remove note from index."""
        self._by_slug.pop(note.slug, None)
        self._by_uri.pop(note.uri, None)
        self._by_file_path.pop(note.file_path, None)
    
    def clear(self):
        """Clear all notes from index."""
        self._by_slug.clear()
        self._by_uri.clear()
        self._by_file_path.clear()
    
    def all_notes(self) -> list[Note]:
        """Get all notes in index."""
        return list(self._by_slug.values())
    
    def count(self) -> int:
        """Get count of notes in index."""
        return len(self._by_slug)
    
    def search(self, query: str, limit: int = 10) -> list[Note]:
        """
        Simple text search through notes.
        
        Args:
            query: Search query (case-insensitive)
            limit: Maximum number of results
            
        Returns:
            List of matching notes
        """
        query_lower = query.lower()
        matches = []
        
        for note in self._by_slug.values():
            # Search in title and content
            if (query_lower in note.title.lower() or 
                query_lower in note.content.lower()):
                matches.append(note)
                if len(matches) >= limit:
                    break
        
        return matches
    
    def get_by_project(self, project: str) -> list[Note]:
        """
        Filter notes by project using ProjectDirectoryMapper.
        
        Args:
            project: Project name (e.g., "DAAS", "THN") or directory name (e.g., "daas", "thn")
            
        Returns:
            List of notes in the specified project directory
        """
        if not project:
            return []
        
        # Use ProjectDirectoryMapper to get directory name
        mapper = ProjectDirectoryMapper()
        project_directory = mapper.get_directory(project)
        
        if not project_directory:
            return []
        
        matches = []
        for note in self._by_slug.values():
            # Check if note's file_path starts with project directory
            if note.file_path.startswith(f"{project_directory}/"):
                matches.append(note)
        
        return matches
    
    def search_by_project(self, project: str, query: str, limit: int = 10) -> list[Note]:
        """
        Search notes within a specific project using ProjectDirectoryMapper.
        
        Args:
            project: Project name (e.g., "DAAS", "THN") or directory name (e.g., "daas", "thn")
            query: Search query (case-insensitive)
            limit: Maximum number of results
            
        Returns:
            List of matching notes from the specified project directory
        """
        if not project:
            return []
        
        # Use ProjectDirectoryMapper to get directory name
        mapper = ProjectDirectoryMapper()
        project_directory = mapper.get_directory(project)
        
        if not project_directory:
            return []
        
        query_lower = query.lower()
        matches = []
        
        for note in self._by_slug.values():
            # Check project directory first
            if not note.file_path.startswith(f"{project_directory}/"):
                continue
            
            # Then search in title and content
            if (query_lower in note.title.lower() or 
                query_lower in note.content.lower()):
                matches.append(note)
                if len(matches) >= limit:
                    break
        
        return matches