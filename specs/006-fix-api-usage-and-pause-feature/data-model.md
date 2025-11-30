# Data Model: Fix API Usage Display and Add Pause Feature

## 1. SessionUsageTracker (EXISTING - Bug Fix)

| Attribute | Type | Notes |
|-----------|------|-------|
| usage_records | list[UsageRecord] | List of all API call usage records |
| total_prompt_tokens | int | Sum of all prompt tokens |
| total_completion_tokens | int | Sum of all completion tokens |
| total_tokens | int | Sum of all total tokens |
| total_cost | float | Sum of all costs |
| api_call_count | int | Number of API calls made |
| models_used | set[str] | Set of model names used |
| has_mock_mode | bool | Whether mock mode was used |

**Bug Fix**: Ensure usage is properly recorded from streaming responses. Usage data comes in final chunk with `done=True`.

**Operations**:
- **Read**: `get_summary()` - Returns aggregated usage data
- **Update**: `record_usage()` - Records usage from API call (must work for both streaming and non-streaming)

## 2. Streaming State (NEW - For Pause Feature)

| Attribute | Type | Notes |
|-----------|------|-------|
| is_streaming | bool | Whether streaming is currently active |
| pause_requested | threading.Event | Event flag set when `@@` is detected |
| pause_detector_thread | threading.Thread | Background thread monitoring for `@@` |

**Operations**:
- **Start**: When streaming begins, set `is_streaming=True`, start pause detector thread
- **Check**: Streaming loop checks `pause_requested.is_set()` periodically
- **Stop**: When streaming ends (normally or paused), set `is_streaming=False`, stop pause detector thread

## 3. Partial Response (EXISTING - Enhanced for Pause)

| Attribute | Type | Notes |
|-----------|------|-------|
| reply | str | Accumulated response content during streaming |
| partial | bool | Whether response is complete or partial |

**Operations**:
- **Accumulate**: Add chunks to `reply` during streaming
- **Save**: Save `reply` to database when streaming completes or is paused
- **Display**: Show partial response indicator when paused

## State Transitions

### Usage Tracking Flow

```
API Call Made
  ↓
Response Received (streaming or non-streaming)
  ↓
Extract Usage Data (tokens, model, cost)
  ↓
Record in SessionUsageTracker
  ↓
Display on Exit (get_summary())
```

**Bug Fix**: Ensure usage data is extracted from final streaming chunk with `done=True`.

### Streaming with Pause Flow

```
User sends message
  ↓
Start streaming (is_streaming=True)
  ↓
Start pause detector thread
  ↓
Stream chunks and display
  ↓
[User types @@] → pause_requested.set()
  ↓
Check pause_requested in loop
  ↓
Break from streaming loop
  ↓
Save partial response
  ↓
Stop pause detector thread (is_streaming=False)
  ↓
Return to input prompt
```

### Normal Streaming Flow (No Pause)

```
User sends message
  ↓
Start streaming (is_streaming=True)
  ↓
Start pause detector thread
  ↓
Stream chunks and display
  ↓
Streaming completes normally
  ↓
Save complete response
  ↓
Stop pause detector thread (is_streaming=False)
  ↓
Continue to next input
```

## Validation Rules

### Usage Tracking
- **Rule**: `api_call_count` must match number of successful API calls
- **Enforcement**: Verify usage is recorded for every API call (streaming and non-streaming)
- **Error Handling**: Log warnings if usage tracking fails, but don't fail the API call

### Pause Detection
- **Rule**: `@@` only triggers pause when `is_streaming=True`
- **Enforcement**: Check streaming state before treating `@@` as pause command
- **Error Handling**: If pause detection fails, continue streaming normally

### Partial Response
- **Rule**: Partial responses must be saved to database
- **Enforcement**: Always save `reply` content, even if incomplete
- **Error Handling**: If save fails, display error but continue

## Relationships

- `SessionUsageTracker` aggregates usage from all API calls (streaming and non-streaming)
- Streaming state (`is_streaming`, `pause_requested`) controls pause detection
- Partial response (`reply`) is saved when streaming is paused or interrupted

## Data Consistency Requirements

1. **Usage Accuracy**: `api_call_count` must accurately reflect number of API calls made
2. **Token Totals**: `total_tokens` must equal `total_prompt_tokens + total_completion_tokens`
3. **Cost Calculation**: `total_cost` must match sum of individual call costs
4. **Pause State**: `is_streaming` must accurately reflect streaming status
5. **Partial Response**: Partial responses must be saved with correct conversation_id

