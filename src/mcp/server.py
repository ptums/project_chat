"""
Main MCP server entry point.

Sets up and runs the MCP server with all handlers.
"""
import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any

from .protocol import MCPProtocolHandler
from .resources import ResourcesHandler
from .tools import ToolsHandler
from ..models.repository import Repository
from ..models.index import NoteIndex
from ..services.index_builder import IndexBuilder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # Log to stderr so stdout is only for JSON-RPC
)

logger = logging.getLogger(__name__)


def create_server() -> MCPProtocolHandler:
    """
    Create and configure MCP server.
    
    Returns:
        Configured MCPProtocolHandler
    """
    # Get configuration from environment
    gitlab_url = os.environ.get("GITLAB_URL", "http://192.168.119.200:8201/tumultymedia/meditations")
    repo_path = Path(os.environ.get("REPO_PATH", "/tmp/meditation-mcp-repo"))
    branch = os.environ.get("BRANCH", "main")
    
    logger.info(f"Initializing MCP server with GitLab URL: {gitlab_url}")
    
    # Create repository model
    repository = Repository(
        url=gitlab_url,
        local_path=repo_path,
        branch=branch
    )
    
    # Create note index
    index = NoteIndex()
    
    # Create handlers
    resources_handler = ResourcesHandler(index)
    tools_handler = ToolsHandler(index, repository)
    
    # Create protocol handler
    protocol = MCPProtocolHandler()
    
    # Register resource methods
    protocol.register_method("resources/list", resources_handler.list_resources)
    protocol.register_method("resources/read", resources_handler.read_resource)
    
    # Register tool methods
    protocol.register_method("tools/list", lambda params: {
        "tools": [
            {
                "name": "search_notes",
                "description": "Search meditation notes by keyword",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "sync_repository",
                "description": "Sync meditation notes repository from GitLab",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]
    })
    protocol.register_method("tools/call", lambda params: _handle_tool_call(params, tools_handler))
    
    # Build initial index if repository exists
    if repository.local_path.exists() and (repository.local_path / ".git").exists():
        logger.info("Building initial index from existing repository...")
        builder = IndexBuilder(repository, index)
        try:
            note_count = builder.rebuild_index()
            logger.info(f"Indexed {note_count} notes")
        except Exception as e:
            logger.warning(f"Failed to build initial index: {e}")
    
    return protocol


def _handle_tool_call(params: Dict[str, Any], tools_handler: ToolsHandler) -> Dict[str, Any]:
    """
    Handle tools/call request by routing to appropriate tool.
    
    Args:
        params: Tool call parameters with 'name' and 'arguments'
        tools_handler: ToolsHandler instance
        
    Returns:
        Tool result
    """
    tool_name = params.get("name")
    arguments = params.get("arguments", {})
    
    if tool_name == "search_notes":
        return tools_handler.search_notes(arguments)
    elif tool_name == "sync_repository":
        return tools_handler.sync_repository(arguments)
    else:
        raise ValueError(f"Unknown tool: {tool_name}")


def main():
    """Main entry point for MCP server."""
    protocol = create_server()
    protocol.run()


if __name__ == "__main__":
    main()