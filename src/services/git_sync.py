"""
GitLab repository sync service.

Handles cloning and pulling meditation notes from GitLab repository.
"""
import logging
import os
from pathlib import Path
from typing import Optional
from datetime import datetime
from urllib.parse import urlparse, urlunparse

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
    
    def _get_authenticated_url(self, url: str) -> str:
        """
        Get URL with credentials if available from environment.
        
        Args:
            url: Original repository URL
            
        Returns:
            URL with credentials embedded if available
        """
        gitlab_username = os.getenv("GITLAB_USERNAME") or os.getenv("GITLAB_USER")
        gitlab_token = os.getenv("GITLAB_TOKEN") or os.getenv("GITLAB_PASSWORD")
        
        if gitlab_username and gitlab_token:
            # Check if credentials are already in URL
            if "@" not in url or gitlab_username not in url:
                parsed = urlparse(url)
                if parsed.scheme in ("http", "https"):
                    new_netloc = f"{gitlab_username}:{gitlab_token}@{parsed.netloc.split('@')[-1]}"
                    return urlunparse((
                        parsed.scheme,
                        new_netloc,
                        parsed.path,
                        parsed.params,
                        parsed.query,
                        parsed.fragment
                    ))
        
        return url
    
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
                
                # Configure credentials if needed
                authenticated_url = self._get_authenticated_url(self.repository.url)
                if authenticated_url != self.repository.url:
                    try:
                        repo.remotes.origin.set_url(authenticated_url)
                        logger.debug("Updated remote URL with credentials")
                    except Exception as e:
                        logger.warning(f"Could not update remote URL: {e}")
                
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
                
                # Get authenticated URL for cloning
                authenticated_url = self._get_authenticated_url(self.repository.url)
                
                # Clone repository
                repo = Repo.clone_from(
                    authenticated_url,
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