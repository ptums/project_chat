"""
MCP (Model Context Protocol) server configuration management.

Handles loading and managing MCP server configurations from JSON files
and environment variables.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


def load_mcp_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load MCP server configuration from JSON file.
    
    Args:
        config_path: Path to mcp_config.json file. If None, looks for mcp_config.json in project root.
        
    Returns:
        Dictionary with MCP server configurations
    """
    if config_path is None:
        # Look for mcp_config.json in project root
        project_root = Path(__file__).parent.parent
        config_path = project_root / "mcp_config.json"
    
    config_path = Path(config_path)
    
    if not config_path.exists():
        logger.debug(f"MCP config file not found at {config_path}")
        return {}
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        servers = config.get("mcpServers", {})
        logger.info(f"Loaded MCP configuration from {config_path}: {len(servers)} server(s)")
        return servers
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse MCP config file {config_path}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error loading MCP config file {config_path}: {e}")
        return {}


def resolve_env_variables(server_config: Dict[str, Any], server_name: str) -> Dict[str, Any]:
    """
    Resolve environment variables in server configuration.
    
    Supports:
    - Server-specific env vars: MCP_{SERVER_NAME}_{VAR_NAME}
    - Generic env vars: MCP_{VAR_NAME}
    - Direct env values in config
    
    Args:
        server_config: Server configuration dict
        server_name: Name of the server (for server-specific env vars)
        
    Returns:
        Configuration with environment variables resolved
    """
    resolved = server_config.copy()
    
    # Resolve env dict
    if "env" in resolved:
        env_dict = resolved["env"].copy()
        
        # Check for server-specific env vars first
        server_prefix = f"MCP_{server_name.upper().replace('-', '_')}_"
        generic_prefix = "MCP_"
        
        for key in list(env_dict.keys()):
            # Try server-specific first
            env_key = server_prefix + key.upper().replace('-', '_')
            if env_key in os.environ:
                env_dict[key] = os.environ[env_key]
            # Then try generic
            elif generic_prefix + key.upper().replace('-', '_') in os.environ:
                env_dict[key] = os.environ[generic_prefix + key.upper().replace('-', '_')]
            # If value in config looks like an env var reference, resolve it
            elif isinstance(env_dict[key], str) and env_dict[key].startswith("${") and env_dict[key].endswith("}"):
                env_var_name = env_dict[key][2:-1]
                if env_var_name in os.environ:
                    env_dict[key] = os.environ[env_var_name]
        
        resolved["env"] = env_dict
    
    return resolved


def validate_server_config(server_name: str, config: Dict[str, Any]) -> bool:
    """
    Validate MCP server configuration.
    
    Args:
        server_name: Name of the server
        config: Server configuration dict
        
    Returns:
        True if valid, False otherwise
    """
    if "command" not in config:
        logger.error(f"MCP server '{server_name}' missing required 'command' field")
        return False
    
    if not isinstance(config.get("args", []), list):
        logger.error(f"MCP server '{server_name}' 'args' must be a list")
        return False
    
    if "env" in config and not isinstance(config["env"], dict):
        logger.error(f"MCP server '{server_name}' 'env' must be a dictionary")
        return False
    
    return True


class MCPConfig:
    """
    Manages MCP server configurations.
    
    Loads configurations from JSON file and environment variables,
    validates them, and provides access to server configurations.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize MCP configuration manager.
        
        Args:
            config_path: Path to mcp_config.json file. If None, looks for mcp_config.json in project root.
        """
        self.config_path = config_path
        self._servers: Dict[str, Dict[str, Any]] = {}
        self._project_to_servers: Dict[str, List[str]] = {}
        self._load_config()
    
    def _load_config(self):
        """Load and validate MCP server configurations."""
        raw_config = load_mcp_config(self.config_path)
        
        for server_name, server_config in raw_config.items():
            # Resolve environment variables
            resolved_config = resolve_env_variables(server_config, server_name)
            
            # Validate configuration
            if not validate_server_config(server_name, resolved_config):
                logger.warning(f"Skipping invalid MCP server configuration: {server_name}")
                continue
            
            self._servers[server_name] = resolved_config
            
            # Build project-to-server mapping
            projects = resolved_config.get("projects", [])
            for project in projects:
                if project not in self._project_to_servers:
                    self._project_to_servers[project] = []
                self._project_to_servers[project].append(server_name)
        
        logger.info(f"MCP configuration loaded: {len(self._servers)} server(s), {len(self._project_to_servers)} project(s)")
    
    def get_server_config(self, server_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific server.
        
        Args:
            server_name: Name of the server
            
        Returns:
            Server configuration dict or None if not found
        """
        return self._servers.get(server_name)
    
    def get_all_servers(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all server configurations.
        
        Returns:
            Dictionary mapping server names to configurations
        """
        return self._servers.copy()
    
    def get_servers_for_project(self, project: str) -> List[str]:
        """
        Get list of MCP servers associated with a project.
        
        Args:
            project: Project tag (e.g., "DAAS", "THN")
            
        Returns:
            List of server names
        """
        return self._project_to_servers.get(project, []).copy()
    
    def has_server(self, server_name: str) -> bool:
        """
        Check if a server is configured.
        
        Args:
            server_name: Name of the server
            
        Returns:
            True if server is configured, False otherwise
        """
        return server_name in self._servers


# Global MCP configuration instance
_mcp_config: Optional[MCPConfig] = None


def get_mcp_config() -> MCPConfig:
    """
    Get global MCP configuration instance.
    
    Returns:
        MCPConfig instance
    """
    global _mcp_config
    if _mcp_config is None:
        _mcp_config = MCPConfig()
    return _mcp_config

