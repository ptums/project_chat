"""
Project directory mapping service.

Maps project names (DAAS, THN, FF, General, 700B) to directory names
(daas, thn, ff, general, 700b) in the Obsidian notebook repository.
"""
from typing import Dict


class ProjectDirectoryMapper:
    """Maps project names to directory names."""
    
    def __init__(self):
        """Initialize mapper with project to directory mapping."""
        self._mapping: Dict[str, str] = {
            "DAAS": "daas",
            "THN": "thn",
            "FF": "ff",
            "General": "general",
            "700B": "700b"
        }
    
    def get_directory(self, project: str) -> str:
        """
        Get directory name for a project.
        
        Args:
            project: Project name (DAAS, THN, FF, General, 700B)
            
        Returns:
            Directory name (daas, thn, ff, general, 700b)
            Defaults to lowercase of project name if not in mapping
        """
        # Normalize project name (handle case variations)
        project_upper = project.upper() if project else ""
        
        # Check explicit mapping first
        if project_upper in self._mapping:
            return self._mapping[project_upper]
        
        # Handle "GENERAL" -> "general" (common variation)
        if project_upper == "GENERAL":
            return "general"
        
        # Default to lowercase if no explicit mapping
        # This handles edge cases gracefully
        return project.lower() if project else "general"
    
    def is_valid_project(self, project: str) -> bool:
        """
        Check if project has a mapping.
        
        Args:
            project: Project name to check
            
        Returns:
            True if project has explicit mapping, False otherwise
        """
        if not project:
            return False
        
        project_upper = project.upper()
        return project_upper in self._mapping or project_upper == "GENERAL"
