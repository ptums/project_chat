# Quick Start: Large Text Input Support

**Feature**: Large Text Input Support  
**Date**: 2025-01-27

## Overview

This guide helps you use the enhanced large text input capabilities in the CLI and API for processing dream journals, code blocks, and other lengthy content.

## CLI Usage

### Using `/paste` Mode for Large Text

1. **Start the CLI**:

   ```bash
   python chat_cli.py
   ```

2. **Enter paste mode**:

   ```
   You (THN) 🟢: /paste
   ```

3. **Paste your large text block**:

   - Paste your dream journal entry, code, or other large text
   - Can be thousands of characters
   - Preserves all formatting, newlines, special characters

4. **End the paste**:

   - Type `EOF` on a new line and press Enter
   - Or press Ctrl+D (Unix) / Ctrl+Z (Windows)

5. **Processing**:
   - System confirms receipt: "Received X characters. Processing..."
   - Spinner shows while processing
   - AI response appears when complete

### Example Session

```
You (DAAS) 🟠: /paste
(paste mode) Paste your block now. End with a line containing only EOF
I had another night full of interesting dreams...
[large dream journal entry pasted here]
EOF
Received 5,234 characters. Processing...

AI (DAAS) 🟠: [AI response about the dream]
```

### Normal Input Mode

You can also paste large text directly at the normal prompt:

```
You (THN) 🟢: [paste large text directly]
Detected large input (2,345 characters). Processing...
```

The system automatically detects large pastes and processes them.

## API Usage

### Sending Large Text via API

The API accepts large text in the `message` field:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{
    "conversation_id": "your-conversation-id",
    "message": "Your large text content here...",
    "project": "DAAS"
  }'
```

### Size Limits

- **Default limit**: 16MB (sufficient for 100,000+ character text)
- **No application limit**: Accepts text of any reasonable size
- **Error handling**: Returns 413 if request exceeds limit

## Verification

### Test Large Input

1. **Create a test file** with large content:

   ```bash
   # Create a 10,000 character test file
   python -c "print('A' * 10000)" > test_large.txt
   ```

2. **Paste into CLI**:

   ```bash
   python chat_cli.py
   # Use /paste and paste the content
   ```

3. **Verify**:
   - Check that all content is received
   - Verify no truncation occurs
   - Confirm processing completes successfully

### Check Input Size

The system provides feedback on input size:

- CLI: Shows character count when receiving large input
- API: No explicit size feedback (handled by HTTP)

## Troubleshooting

### Text Still Getting Truncated

**Issue**: Text is still being cut off

**Solutions**:

- Ensure you're using `/paste` mode for very large text
- Check that you're ending with `EOF` on its own line
- Verify terminal supports large paste operations
- Try pasting in smaller chunks if issues persist

### API Returns 413 Error

**Issue**: "Request payload too large" error

**Solutions**:

- Check Flask MAX_CONTENT_LENGTH configuration
- Break very large content into smaller chunks
- Verify request size is under 16MB limit

### Encoding Issues

**Issue**: Special characters or emoji not preserved

**Solutions**:

- Ensure terminal/API client uses UTF-8 encoding
- Check that text source is UTF-8 encoded
- Verify database connection uses UTF-8

## Best Practices

### For Dream Journaling

- Use `/paste` mode for lengthy entries
- Include all details - no need to worry about length
- Use `EOF` to end paste cleanly
- System handles large entries efficiently

### For Code Blocks

- Paste complete code blocks without truncation
- Preserves formatting and indentation
- Can include comments, documentation, etc.
- No need to split into smaller pieces

### For Stream of Consciousness

- Type or paste freely without length concerns
- System captures everything you write
- Can include special characters, emoji, formatting
- Process complete thoughts without interruption

## Next Steps

After setup:

- Start using `/paste` for large dream journal entries
- Paste large code blocks without truncation
- Process lengthy stream-of-consciousness content
- Enjoy unlimited text input capabilities

## Support

For issues or questions:

- Check that you're using `/paste` mode correctly
- Verify `EOF` is on its own line
- Ensure terminal supports large paste operations
- Review troubleshooting section above
