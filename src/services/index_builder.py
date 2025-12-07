"""
Index building service.

Builds and maintains the note index from repository files.
"""
import logging
from pathlib import Path
from typing import Optional

from ..models.repository import Repository
from ..models.index import NoteIndex
from ..services.note_parser import NoteParser

logger = logging.getLogger(__name__)


class IndexBuilder:
    """Service for building note index."""
    
    def __init__(self, repository: Repository, index: NoteIndex):
        """
        Initialize index builder.
        
        Args:
            repository: Repository configuration
            index: NoteIndex instance to populate
        """
        self.repository = repository
        self.index = index
    
    def rebuild_index(self) -> int:
        """
        Rebuild the note index from repository files.
        
        Returns:
            Number of notes indexed
        """
        logger.info("Rebuilding note index...")
        
        # Clear existing index
        self.index.clear()
        
        # Find and parse all notes
        notes = NoteParser.find_notes(
            self.repository.local_path,
            self.repository.notes_dir
        )
        
        # Add notes to index
        for note in notes:
            self.index.add(note)
        
        logger.info(f"Index rebuilt with {self.index.count()} notes")
        return self.index.count()
    
    def sync_and_rebuild(self) -> tuple[bool, int, Optional[str]]:
        """
        Sync repository and rebuild index.
        
        Returns:
            Tuple of (success: bool, note_count: int, error_message: Optional[str])
        """
        from ..services.git_sync import GitSyncService
        
        # Sync repository
        sync_service = GitSyncService(self.repository)
        success, error = sync_service.sync()
        
        if not success:
            return False, 0, error
        
        # Rebuild index
        try:
            note_count = self.rebuild_index()
            return True, note_count, None
        except Exception as e:
            error_msg = f"Failed to rebuild index: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, 0, error_msg