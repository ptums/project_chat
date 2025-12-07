"""
Obsidian markdown note parser.

Parses Obsidian markdown files with YAML frontmatter into Note entities.
"""
import logging
import re
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

import frontmatter
import markdown

from ..models.note import Note

logger = logging.getLogger(__name__)


class NoteParser:
    """Service for parsing Obsidian markdown notes."""
    
    @staticmethod
    def slug_from_filename(filename: str) -> str:
        """
        Generate slug from filename.
        
        Args:
            filename: File name (with or without extension)
            
        Returns:
            Slug string
        """
        # Remove extension
        name = Path(filename).stem
        
        # Convert to lowercase and replace spaces/hyphens with hyphens
        slug = re.sub(r'[^\w\s-]', '', name.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        slug = slug.strip('-')
        
        return slug
    
    @staticmethod
    def parse_note(file_path: Path, repo_path: Path) -> Optional[Note]:
        """
        Parse a markdown file into a Note entity.
        
        Args:
            file_path: Path to markdown file
            repo_path: Repository root path (for relative paths)
            
        Returns:
            Note entity or None if parsing fails
        """
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse frontmatter
            post = frontmatter.loads(content)
            frontmatter_data = post.metadata if post.metadata else {}
            body = post.content
            
            # Generate slug from filename
            slug = NoteParser.slug_from_filename(file_path.name)
            
            # Extract title from frontmatter or first heading or filename
            title = frontmatter_data.get('title')
            if not title:
                # Try to extract from first heading
                heading_match = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
                if heading_match:
                    title = heading_match.group(1).strip()
                else:
                    title = file_path.stem
            
            # Get relative file path
            try:
                relative_path = str(file_path.relative_to(repo_path))
            except ValueError:
                relative_path = str(file_path)
            
            # Get file modification time
            try:
                last_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
            except (OSError, ValueError):
                last_modified = None
            
            return Note(
                slug=slug,
                title=title,
                content=body,
                frontmatter=frontmatter_data,
                file_path=relative_path,
                last_modified=last_modified
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse note {file_path}: {e}")
            return None
    
    @staticmethod
    def find_notes(repo_path: Path, notes_dir: Path) -> list[Note]:
        """
        Find and parse all markdown notes in repository.
        
        Args:
            repo_path: Repository root path
            notes_dir: Directory containing notes (may be repo root)
            
        Returns:
            List of Note entities
        """
        notes = []
        
        if not notes_dir.exists():
            logger.warning(f"Notes directory does not exist: {notes_dir}")
            return notes
        
        logger.info(f"Searching for markdown files in: {notes_dir}")
        
        # Find all .md files, but exclude common non-note files
        exclude_dirs = {'.git', '__pycache__', '.venv', 'venv', 'node_modules'}
        exclude_files = {'README.md', 'readme.md', 'CHANGELOG.md', 'LICENSE.md'}
        
        md_files_found = 0
        for md_file in notes_dir.rglob("*.md"):
            md_files_found += 1
            # Skip if in excluded directory
            if any(excluded in md_file.parts for excluded in exclude_dirs):
                logger.debug(f"Skipping {md_file} (in excluded directory)")
                continue
            
            # Skip common non-note files
            if md_file.name in exclude_files:
                logger.debug(f"Skipping {md_file} (excluded file)")
                continue
            
            logger.debug(f"Parsing note: {md_file}")
            note = NoteParser.parse_note(md_file, repo_path)
            if note:
                notes.append(note)
                logger.debug(f"Successfully parsed note: {note.slug} - {note.title}")
            else:
                logger.warning(f"Failed to parse note: {md_file}")
        
        logger.info(f"Found {md_files_found} markdown files, parsed {len(notes)} notes from {notes_dir}")
        return notes