"""
Note saver service.

Saves conversations as markdown notes in the appropriate project directory
and commits/pushes them to the GitLab repository.
"""
import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from urllib.parse import urlparse, urlunparse, quote

import git
from git import Repo, GitCommandError

from ..models.repository import Repository
from ..models.index import NoteIndex
from ..models.note import Note
from ..services.project_filter import ProjectDirectoryMapper
from ..services.note_parser import NoteParser

logger = logging.getLogger(__name__)


class ConversationNote:
    """Represents a conversation to be saved as a note."""
    
    def __init__(self, title: str, project: str, messages: List[Dict[str, Any]], 
                 created_at: Optional[datetime] = None, metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize conversation note.
        
        Args:
            title: Note title
            project: Project name (DAAS, THN, etc.)
            messages: List of message dicts with role, content, timestamp
            created_at: Conversation creation time
            metadata: Additional metadata (tags, etc.)
        """
        self.title = title
        self.project = project
        self.messages = messages
        self.created_at = created_at or datetime.now()
        self.metadata = metadata or {}
    
    def generate_filename(self) -> str:
        """
        Generate filename from title or content.
        
        Returns:
            Filename string (e.g., "morning-planning-session.md")
        """
        if self.title:
            # Convert title to slug
            slug = self._slug_from_title(self.title)
            return f"{slug}.md"
        else:
            # Generate from first user message or timestamp
            if self.messages:
                first_user_msg = next((msg for msg in self.messages if msg.get("role") == "user"), None)
                if first_user_msg:
                    content = first_user_msg.get("content", "")[:50]
                    slug = self._slug_from_title(content)
                    return f"{slug}.md"
            
            # Fallback to timestamp
            timestamp = self.created_at.strftime("%Y-%m-%d-%H%M%S")
            return f"conversation-{timestamp}.md"
    
    def _slug_from_title(self, title: str) -> str:
        """Convert title to slug."""
        # Remove special characters, convert to lowercase, replace spaces with hyphens
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        slug = slug.strip('-')
        # Limit length
        if len(slug) > 100:
            slug = slug[:100]
        return slug
    
    def to_markdown(self) -> str:
        """
        Convert conversation to Obsidian markdown format.
        
        Returns:
            Markdown string with YAML frontmatter
        """
        # Build frontmatter
        frontmatter = {
            "title": self.title,
            "project": self.project,
            "created": self.created_at.isoformat() + "Z",
            "tags": ["conversation", "ai-chat"]
        }
        
        # Add any additional metadata
        if self.metadata:
            frontmatter.update(self.metadata)
        
        # Format frontmatter as YAML
        frontmatter_lines = ["---"]
        for key, value in frontmatter.items():
            if isinstance(value, list):
                frontmatter_lines.append(f"{key}: {value}")
            elif isinstance(value, str):
                # Escape quotes if needed
                if '"' in value:
                    value = value.replace('"', '\\"')
                frontmatter_lines.append(f'{key}: "{value}"')
            else:
                frontmatter_lines.append(f"{key}: {value}")
        frontmatter_lines.append("---")
        
        # Build content
        content_lines = [f"# {self.title}", ""]
        
        for msg in self.messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            timestamp = msg.get("timestamp")
            
            # Format timestamp for display
            time_str = ""
            if timestamp:
                try:
                    if isinstance(timestamp, str):
                        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    else:
                        dt = timestamp
                    time_str = dt.strftime("%I:%M %p")
                except Exception:
                    time_str = ""
            
            # Format message header
            role_display = "User" if role == "user" else "Assistant"
            header = f"## {role_display} Message"
            if time_str:
                header += f" ({time_str})"
            
            content_lines.append(header)
            content_lines.append("")
            content_lines.append(content)
            content_lines.append("")
        
        # Combine frontmatter and content
        return "\n".join(frontmatter_lines) + "\n\n" + "\n".join(content_lines)


class NoteSaver:
    """Service for saving conversations as notes."""
    
    def __init__(self, repository: Repository, index: NoteIndex):
        """
        Initialize note saver.
        
        Args:
            repository: Repository instance
            index: NoteIndex instance
        """
        self.repository = repository
        self.index = index
        self.project_mapper = ProjectDirectoryMapper()
    
    def save_conversation(
        self, 
        conversation_note: ConversationNote,
        gitlab_username: Optional[str] = None,
        gitlab_password: Optional[str] = None
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Save conversation as note in project directory.
        
        Args:
            conversation_note: ConversationNote instance
            gitlab_username: Optional GitLab username for authentication
            gitlab_password: Optional GitLab password or token for authentication
            
        Returns:
            Tuple of (success: bool, file_path: Optional[str], error_message: Optional[str])
        """
        try:
            # Get project directory using ProjectDirectoryMapper
            # Handle case where project might not have explicit mapping
            directory = self.project_mapper.get_directory(conversation_note.project)
            
            # Validate directory (fallback to "general" if invalid)
            if not directory or not self.project_mapper.is_valid_project(conversation_note.project):
                logger.warning(f"Project '{conversation_note.project}' not in mapping, defaulting to 'general'")
                directory = "general"
            
            project_dir = self.repository.local_path / directory
            
            # Create project directory if it doesn't exist
            project_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            filename = conversation_note.generate_filename()
            
            # Handle duplicate filenames
            file_path = project_dir / filename
            counter = 1
            while file_path.exists():
                # Append number before extension
                name_parts = filename.rsplit(".", 1)
                if len(name_parts) == 2:
                    new_filename = f"{name_parts[0]}-{counter}.{name_parts[1]}"
                else:
                    new_filename = f"{filename}-{counter}"
                file_path = project_dir / new_filename
                counter += 1
            
            # Generate markdown content
            markdown_content = conversation_note.to_markdown()
            
            # Write file
            file_path.write_text(markdown_content, encoding='utf-8')
            logger.info(f"Created note file: {file_path}")
            
            # Get relative path for repository
            try:
                relative_path = str(file_path.relative_to(self.repository.local_path))
            except ValueError:
                relative_path = str(file_path)
            
            # Git operations
            if not (self.repository.local_path / ".git").exists():
                error_msg = "Repository not initialized. Run /mcp sync first."
                logger.error(error_msg)
                return False, None, error_msg
            
            repo = Repo(self.repository.local_path)
            
            # Temporarily configure credentials in remote URL if provided
            original_url = None
            if gitlab_username and gitlab_password:
                try:
                    remote = repo.remotes.origin
                    original_url = remote.url
                    
                    # Parse URL and inject credentials
                    parsed = urlparse(original_url)
                    if parsed.scheme in ("http", "https"):
                        # Extract host and port using urlparse attributes (handles passwords with @ correctly)
                        # This is safer than string splitting
                        hostname = parsed.hostname or ''
                        port = f":{parsed.port}" if parsed.port else ''
                        netloc = f"{hostname}{port}"
                        
                        # URL-encode username and password to handle special characters like @, :, etc.
                        encoded_username = quote(gitlab_username, safe='')
                        encoded_password = quote(gitlab_password, safe='')
                        
                        # Build new netloc with encoded credentials
                        new_netloc = f"{encoded_username}:{encoded_password}@{netloc}"
                        authenticated_url = urlunparse((
                            parsed.scheme,
                            new_netloc,
                            parsed.path,
                            parsed.params,
                            parsed.query,
                            parsed.fragment
                        ))
                        
                        # Update remote URL with credentials
                        remote.set_url(authenticated_url)
                        logger.debug("Temporarily configured remote URL with credentials")
                except Exception as e:
                    logger.warning(f"Could not configure credentials in remote URL: {e}")
            
            # Check if repository is out of sync (has remote changes)
            try:
                repo.remotes.origin.fetch()
                local_sha = repo.head.commit.hexsha
                remote_sha = repo.remotes.origin.refs[0].commit.hexsha
                if local_sha != remote_sha:
                    logger.info("Repository out of sync, pulling latest changes...")
                    try:
                        repo.git.pull('origin', self.repository.branch)
                    except GitCommandError as e:
                        # Handle merge conflicts - abort and report
                        if "merge conflict" in str(e).lower() or "CONFLICT" in str(e):
                            logger.error("Merge conflict detected. Aborting save operation.")
                            repo.git.merge('--abort')
                            return False, None, "Repository has conflicts. Please resolve manually and try again."
                        raise
            except Exception as e:
                logger.warning(f"Could not check/pull remote changes: {e}")
                # Continue anyway - might be network issue, but local save should still work
            
            # Stage file
            repo.index.add([relative_path])
            
            # Commit
            commit_message = f"Add conversation note: {conversation_note.title}"
            repo.index.commit(commit_message)
            logger.info(f"Committed note: {commit_message}")
            
            # Push to remote
            push_error = None
            try:
                repo.remotes.origin.push(self.repository.branch)
                logger.info(f"Pushed note to remote repository")
            except GitCommandError as e:
                error_msg = f"Failed to push to repository: {str(e)}"
                logger.error(error_msg)
                # Handle specific error cases
                if "permission denied" in str(e).lower() or "authentication" in str(e).lower():
                    push_error = "Permission denied. Check GitLab credentials."
                elif "network" in str(e).lower() or "connection" in str(e).lower():
                    push_error = "Network error. Note saved locally but not pushed."
                else:
                    push_error = error_msg
            finally:
                # Restore original URL if we modified it
                if original_url:
                    try:
                        repo.remotes.origin.set_url(original_url)
                        logger.debug("Restored original remote URL")
                    except Exception as e:
                        logger.warning(f"Could not restore original remote URL: {e}")
            
            # If push failed, return success with warning
            if push_error:
                return True, relative_path, f"Note saved but push failed: {push_error}"
            
            # Parse and add note to index
            try:
                parsed_note = NoteParser.parse_note(file_path, self.repository.local_path)
                if parsed_note:
                    self.index.add(parsed_note)
                    logger.info(f"Added note to index: {parsed_note.slug}")
            except Exception as e:
                logger.warning(f"Failed to add note to index: {e}")
            
            return True, relative_path, None
            
        except Exception as e:
            error_msg = f"Failed to save conversation note: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, None, error_msg
