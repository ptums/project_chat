# CLI Contract: MCP Integration

## New Commands

### `/mcp list [server]`

List available MCP resources from a server.

**Usage**:
```
/mcp list
/mcp list meditation-notes
```

**Behavior**:
- If no server specified, list resources from all configured servers
- If server specified, list resources from that server only
- Display resource URIs, names, and descriptions
- Use cached resource list if available

**Output Format**:
```
MCP Resources (meditation-notes):
  meditation://note/morning-meditation-2024-12-01 - Morning Meditation - Dec 1
  meditation://note/evening-meditation-2024-12-01 - Evening Meditation - Dec 1
  ...
```

### `/mcp read <uri>`

Read a specific MCP resource.

**Usage**:
```
/mcp read meditation://note/morning-meditation-2024-12-01
```

**Behavior**:
- Read resource from MCP server
- Display content (formatted if markdown)
- Use cached resource if available and not expired
- Show error if resource not found

**Output Format**:
```
Resource: meditation://note/morning-meditation-2024-12-01
==================================================

# Morning Meditation

Content here...
```

### `/mcp search <server> <query> [limit]`

Search MCP resources using a tool.

**Usage**:
```
/mcp search meditation-notes "morning routine"
/mcp search meditation-notes "meditation" 5
```

**Behavior**:
- Call search_notes tool (or equivalent) on specified server
- Display search results
- Limit results to specified number (default: 10)

**Output Format**:
```
Search Results (meditation-notes): "morning routine"
==================================================

Found 3 notes:

1. Morning Meditation - Dec 1
   meditation://note/morning-meditation-2024-12-01
   Brief description...

2. Morning Routine
   meditation://note/morning-routine
   Brief description...
```

### `/mcp sync [server]`

Sync MCP server repository and update index.

**Usage**:
```
/mcp sync
/mcp sync meditation-notes
```

**Behavior**:
- If no server specified, sync all configured servers
- If server specified, sync that server only
- Call sync_repository tool (or equivalent)
- Invalidate resource cache after sync
- Display sync status

**Output Format**:
```
Syncing meditation-notes...
Repository sync completed. Found 45 notes (3 new). Index updated.
✓ Sync complete
```

### `/mcp status`

Show status of all configured MCP servers.

**Usage**:
```
/mcp status
```

**Behavior**:
- List all configured MCP servers
- Show connection status (connected/disconnected/error)
- Show last error if any
- Show number of cached resources

**Output Format**:
```
MCP Server Status:
==================================================
meditation-notes: ✓ Connected (42 resources cached)
code-index: ✗ Disconnected (Error: Process not found)
```

## Error Messages

### Server Not Configured
```
Error: MCP server 'meditation-notes' not configured.
Use /mcp status to see available servers.
```

### Server Not Available
```
Error: MCP server 'meditation-notes' is not available.
Last error: Connection timeout
```

### Resource Not Found
```
Error: Resource 'meditation://note/non-existent' not found.
```

### Tool Not Available
```
Error: Tool 'search_notes' not available on server 'meditation-notes'.
```

## Integration with Existing Commands

### Context Building

MCP resources are automatically included in conversation context when:
- Project is associated with an MCP server (via config)
- User message contains keywords that match resource names
- Context builder determines MCP resources are relevant

No CLI changes required - automatic background integration.

