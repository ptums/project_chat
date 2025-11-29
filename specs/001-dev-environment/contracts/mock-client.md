# Mock OpenAI Client Contract

**Feature**: Development Environment  
**Date**: 2025-01-27

## Overview

The mock client provides a drop-in replacement for the OpenAI Python SDK client, returning mock responses without making API calls.

## Interface Contract

### Required Interface

The mock client must implement the same interface as `openai.OpenAI`:

```python
client.chat.completions.create(
    model: str,
    messages: list[dict],
    **kwargs
) -> ResponseObject
```

Where `ResponseObject` has:
- `choices`: list of choice objects
- `choices[0]`: first choice object
- `choices[0].message`: message object
- `choices[0].message.content`: string response text

### Response Structure

```python
{
    "choices": [
        {
            "message": {
                "content": "Mock response text"
            }
        }
    ]
}
```

## Behavior Contract

### Response Generation

1. **Input**: User message and conversation history
2. **Processing**: Generate simple acknowledgment response
3. **Output**: Text response indicating mock mode
4. **Performance**: Response time < 100ms (no network calls)

### Response Content

Mock responses must:
- Acknowledge the user's message
- Indicate mock mode clearly
- Reference project context if available
- Be distinguishable from real API responses

### Metadata

When saving mock responses:
- Set `meta.model = "mock"`
- Set `meta.mock_mode = true`
- Include `created_at` timestamp

## Usage Contract

### Initialization

```python
from brain_core.mock_client import MockOpenAIClient

client = MockOpenAIClient()
```

### Usage (Same as OpenAI Client)

```python
response = client.chat.completions.create(
    model="gpt-4.1",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"}
    ]
)

answer = response.choices[0].message.content
```

## Error Handling

- **No network errors**: Mock client never makes network calls
- **No API errors**: No rate limits, no authentication errors
- **Input validation**: Should handle invalid inputs gracefully (log and return default response)

## Testing Contract

### Test Scenarios

1. **Basic response**: Verify response structure matches OpenAI client
2. **Response content**: Verify mock indicator is present
3. **Performance**: Verify response time < 100ms
4. **Metadata**: Verify metadata includes mock flags
5. **Integration**: Verify works with existing `chat.py` code

## Implementation Notes

- Must be importable as `from brain_core.mock_client import MockOpenAIClient`
- Must not require OpenAI SDK to be installed (for development-only use)
- Should be simple and maintainable (no complex AI simulation)

