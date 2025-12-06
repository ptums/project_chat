# MCP Server Integration

## Overview

Integrate Model Context Protocol (MCP) server support into project_chat to enable access to external resources and tools. The initial integration will support the meditation MCP server, which provides access to meditation notes stored in a GitLab repository.

## Requirements

### 1. MCP Client Infrastructure

- Implement MCP client that communicates via JSON-RPC over stdio
- Support stdio transport for MCP server communication
- Handle MCP protocol initialization and capabilities negotiation
- Support resource discovery and retrieval
- Support tool invocation

### 2. Configuration Management

- Add MCP server configuration to project_chat config system
- Support multiple MCP servers (extensible for future servers)
- Configuration via environment variables or config file
- Support for server-specific environment variables

### 3. Meditation MCP Server Integration

- Configure meditation MCP server connection
- Access meditation notes as resources during conversations
- Support search_notes tool for finding relevant meditation content
- Support sync_repository tool for updating note index
- Integrate meditation notes into conversation context when relevant

### 4. Context Integration

- Automatically include relevant MCP resources in conversation context
- Support project-specific MCP server associations (e.g., meditation notes for DAAS project)
- Graceful degradation if MCP server unavailable
- Cache MCP resources to reduce latency

### 5. CLI Integration

- Add `/mcp` command for manual MCP operations
- Support listing available MCP resources
- Support searching MCP resources
- Support manual sync operations

## Technical Details

### MCP Server Configuration

The meditation MCP server should be configured as:

```json
{
  "mcpServers": {
    "meditation-notes": {
      "command": "python",
      "args": ["-m", "src.mcp.server"],
      "env": {
        "GITLAB_URL": "http://192.168.119.200:8201/tumultymedia/meditations"
      }
    }
  }
}
```

### MCP Protocol Support

- JSON-RPC 2.0 over stdio
- Protocol version: 2024-11-05
- Resources: list and read operations
- Tools: call operations
- Error handling with appropriate JSON-RPC error codes

### Integration Points

1. **Context Building**: MCP resources can be included in conversation context
2. **Tool Invocation**: MCP tools can be called during conversations
3. **Resource Access**: MCP resources can be read and included in responses
4. **Project Association**: MCP servers can be associated with specific projects

## Use Cases

1. **Automatic Context**: When discussing meditation topics in DAAS project, automatically include relevant meditation notes
2. **Manual Search**: User can search meditation notes using `/mcp search meditation-notes "morning routine"`
3. **Resource Access**: User can read specific meditation notes using `/mcp read meditation://note/morning-meditation-2024-12-01`
4. **Sync**: User can sync meditation repository using `/mcp sync meditation-notes`

## Constraints

- Must not break existing functionality
- Must handle MCP server failures gracefully
- Must support async/background operations for MCP calls
- Must cache MCP resources to avoid excessive calls
- Must respect rate limits if MCP server has them

