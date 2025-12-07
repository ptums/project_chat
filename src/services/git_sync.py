"""
GitLab repository sync service.

Handles cloning and pulling meditation notes from GitLab repository.
"""
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

import git
from git import Repo, GitCommandError

from ..models.repository import Repository

logger = logging.getLogger(__name__)


class GitSyncService:
    """Service for syncing GitLab repository."""
    
    def __init__(self, repository: Repository):
        """
        Initialize Git sync service.
        
        Args:
            repository: Repository configuration
        """
        self.repository = repository
    
    
    def sync(self) -> tuple[bool, Optional[str]]:
        """
        Sync repository (clone if needed, pull if exists).
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            if self.repository.local_path.exists() and (self.repository.local_path / ".git").exists():
                # Repository exists, pull latest changes
                logger.info(f"Pulling repository from {self.repository.url}")
                repo = Repo(self.repository.local_path)
                
                # Fetch latest changes
                repo.remotes.origin.fetch()
                
                # Pull current branch
                repo.git.pull('origin', self.repository.branch)
                
                logger.info(f"Repository synced successfully")
                self.repository.last_sync = datetime.now()
                self.repository.sync_error = None
                return True, None
            else:
                # Repository doesn't exist, clone it
                logger.info(f"Cloning repository from {self.repository.url}")
                
                # Create parent directory if needed
                self.repository.local_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Clone repository
                repo = Repo.clone_from(
                    self.repository.url,
                    str(self.repository.local_path),
                    branch=self.repository.branch
                )
                
                logger.info(f"Repository cloned successfully")
                self.repository.last_sync = datetime.now()
                self.repository.sync_error = None
                return True, None
                
        except GitCommandError as e:
            error_msg = f"Git error: {str(e)}"
            logger.error(error_msg)
            self.repository.sync_error = error_msg
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error during sync: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.repository.sync_error = error_msg
            return False, error_msg