# Data Model: MCP Server Integration

## Overview

This integration does not introduce new database tables. MCP resources and configuration are managed in memory and via configuration files.

## Configuration Entities

### MCP Server Configuration

**Location**: `mcp_config.json` or `config.py`

**Structure**:
```json
{
  "mcpServers": {
    "meditation-notes": {
      "command": "python",
      "args": ["-m", "src.mcp.server"],
      "env": {
        "GITLAB_URL": "http://192.168.119.200:8201/tumultymedia/meditations"
      },
      "projects": ["DAAS"]  // Optional: associate with specific projects
    }
  }
}
```

**Fields**:
- `command`: Executable command to start MCP server
- `args`: Command-line arguments
- `env`: Environment variables for the server process
- `projects`: Optional list of project tags that should use this server

## In-Memory Entities

### MCP Client State

**Purpose**: Track active MCP server processes and connections

**Fields**:
- `server_name`: String identifier (e.g., "meditation-notes")
- `process`: subprocess.Popen instance
- `initialized`: Boolean (has initialize been called)
- `capabilities`: Dict of server capabilities
- `last_error`: Timestamp and error message of last failure
- `retry_count`: Number of consecutive failures

### MCP Resource Cache

**Purpose**: Cache MCP resources to reduce latency

**Structure**:
```python
{
  "meditation://note/morning-meditation-2024-12-01": {
    "content": "...",
    "mimeType": "text/markdown",
    "cached_at": timestamp,
    "ttl": 300  # seconds
  }
}
```

**Fields**:
- Resource URI as key
- `content`: Resource content (text)
- `mimeType`: MIME type of content
- `cached_at`: Timestamp when cached
- `ttl`: Time-to-live in seconds

### MCP Resource List Cache

**Purpose**: Cache list of available resources

**Structure**:
```python
{
  "server_name": {
    "resources": [...],
    "cached_at": timestamp,
    "ttl": 60  # seconds
  }
}
```

## No Database Changes

- No new tables required
- No schema modifications
- Configuration stored in files, not database
- Resources cached in memory only

