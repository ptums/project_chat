# brain_core/memory.py

from .db import get_conn


# ------------------------------------------------------------
# Fetch stable, high-level project knowledge entries
# ------------------------------------------------------------
def fetch_project_knowledge(project: str) -> list[str]:
    if not project:
        return []

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT summary
                    FROM project_knowledge
                    WHERE project = %s
                    ORDER BY key
                    """,
                    (project,),
                )
                rows = cur.fetchall()
    except Exception:
        return []

    return [r[0] for r in rows]


# ------------------------------------------------------------
# Build project context: knowledge + recent snippets
# ------------------------------------------------------------
def get_project_context(
    project: str,
    current_conversation_id,
    limit_messages: int = 80,
) -> str:
    if not project or project == "general":
        return ""

    # Project knowledge
    knowledge_summaries = fetch_project_knowledge(project)
    knowledge_section = ""
    if knowledge_summaries:
        bullet_list = "\n".join(f"- {k}" for k in knowledge_summaries)
        knowledge_section = (
            f"Here is stable, high-level knowledge about the project '{project}':\n"
            f"{bullet_list}\n"
        )

    # Recent snippets from other conversations in the same project
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT m.role, m.content
                    FROM messages m
                    JOIN conversations c ON m.conversation_id = c.id
                    WHERE c.project = %s
                      AND m.conversation_id <> %s
                    ORDER BY m.created_at DESC
                    LIMIT %s
                    """,
                    (project, str(current_conversation_id), limit_messages),
                )
                rows = cur.fetchall()
    except Exception:
        rows = []

    # Format snippet lines
    snippet_lines = []
    for role, content in reversed(rows):
        short = (content or "").strip()
        if len(short) > 300:
            short = short[:300] + "..."
        snippet_lines.append(f"- ({role}) {short}")

    # Build snippet section
    snippets_section = ""
    if snippet_lines:
        joined = "\n".join(snippet_lines)
        snippets_section = (
            f"Here are some recent snippets from other sessions in the '{project}' project:\n"
            f"{joined}\n"
        )

    # Final combined context
    if not knowledge_section and not snippets_section:
        return ""

    return (
        f"You are continuing a conversation in project '{project}'.\n\n"
        f"{knowledge_section}"
        f"{snippets_section}"
        f"Use this only as background; the user's current message is primary."
    )


# ------------------------------------------------------------
# Text-only search (fallback until embeddings are added)
# ------------------------------------------------------------
def semantic_search_snippets(project: str, query: str, limit: int = 10):
    """
    Simple text search using ILIKE.
    No embeddings or semantic vectors.
    """
    query = query.strip()
    if not query:
        return []

    like_query = f"%{query}%"

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                if project == "general":
                    cur.execute(
                        """
                        SELECT c.project, m.content
                        FROM messages m
                        JOIN conversations c ON m.conversation_id = c.id
                        WHERE m.content ILIKE %s
                        ORDER BY m.created_at DESC
                        LIMIT %s
                        """,
                        (like_query, limit),
                    )
                else:
                    cur.execute(
                        """
                        SELECT c.project, m.content
                        FROM messages m
                        JOIN conversations c ON m.conversation_id = c.id
                        WHERE c.project = %s
                          AND m.content ILIKE %s
                        ORDER BY m.created_at DESC
                        LIMIT %s
                        """,
                        (project, like_query, limit),
                    )

                rows = cur.fetchall()
    except Exception:
        return []

    results = []
    for proj, content in rows:
        short = (content or "").strip()
        if len(short) > 240:
            short = short[:240] + "..."
        results.append((proj, short))

    return results
