"""
Repository entity for GitLab meditation notes repository.

Manages the local clone/pull state of the repository.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from pathlib import Path


@dataclass
class Repository:
    """Repository state and configuration."""
    
    url: str
    local_path: Path
    branch: str = "main"
    last_sync: Optional[datetime] = None
    sync_error: Optional[str] = None
    
    @property
    def notes_dir(self) -> Path:
        """
        Path to notes directory within repository.
        
        Tries multiple common locations:
        1. notes/ subdirectory
        2. Root of repository (if notes/ doesn't exist)
        """
        notes_subdir = self.local_path / "notes"
        if notes_subdir.exists() and notes_subdir.is_dir():
            return notes_subdir
        # If notes/ doesn't exist, use repository root
        return self.local_path
    
    def to_dict(self) -> dict:
        """Convert repository to dictionary."""
        return {
            "url": self.url,
            "local_path": str(self.local_path),
            "branch": self.branch,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "sync_error": self.sync_error
        }