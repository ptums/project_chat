# Data Model: OpenAI Usage and Cost Tracking

**Feature**: OpenAI Usage and Cost Tracking  
**Date**: 2025-01-27

## Overview

This feature tracks OpenAI API usage during a CLI session. All data is stored in-memory (no database persistence). The data model consists of three main entities: UsageRecord, SessionUsageTracker, and ModelPricing.

## Entities

### UsageRecord

Represents a single API call's usage data.

**Attributes**:
- `prompt_tokens` (int): Number of tokens in the input/prompt
- `completion_tokens` (int): Number of tokens in the AI's response
- `total_tokens` (int): Sum of prompt_tokens + completion_tokens
- `model` (str): Model name used for this API call (e.g., "gpt-4", "gpt-3.5-turbo")
- `cost` (float): Calculated cost for this API call in dollars
- `timestamp` (datetime): When this API call was made (optional, for future use)

**Validation Rules**:
- `prompt_tokens >= 0`
- `completion_tokens >= 0`
- `total_tokens == prompt_tokens + completion_tokens`
- `model` must be non-empty string
- `cost >= 0.0`

**Relationships**:
- Many UsageRecords belong to one SessionUsageTracker

### SessionUsageTracker

Aggregates usage data for the entire CLI session.

**Attributes**:
- `usage_records` (list[UsageRecord]): List of all API call usage records
- `total_prompt_tokens` (int): Sum of all prompt_tokens
- `total_completion_tokens` (int): Sum of all completion_tokens
- `total_tokens` (int): Sum of all total_tokens
- `total_cost` (float): Sum of all costs in dollars
- `api_call_count` (int): Number of successful API calls
- `models_used` (set[str]): Set of unique model names used
- `has_mock_mode` (bool): Whether mock mode was used (no real API calls)

**Methods**:
- `record_usage(prompt_tokens, completion_tokens, total_tokens, model, cost)`: Add a usage record
- `get_summary()`: Return aggregated summary data
- `reset()`: Clear all tracking data (for testing)

**Validation Rules**:
- All totals must be >= 0
- `api_call_count == len(usage_records)`
- `total_tokens == total_prompt_tokens + total_completion_tokens`
- `total_cost` should match sum of individual record costs (within floating point precision)

**State Transitions**:
- Initialized: Empty state, all counters at 0
- Active: Records being added as API calls are made
- Final: Summary displayed on exit

### ModelPricing

Pricing information for OpenAI models.

**Attributes**:
- `model_name` (str): Model identifier (e.g., "gpt-4", "gpt-3.5-turbo")
- `input_cost_per_1k` (float): Cost per 1,000 input tokens in dollars
- `output_cost_per_1k` (float): Cost per 1,000 output tokens in dollars

**Storage**:
- Hardcoded dictionary in `usage_tracker.py`
- Format: `{model_name: {"input": cost, "output": cost}}`

**Validation Rules**:
- `input_cost_per_1k >= 0.0`
- `output_cost_per_1k >= 0.0`
- Model name must be non-empty string

**Relationships**:
- Many UsageRecords reference one ModelPricing entry (by model name)

## Data Flow

### Recording Usage

1. API call made in `brain_core/chat.py`
2. Response received with `response.usage` object
3. Extract `prompt_tokens`, `completion_tokens`, `total_tokens`, `model`
4. Look up model pricing
5. Calculate cost: `(input_cost * prompt_tokens / 1000) + (output_cost * completion_tokens / 1000)`
6. Create UsageRecord
7. Add to SessionUsageTracker
8. Update aggregated totals

### Displaying Summary

1. User types `/exit` or program terminates
2. Call `SessionUsageTracker.get_summary()`
3. Format summary with:
   - Total tokens (prompt + completion + total)
   - Total cost
   - API call count
   - Models used
   - Mock mode indicator (if applicable)
4. Display formatted summary to user

## Edge Cases

### No API Calls
- `api_call_count == 0`
- All totals are 0
- Display: "No API calls made during this session"

### Mock Mode Only
- `has_mock_mode == True`
- `api_call_count == 0`
- Display: "Mock mode used - no API calls made"

### Failed API Calls
- Not recorded in tracker
- `api_call_count` only includes successful calls
- No impact on totals

### Missing Usage Data
- If `response.usage` is missing (shouldn't happen with OpenAI SDK)
- Skip recording, log warning
- Don't increment `api_call_count`

### Unknown Model
- Model not in pricing dictionary
- Options:
  1. Use fallback pricing (0.0 or default)
  2. Display warning in summary
  3. Skip cost calculation, show tokens only

### Very Large Token Counts
- Format numbers with commas (e.g., "1,234,567 tokens")
- Use appropriate precision for costs (e.g., "$123.45" not "$123.456789")

## No Database Changes

All tracking is in-memory only:
- No new database tables
- No schema migrations
- No persistence across sessions
- Session data is lost on program exit (by design)

