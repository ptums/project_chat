# brain_core/db.py
import uuid

import psycopg2
from psycopg2.extras import Json

from .config import DB_CONFIG


def get_conn():
    return psycopg2.connect(**DB_CONFIG)


def create_conversation(title: str, project: str = "general") -> uuid.UUID:
    conv_id = uuid.uuid4()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO conversations (id, title, project)
                VALUES (%s, %s, %s)
                """,
                (str(conv_id), title, project),
            )
    return conv_id


def save_message(
    conversation_id: uuid.UUID,
    role: str,
    content: str,
    meta: dict | None = None,
) -> uuid.UUID:
    msg_id = uuid.uuid4()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO messages (id, conversation_id, role, content, meta_json)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (str(msg_id), str(conversation_id), role, content, Json(meta or {})),
            )
    return msg_id


def load_conversation_messages(conversation_id: uuid.UUID, limit: int = 50):
    """Load last N messages in chronological order for this conversation."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT role, content
                FROM messages
                WHERE conversation_id = %s
                ORDER BY created_at ASC
                LIMIT %s
                """,
                (str(conversation_id), limit),
            )
            rows = cur.fetchall()
    return [{"role": role, "content": content} for role, content in rows]
