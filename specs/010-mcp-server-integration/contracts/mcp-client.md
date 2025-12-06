# MCP Client Contract

## Overview

The MCP client communicates with MCP servers using JSON-RPC 2.0 over stdio.

## Protocol

### Transport
- **Method**: stdio (stdin/stdout)
- **Format**: JSON-RPC 2.0
- **Encoding**: UTF-8

### Protocol Version
- **Version**: 2024-11-05

## Initialization

### Initialize Request

**Method**: `initialize`

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "project_chat",
      "version": "1.0"
    }
  }
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "resources": {},
      "tools": {}
    },
    "serverInfo": {
      "name": "meditation-mcp",
      "version": "1.0"
    }
  }
}
```

## Resources

### List Resources

**Method**: `resources/list`

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "resources/list"
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "resources": [
      {
        "uri": "meditation://note/morning-meditation-2024-12-01",
        "name": "Morning Meditation - Dec 1",
        "description": "Meditation note",
        "mimeType": "text/markdown"
      }
    ]
  }
}
```

### Read Resource

**Method**: `resources/read`

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "resources/read",
  "params": {
    "uri": "meditation://note/morning-meditation-2024-12-01"
  }
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "contents": [
      {
        "uri": "meditation://note/morning-meditation-2024-12-01",
        "mimeType": "text/markdown",
        "text": "# Morning Meditation\n\nContent here..."
      }
    ]
  }
}
```

**Error Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "error": {
    "code": -32000,
    "message": "Resource not found",
    "data": {
      "uri": "meditation://note/non-existent"
    }
  }
}
```

## Tools

### List Tools

**Method**: `tools/list`

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/list"
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "result": {
    "tools": [
      {
        "name": "search_notes",
        "description": "Search meditation notes",
        "inputSchema": {
          "type": "object",
          "properties": {
            "query": {"type": "string"},
            "limit": {"type": "integer"}
          }
        }
      },
      {
        "name": "sync_repository",
        "description": "Sync repository and update index"
      }
    ]
  }
}
```

### Call Tool

**Method**: `tools/call`

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "tools/call",
  "params": {
    "name": "search_notes",
    "arguments": {
      "query": "morning",
      "limit": 10
    }
  }
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Found 3 notes matching 'morning':\n\n1. Morning Meditation - Dec 1\n2. Morning Routine\n..."
      }
    ]
  }
}
```

## Error Handling

### Error Codes

- `-32700`: Parse error
- `-32600`: Invalid Request
- `-32601`: Method not found
- `-32602`: Invalid params
- `-32603`: Internal error
- `-32000`: Server error (custom, e.g., "Resource not found")

### Timeout Handling

- Resource requests: 500ms timeout
- Tool invocations: 1000ms timeout
- Initialize: 2000ms timeout

## Client Implementation Requirements

1. **Process Management**:
   - Start MCP server process on first use
   - Keep process alive for session
   - Handle process crashes and restart
   - Shutdown gracefully on exit

2. **Request/Response**:
   - Send JSON-RPC requests via stdin
   - Read JSON-RPC responses from stdout
   - Handle JSON parsing errors
   - Handle timeout errors

3. **Error Recovery**:
   - Retry with exponential backoff on failure
   - Graceful degradation if server unavailable
   - Clear error messages to user

4. **Caching**:
   - Cache resources with TTL
   - Cache resource lists
   - Invalidate cache on sync operations

