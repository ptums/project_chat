# API Contracts: Project-Organized Notes

## MCP API Extensions

### `list_resources_by_project(project: str) -> List[Dict[str, Any]]`

List all resources filtered by project directory.

**Parameters**:

- `project`: Project name (DAAS, THN, FF, General, 700B)

**Returns**: List of resource dictionaries with uri, name, description, mimeType

**Example**:

```python
api = get_mcp_api()
resources = api.list_resources_by_project("DAAS")
# Returns only notes from "daas/" directory
```

### `get_project_notes(project: str, user_message: str, limit: int = 5) -> List[Dict[str, Any]]`

Get relevant notes for a project based on user message.

**Parameters**:

- `project`: Project name
- `user_message`: User message for keyword matching
- `limit`: Maximum number of notes to return

**Returns**: List of note dictionaries with uri, title, content snippet

**Example**:

```python
api = get_mcp_api()
notes = api.get_project_notes("DAAS", "morning routine", limit=3)
```

### `save_conversation(project: str, messages: List[Dict], title: Optional[str] = None) -> Dict[str, Any]`

Save a conversation as a note in the project directory.

**Parameters**:

- `project`: Project name
- `messages`: List of message dicts with role, content, timestamp
- `title`: Optional title for the note

**Returns**: Dict with success status, file_path, and message

**Example**:

```python
api = get_mcp_api()
result = api.save_conversation(
    project="DAAS",
    messages=[
        {"role": "user", "content": "Hello", "timestamp": "2025-12-07T10:30:00Z"},
        {"role": "assistant", "content": "Hi there!", "timestamp": "2025-12-07T10:30:05Z"}
    ],
    title="My Conversation"
)
# Returns: {"success": True, "file_path": "daas/my-conversation.md", "message": "Note saved"}
```

## Project Directory Mapper

### `get_directory(project: str) -> str`

Map project name to directory name.

**Parameters**:

- `project`: Project name (DAAS, THN, FF, General, 700B)

**Returns**: Directory name (daas, thn, ff, general, 700b)

**Example**:

```python
mapper = ProjectDirectoryMapper()
directory = mapper.get_directory("DAAS")  # Returns "daas"
```
