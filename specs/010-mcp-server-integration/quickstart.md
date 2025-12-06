# Quickstart: MCP Server Integration

## Overview

This guide shows how to configure and use MCP server integration in project_chat, specifically for the meditation MCP server.

## Prerequisites

1. Meditation MCP server installed and accessible
2. GitLab repository accessible (for meditation notes)
3. Python 3.10+ (existing requirement)

## Configuration

### Step 1: Create MCP Configuration File

Create `mcp_config.json` in project root:

```json
{
  "mcpServers": {
    "meditation-notes": {
      "command": "python",
      "args": ["-m", "src.mcp.server"],
      "env": {
        "GITLAB_URL": "http://192.168.119.200:8201/tumultymedia/meditations"
      },
      "projects": ["DAAS"]
    }
  }
}
```

### Step 2: Set Environment Variables (Optional)

If you need to pass additional environment variables:

```bash
export MCP_MEDITATION_GITLAB_TOKEN=your-token-here
export MCP_MEDITATION_GITLAB_BRANCH=main
```

Or add to `.env` file:
```
MCP_MEDITATION_GITLAB_TOKEN=your-token-here
MCP_MEDITATION_GITLAB_BRANCH=main
```

### Step 3: Verify Configuration

Start project_chat and check MCP status:

```bash
python3 chat_cli.py
```

In chat, run:
```
/mcp status
```

Expected output:
```
MCP Server Status:
==================================================
meditation-notes: ✓ Connected (42 resources cached)
```

## Usage Examples

### Example 1: List Meditation Notes

```
You (DAAS) 🟣: /mcp list meditation-notes
```

Output:
```
MCP Resources (meditation-notes):
  meditation://note/morning-meditation-2024-12-01 - Morning Meditation - Dec 1
  meditation://note/evening-meditation-2024-12-01 - Evening Meditation - Dec 1
  ...
```

### Example 2: Read a Specific Note

```
You (DAAS) 🟣: /mcp read meditation://note/morning-meditation-2024-12-01
```

Output:
```
Resource: meditation://note/morning-meditation-2024-12-01
==================================================

# Morning Meditation

Today's meditation focused on...
```

### Example 3: Search Notes

```
You (DAAS) 🟣: /mcp search meditation-notes "morning routine"
```

Output:
```
Search Results (meditation-notes): "morning routine"
==================================================

Found 3 notes:

1. Morning Meditation - Dec 1
   meditation://note/morning-meditation-2024-12-01
   ...

2. Morning Routine
   meditation://note/morning-routine
   ...
```

### Example 4: Sync Repository

```
You (DAAS) 🟣: /mcp sync meditation-notes
```

Output:
```
Syncing meditation-notes...
Repository sync completed. Found 45 notes (3 new). Index updated.
✓ Sync complete
```

### Example 5: Automatic Context Integration

When discussing meditation topics in DAAS project, relevant meditation notes are automatically included in context:

```
You (DAAS) 🟣: What did I write about morning meditation last week?
```

The system automatically:
1. Detects "morning meditation" keyword
2. Searches meditation notes via MCP
3. Includes relevant notes in conversation context
4. AI responds with context from your notes

## Troubleshooting

### Issue: MCP Server Not Found

**Symptoms**: `/mcp status` shows server as disconnected

**Solutions**:
1. Verify MCP server is installed and accessible
2. Check `command` and `args` in `mcp_config.json`
3. Verify Python path can find MCP server module
4. Check server logs for errors

### Issue: Connection Timeout

**Symptoms**: MCP requests timeout

**Solutions**:
1. Verify GitLab repository is accessible
2. Check network connectivity
3. Verify environment variables are set correctly
4. Check MCP server logs

### Issue: Resources Not Found

**Symptoms**: `/mcp list` returns empty list

**Solutions**:
1. Run `/mcp sync` to update index
2. Verify repository has .md files
3. Check MCP server logs for parsing errors
4. Verify repository path in configuration

### Issue: Slow Performance

**Symptoms**: MCP commands take >1 second

**Solutions**:
1. Check cache is working (resources should be cached)
2. Verify MCP server is running (not restarting each time)
3. Check repository size (should handle 1000+ notes)
4. Check network latency to GitLab

## Advanced Configuration

### Multiple MCP Servers

You can configure multiple MCP servers:

```json
{
  "mcpServers": {
    "meditation-notes": {
      "command": "python",
      "args": ["-m", "src.mcp.server"],
      "env": {
        "GITLAB_URL": "http://192.168.119.200:8201/tumultymedia/meditations"
      },
      "projects": ["DAAS"]
    },
    "code-index": {
      "command": "python",
      "args": ["-m", "src.mcp.code_server"],
      "env": {
        "REPO_PATH": "../repos"
      },
      "projects": ["THN"]
    }
  }
}
```

### Project-Specific Servers

Associate MCP servers with specific projects:

```json
{
  "mcpServers": {
    "meditation-notes": {
      "projects": ["DAAS"]
    }
  }
}
```

When in DAAS project, meditation notes are automatically included in context.

## Next Steps

1. Test MCP integration with meditation server
2. Configure additional MCP servers as needed
3. Use `/mcp` commands to explore available resources
4. Let automatic context integration enhance conversations

