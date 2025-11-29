# API Input Contract

**Feature**: Large Text Input Support  
**Date**: 2025-01-27

## Overview

This contract defines how the API accepts and processes large text input from clients.

## Endpoint

### POST /api/chat

**Purpose**: Send chat message with potentially large text content.

## Request Format

### Headers

- `Content-Type: application/json`
- `X-API-Key: <optional_api_key>` (if configured)

### Request Body

```json
{
  "conversation_id": "uuid-string",
  "message": "large text content here...",
  "project": "THN|DAAS|FF|700B|general"
}
```

### Request Size Limits

- **Default Flask limit**: 16MB (sufficient for text)
- **Configured limit**: Explicitly set to handle 100,000+ character text
- **No application-level limit**: Accepts text of any reasonable size

## Response Format

### Success Response (200 OK)

```json
{
  "conversation_id": "uuid-string",
  "project": "DAAS",
  "message": "large text content...",
  "reply": "AI response text"
}
```

### Error Responses

**400 Bad Request** - Missing or invalid parameters:

```json
{
  "error": "message is required"
}
```

**400 Bad Request** - Invalid conversation_id:

```json
{
  "error": "conversation_id is not a valid UUID"
}
```

**413 Payload Too Large** - Request exceeds size limit:

```json
{
  "error": "Request payload too large. Maximum size: 16MB"
}
```

## Text Input Handling

### Message Field

- **Type**: String (UTF-8 text)
- **Size**: No application limit (Flask handles up to configured max)
- **Encoding**: UTF-8
- **Content**: Preserves all characters, newlines, special characters

### Validation

- **Required**: `message` field must be present and non-empty
- **Encoding**: Must be valid UTF-8
- **Size**: Validated against Flask MAX_CONTENT_LENGTH

## Configuration

### Flask MAX_CONTENT_LENGTH

```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
```

This allows:

- Text messages up to ~16MB
- Sufficient for 100,000+ character inputs
- Can be increased if needed

## Error Handling

### Request Size Errors

- **413 Payload Too Large**: Returned if request exceeds MAX_CONTENT_LENGTH
- **Clear error message**: Indicates maximum allowed size
- **Client guidance**: Suggests breaking into smaller chunks if needed

### Encoding Errors

- **400 Bad Request**: Returned for invalid UTF-8
- **Error message**: Indicates encoding issue

### Processing Errors

- **500 Internal Server Error**: For unexpected errors
- **Error logging**: Server logs detailed error information

## Examples

### Example 1: Large Dream Journal Entry

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{
    "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
    "message": "I had another night full of interesting dreams... [5000+ characters]",
    "project": "DAAS"
  }'
```

### Example 2: Large Code Block

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
    "message": "def large_function():\n    # [10000+ character code block]",
    "project": "general"
  }'
```

## Implementation Notes

- Configure Flask MAX_CONTENT_LENGTH for large payloads
- No changes needed to endpoint logic (already accepts text strings)
- JSON parsing handles large strings automatically
- Database TEXT field supports unlimited size
