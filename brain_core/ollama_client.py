"""
Ollama client helper for making HTTP requests to Ollama API.
Provides a simple interface for generating text completions via Ollama.
"""
import logging
import os
import requests
from typing import Optional

logger = logging.getLogger(__name__)


class OllamaError(Exception):
    """Raised when Ollama API call fails."""
    pass


def check_ollama_health(base_url: Optional[str] = None, timeout: int = 5) -> bool:
    """
    Check if Ollama is running and accessible.
    
    Args:
        base_url: Ollama base URL (defaults to OLLAMA_BASE_URL env var)
        timeout: Health check timeout in seconds (default: 5)
    
    Returns:
        True if Ollama is accessible, False otherwise
    """
    if base_url is None:
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    base_url = base_url.rstrip("/")
    health_url = f"{base_url}/api/tags"
    
    try:
        response = requests.get(health_url, timeout=timeout)
        return response.status_code == 200
    except Exception:
        return False


def generate_with_ollama(
    model: str,
    prompt: str,
    base_url: Optional[str] = None,
    timeout: int = 60,
) -> str:
    """
    Generate text completion using Ollama API.
    
    Args:
        model: Ollama model name (e.g., "llama3:8b")
        prompt: Input prompt text
        base_url: Ollama base URL (defaults to OLLAMA_BASE_URL env var or http://localhost:11434)
        timeout: Request timeout in seconds (default: 60)
    
    Returns:
        Generated text response from Ollama
    
    Raises:
        OllamaError: If the API call fails or returns invalid response
    """
    # Get base URL from parameter, env var, or default
    if base_url is None:
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Ensure base_url doesn't end with trailing slash
    base_url = base_url.rstrip("/")
    
    # Construct API endpoint
    api_url = f"{base_url}/api/generate"
    
    # Prepare request payload
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }
    
    # Attempt to use format parameter for structured JSON output
    # Note: This is experimental - Ollama may not support this yet
    # If not supported, the API will ignore it and we'll rely on prompt engineering
    # Some Ollama versions support "json" format parameter for structured output
    # This is a best-effort attempt - if it fails, we fall back to prompt-only approach
    payload["format"] = "json"
    logger.debug("Attempting to use format=json parameter (may not be supported by all Ollama versions)")
    
    try:
        logger.debug(f"Calling Ollama API: {api_url} with model={model}")
        response = requests.post(api_url, json=payload, timeout=timeout)
        response.raise_for_status()
        
        # Parse JSON response
        result = response.json()
        
        # Extract response text
        if "response" not in result:
            raise OllamaError(
                f"Invalid Ollama response: missing 'response' field. "
                f"Response: {result}"
            )
        
        return result.get("response", "")
        
    except requests.exceptions.Timeout:
        # Check if Ollama is accessible before suggesting timeout increase
        is_accessible = check_ollama_health(base_url, timeout=2)
        if not is_accessible:
            raise OllamaError(
                f"Ollama API request timed out after {timeout}s. "
                f"Ollama may not be running or accessible at {base_url}. "
                f"Verify Ollama is running: `ollama serve` or check {base_url}/api/tags"
            )
        else:
            raise OllamaError(
                f"Ollama API request timed out after {timeout}s. "
                f"The model may be loading or the conversation is very long. "
                f"Try increasing OLLAMA_TIMEOUT (current: {timeout}s) or check Ollama logs."
            )
    except requests.exceptions.ConnectionError as e:
        raise OllamaError(
            f"Failed to connect to Ollama at {base_url}. "
            f"Ensure Ollama is running and accessible. Error: {e}"
        )
    except requests.exceptions.HTTPError as e:
        raise OllamaError(
            f"Ollama API returned error: HTTP {response.status_code}. "
            f"Response: {response.text if hasattr(response, 'text') else str(e)}"
        )
    except requests.exceptions.RequestException as e:
        raise OllamaError(f"Ollama API request failed: {e}")
    except (KeyError, ValueError) as e:
        raise OllamaError(f"Failed to parse Ollama response: {e}")

