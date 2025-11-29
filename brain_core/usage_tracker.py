# brain_core/usage_tracker.py
"""
Usage tracking for OpenAI API calls during CLI session.
Tracks token usage and calculates costs based on model pricing.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class UsageRecord:
    """Represents a single API call's usage data."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str
    cost: float

    def __post_init__(self):
        """Validate usage record data."""
        if self.prompt_tokens < 0:
            raise ValueError("prompt_tokens must be >= 0")
        if self.completion_tokens < 0:
            raise ValueError("completion_tokens must be >= 0")
        if self.total_tokens != self.prompt_tokens + self.completion_tokens:
            raise ValueError(
                f"total_tokens ({self.total_tokens}) must equal "
                f"prompt_tokens ({self.prompt_tokens}) + "
                f"completion_tokens ({self.completion_tokens})"
            )
        if not self.model:
            raise ValueError("model must be non-empty string")
        if self.cost < 0.0:
            raise ValueError("cost must be >= 0.0")


# Model pricing per 1K tokens (as of 2024-2025)
# Prices in USD, per 1,000 tokens
# Source: https://openai.com/pricing
MODEL_PRICING: dict[str, dict[str, float]] = {
    "gpt-4": {
        "input": 0.03,   # $0.03 per 1K input tokens
        "output": 0.06,  # $0.06 per 1K output tokens
    },
    "gpt-4-turbo": {
        "input": 0.01,   # $0.01 per 1K input tokens
        "output": 0.03,  # $0.03 per 1K output tokens
    },
    "gpt-4-1106-preview": {
        "input": 0.01,
        "output": 0.03,
    },
    "gpt-4-0125-preview": {
        "input": 0.01,
        "output": 0.03,
    },
    "gpt-3.5-turbo": {
        "input": 0.0005,  # $0.0005 per 1K input tokens
        "output": 0.0015, # $0.0015 per 1K output tokens
    },
    "gpt-3.5-turbo-1106": {
        "input": 0.001,
        "output": 0.002,
    },
    "gpt-3.5-turbo-0125": {
        "input": 0.0005,
        "output": 0.0015,
    },
    # Add more models as needed
}


def get_model_pricing(model: str) -> Optional[dict[str, float]]:
    """
    Get pricing information for a model.
    
    Args:
        model: Model name (e.g., "gpt-4", "gpt-3.5-turbo")
        
    Returns:
        Dictionary with "input" and "output" costs per 1K tokens, or None if model not found
    """
    return MODEL_PRICING.get(model)


def calculate_cost(
    prompt_tokens: int,
    completion_tokens: int,
    model: str,
) -> float:
    """
    Calculate cost for an API call based on token usage and model pricing.
    
    Args:
        prompt_tokens: Number of input tokens
        completion_tokens: Number of output tokens
        model: Model name
        
    Returns:
        Cost in dollars (0.0 if model pricing not found)
    """
    pricing = get_model_pricing(model)
    if not pricing:
        # Unknown model - return 0.0 (will be handled in display)
        # This handles edge case where model pricing is not available
        return 0.0
    
    input_cost = (pricing["input"] * prompt_tokens) / 1000.0
    output_cost = (pricing["output"] * completion_tokens) / 1000.0
    
    return input_cost + output_cost


class SessionUsageTracker:
    """Tracks usage data for the entire CLI session."""
    
    def __init__(self):
        """Initialize empty session tracker."""
        self.usage_records: list[UsageRecord] = []
        self.total_prompt_tokens: int = 0
        self.total_completion_tokens: int = 0
        self.total_tokens: int = 0
        self.total_cost: float = 0.0
        self.api_call_count: int = 0
        self.models_used: set[str] = set()
        self.has_mock_mode: bool = False
    
    def record_usage(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        model: str,
        cost: float,
    ) -> None:
        """
        Record usage from a single API call.
        
        Args:
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            total_tokens: Total tokens (should equal prompt + completion)
            model: Model name used
            cost: Calculated cost for this call
        """
        record = UsageRecord(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            model=model,
            cost=cost,
        )
        
        self.usage_records.append(record)
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        self.total_tokens += total_tokens
        self.total_cost += cost
        self.api_call_count += 1
        self.models_used.add(model)
    
    def get_summary(self) -> dict:
        """
        Get aggregated summary of session usage.
        
        Returns:
            Dictionary with summary data:
            - total_prompt_tokens
            - total_completion_tokens
            - total_tokens
            - total_cost
            - api_call_count
            - models_used (list of model names)
            - has_mock_mode
        """
        return {
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "api_call_count": self.api_call_count,
            "models_used": sorted(list(self.models_used)),
            "has_mock_mode": self.has_mock_mode,
        }
    
    def reset(self) -> None:
        """Clear all tracking data (for testing)."""
        self.usage_records.clear()
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.api_call_count = 0
        self.models_used.clear()
        self.has_mock_mode = False


# Global session tracker instance
# Initialized at CLI startup, used throughout session
_session_tracker: Optional[SessionUsageTracker] = None


def get_session_tracker() -> SessionUsageTracker:
    """
    Get the global session tracker instance.
    Creates a new instance if one doesn't exist.
    
    Returns:
        SessionUsageTracker instance
    """
    global _session_tracker
    if _session_tracker is None:
        _session_tracker = SessionUsageTracker()
    return _session_tracker


def reset_session_tracker() -> None:
    """Reset the global session tracker (for testing)."""
    global _session_tracker
    if _session_tracker is not None:
        _session_tracker.reset()
    else:
        _session_tracker = SessionUsageTracker()

