# brain_core/config.py
import logging
import os
from dotenv import load_dotenv
from openai import OpenAI

logger = logging.getLogger(__name__)

# Load .env.local first (development), then .env (production/default)
# .env.local takes precedence if it exists
if os.path.exists(".env.local"):
    load_dotenv(".env.local")
load_dotenv()

# Environment mode: "development" or "production"
# Validate and normalize the mode value
def _normalize_env_mode(raw_value: str) -> str:
    """Normalize and validate environment mode value."""
    normalized = raw_value.lower()
    if normalized in ("development", "dev"):
        return "development"
    elif normalized in ("production", "prod"):
        return "production"
    else:
        # Invalid mode - default to production with error message
        logger.error(
            f"Invalid ENV_MODE value: '{raw_value}'. "
            "Must be 'development' or 'production'. Defaulting to 'production'."
        )
        return "production"


_raw_env_mode = os.getenv("ENV_MODE", "production")
ENV_MODE = _normalize_env_mode(_raw_env_mode)

# Mock mode: automatically enabled in development mode
# In production, always use real OpenAI SDK
MOCK_MODE = ENV_MODE == "development"

# Database configuration
# In development mode, use separate dev database
if ENV_MODE == "development":
    DB_CONFIG = {
        "host": os.getenv("DEV_DB_HOST", os.getenv("DB_HOST", "127.0.0.1")),
        "port": int(os.getenv("DEV_DB_PORT", os.getenv("DB_PORT", "5432"))),
        "dbname": os.getenv("DEV_DB_NAME", "ongoing_projects_dev"),
        "user": os.getenv("DEV_DB_USER", os.getenv("DB_USER", "thn_user")),
        "password": os.getenv("DEV_DB_PASSWORD", os.getenv("DB_PASSWORD", "")),
    }
else:
    DB_CONFIG = {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "dbname": os.getenv("DB_NAME", "ongoing_projects"),
        "user": os.getenv("DB_USER", "thn_user"),
        "password": os.getenv("DB_PASSWORD", ""),
    }

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")

# Ollama configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
# Default Ollama model for conversation organization
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:8b")
# Current version of the conversation indexer prompt/schema
CONVERSATION_INDEX_VERSION = int(os.getenv("CONVERSATION_INDEX_VERSION", "1"))
# Timeout for Ollama API calls (indexing operations may take longer)
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "300"))  # 5 minutes default for indexing

# DAAS semantic retrieval configuration
# Number of top-k most relevant dreams to retrieve for pattern-based queries
DAAS_VECTOR_TOP_K = int(os.getenv("DAAS_VECTOR_TOP_K", "5"))

# Log configuration on startup
logger.info(f"Environment mode: {ENV_MODE}")
logger.info(f"Mock mode: {MOCK_MODE}")
logger.info(f"Database: {DB_CONFIG['dbname']} @ {DB_CONFIG['host']}:{DB_CONFIG['port']}")
if not MOCK_MODE:
    logger.info(f"OpenAI model: {OPENAI_MODEL}")
else:
    logger.info("Using mock OpenAI client (no API calls)")
logger.info(f"Ollama endpoint: {OLLAMA_BASE_URL} (model: {OLLAMA_MODEL})")

# Initialize client based on mode
if MOCK_MODE:
    from .mock_client import MockOpenAIClient
    client = MockOpenAIClient()
else:
    client = OpenAI()


def validate_database_connection() -> bool:
    """
    Validate that the database connection is available.
    Returns True if connection succeeds, False otherwise.
    """
    try:
        import psycopg2
        test_conn = psycopg2.connect(**DB_CONFIG)
        test_conn.close()
        return True
    except Exception as e:
        logger.error(f"Database connection validation failed: {e}")
        return False


# Validate database connection on startup
# In production, fail fast. In development, warn but allow startup
# (developer might be setting up the database)
if not validate_database_connection():
    error_msg = (
        f"Failed to connect to database '{DB_CONFIG['dbname']}' "
        f"at {DB_CONFIG['host']}:{DB_CONFIG['port']}. "
        "Please check your database configuration and ensure the database is running."
    )
    if ENV_MODE == "production":
        logger.error(error_msg)
        raise ConnectionError(error_msg)
    else:
        logger.warning(
            error_msg + " Continuing in development mode. "
            "Run 'python setup_dev.py' to initialize the development database."
        )
