
import logging
from typing import List, Optional
from uuid import UUID, uuid4

from services.database.database import (
    get_database_connection,
    get_database_mode,
)
from services.database.models import ChatMessage, ChatSession

logger = logging.getLogger(__name__)

# Dedicated table names for the AI Report Service.
SESSION_TABLE = "report_chat_sessions"
MESSAGE_TABLE = "report_chat_messages"

SESSION_COLUMNS = (
    "conversation_id, login_id, property_id, screen_module, "
    "selected_module, active_module, conversation_summary, "
    "created_at, updated_at, last_message_at, is_active"
)

MESSAGE_COLUMNS = (
    "id, conversation_id, login_id, property_id, role, "
    "message, module, created_at"
)


def _session(row) -> Optional[ChatSession]:
    """Convert a database row into a ChatSession model."""
    if row is None:
        return None

    values = list(row)

    # CompatibleCursor normally converts this to UUID already.
    if not isinstance(values[0], UUID):
        values[0] = UUID(str(values[0]))

    # MySQL and SQLite may return is_active as an integer.
    values[10] = bool(values[10])

    return ChatSession(*values)


def _message(row) -> Optional[ChatMessage]:
    """Convert a database row into a ChatMessage model."""
    if row is None:
        return None

    values = list(row)

    # CompatibleCursor normally converts this to UUID already.
    if not isinstance(values[1], UUID):
        values[1] = UUID(str(values[1]))

    return ChatMessage(*values)


class ChatRepository:
    """Database operations for chatbot sessions and messages."""

    @staticmethod
    def create_session(
        login_id: int,
        property_id: int,
        conversation_id: Optional[UUID] = None,
        screen_module: Optional[str] = None,
        selected_module: Optional[str] = None,
        active_module: Optional[str] = None,
        conversation_summary: Optional[str] = None,
    ) -> ChatSession:
        conversation_id = conversation_id or uuid4()
        mode = get_database_mode()
        conn = get_database_connection()

        try:
            with conn.cursor() as cur:
                if mode == "mysql":
                    insert_prefix = "INSERT IGNORE INTO"
                elif mode == "sqlite":
                    insert_prefix = "INSERT OR IGNORE INTO"
                else:
                    insert_prefix = "INSERT INTO"

                sql = f"""
                    {insert_prefix} {SESSION_TABLE}
                    (
                        conversation_id,
                        login_id,
                        property_id,
                        screen_module,
                        selected_module,
                        active_module,
                        conversation_summary,
                        is_active
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)
                """

                if mode in {"postgres", "postgresql"}:
                    sql += """
                        ON CONFLICT (conversation_id) DO NOTHING
                    """

                cur.execute(
                    sql,
                    (
                        conversation_id,
                        login_id,
                        property_id,
                        screen_module,
                        selected_module,
                        active_module,
                        conversation_summary,
                    ),
                )

                cur.execute(
                    f"""
                    SELECT {SESSION_COLUMNS}
                    FROM {SESSION_TABLE}
                    WHERE conversation_id = %s
                      AND login_id = %s
                      AND property_id = %s
                    """,
                    (conversation_id, login_id, property_id),
                )
                row = cur.fetchone()

                if row is None:
                    raise ValueError(
                        "Conversation ID already exists or the conversation "
                        "does not belong to this user and property."
                    )

            conn.commit()
            return _session(row)

        except Exception:
            conn.rollback()
            logger.exception("Failed to create chat session")
            raise
        finally:
            conn.close()

    @staticmethod
    def get_session(
        conversation_id: UUID,
        login_id: int,
        property_id: int,
    ) -> Optional[ChatSession]:
        conn = get_database_connection()

        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT {SESSION_COLUMNS}
                    FROM {SESSION_TABLE}
                    WHERE conversation_id = %s
                      AND login_id = %s
                      AND property_id = %s
                    LIMIT 1
                    """,
                    (conversation_id, login_id, property_id),
                )
                return _session(cur.fetchone())
        finally:
            conn.close()

    @staticmethod
    def get_or_create_session(
        login_id: int,
        property_id: int,
        conversation_id: Optional[UUID] = None,
        screen_module: Optional[str] = None,
        selected_module: Optional[str] = None,
        active_module: Optional[str] = None,
    ) -> ChatSession:
        if conversation_id is not None:
            session = ChatRepository.get_session(
                conversation_id,
                login_id,
                property_id,
            )

            if session is None:
                raise ValueError(
                    "Conversation not found for the specified user and property."
                )

            return session

        return ChatRepository.create_session(
            login_id=login_id,
            property_id=property_id,
            conversation_id=uuid4(),
            screen_module=screen_module,
            selected_module=selected_module,
            active_module=active_module,
        )

    @staticmethod
    def save_message(
        conversation_id: UUID,
        login_id: int,
        property_id: int,
        role: str,
        message: str,
        module: Optional[str] = None,
    ) -> ChatMessage:
        if role not in {"user", "assistant"}:
            raise ValueError(
                "Invalid message role. Expected 'user' or 'assistant'."
            )

        if not message or not message.strip():
            raise ValueError("Message cannot be empty.")

        mode = get_database_mode()
        conn = get_database_connection()

        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT 1
                    FROM {SESSION_TABLE}
                    WHERE conversation_id = %s
                      AND login_id = %s
                      AND property_id = %s
                      AND is_active = TRUE
                    LIMIT 1
                    """,
                    (conversation_id, login_id, property_id),
                )

                if cur.fetchone() is None:
                    raise ValueError("Conversation not found or inactive.")

                insert_sql = f"""
                    INSERT INTO {MESSAGE_TABLE}
                    (
                        conversation_id,
                        login_id,
                        property_id,
                        role,
                        message,
                        module
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                """

                if mode in {"postgres", "postgresql"}:
                    cur.execute(
                        insert_sql + " RETURNING id",
                        (
                            conversation_id,
                            login_id,
                            property_id,
                            role,
                            message.strip(),
                            module,
                        ),
                    )
                    inserted_id = cur.fetchone()[0]
                else:
                    cur.execute(
                        insert_sql,
                        (
                            conversation_id,
                            login_id,
                            property_id,
                            role,
                            message.strip(),
                            module,
                        ),
                    )
                    inserted_id = cur.lastrowid

                cur.execute(
                    f"""
                    UPDATE {SESSION_TABLE}
                    SET updated_at = CURRENT_TIMESTAMP,
                        last_message_at = CURRENT_TIMESTAMP
                    WHERE conversation_id = %s
                      AND login_id = %s
                      AND property_id = %s
                    """,
                    (conversation_id, login_id, property_id),
                )

                cur.execute(
                    f"""
                    SELECT {MESSAGE_COLUMNS}
                    FROM {MESSAGE_TABLE}
                    WHERE id = %s
                    """,
                    (inserted_id,),
                )
                row = cur.fetchone()

                if row is None:
                    raise RuntimeError("Message was inserted but could not be retrieved.")

            conn.commit()
            return _message(row)

        except Exception:
            conn.rollback()
            logger.exception("Failed to save chat message")
            raise
        finally:
            conn.close()

    @staticmethod
    def get_recent_messages(
        conversation_id: UUID,
        login_id: int,
        property_id: int,
        limit: int = 20,
    ) -> List[ChatMessage]:
        limit = min(max(int(limit), 1), 100)
        conn = get_database_connection()

        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT {MESSAGE_COLUMNS}
                    FROM {MESSAGE_TABLE}
                    WHERE conversation_id = %s
                      AND login_id = %s
                      AND property_id = %s
                    ORDER BY created_at DESC, id DESC
                    LIMIT %s
                    """,
                    (conversation_id, login_id, property_id, limit),
                )
                rows = cur.fetchall()

            # Return messages in chronological order for the LLM.
            return [_message(row) for row in reversed(rows)]

        finally:
            conn.close()

    @staticmethod
    def update_session_context(
        conversation_id: UUID,
        login_id: int,
        property_id: int,
        screen_module: Optional[str] = None,
        selected_module: Optional[str] = None,
        active_module: Optional[str] = None,
        conversation_summary: Optional[str] = None,
    ) -> Optional[ChatSession]:
        conn = get_database_connection()

        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE {SESSION_TABLE}
                    SET screen_module = COALESCE(%s, screen_module),
                        selected_module = COALESCE(%s, selected_module),
                        active_module = COALESCE(%s, active_module),
                        conversation_summary = COALESCE(
                            %s, conversation_summary
                        ),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE conversation_id = %s
                      AND login_id = %s
                      AND property_id = %s
                    """,
                    (
                        screen_module,
                        selected_module,
                        active_module,
                        conversation_summary,
                        conversation_id,
                        login_id,
                        property_id,
                    ),
                )

                cur.execute(
                    f"""
                    SELECT {SESSION_COLUMNS}
                    FROM {SESSION_TABLE}
                    WHERE conversation_id = %s
                      AND login_id = %s
                      AND property_id = %s
                    """,
                    (conversation_id, login_id, property_id),
                )
                row = cur.fetchone()

            conn.commit()
            return _session(row)

        except Exception:
            conn.rollback()
            logger.exception("Failed to update chat session context")
            raise
        finally:
            conn.close()

    @staticmethod
    def close_session(
        conversation_id: UUID,
        login_id: int,
        property_id: int,
    ) -> bool:
        conn = get_database_connection()

        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE {SESSION_TABLE}
                    SET is_active = FALSE,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE conversation_id = %s
                      AND login_id = %s
                      AND property_id = %s
                      AND is_active = TRUE
                    """,
                    (conversation_id, login_id, property_id),
                )
                changed = cur.rowcount > 0

            conn.commit()
            return changed

        except Exception:
            conn.rollback()
            logger.exception("Failed to close chat session")
            raise
        finally:
            conn.close()

    @staticmethod
    def get_recent_sessions(
        login_id: int,
        property_id: int,
        limit: int = 5,
    ) -> List[dict]:
        """Return the latest chat sessions for a user and property."""

        limit = min(max(int(limit), 1), 5)
        conn = get_database_connection()

        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT
                        s.conversation_id,
                        s.screen_module,
                        s.selected_module,
                        s.active_module,
                        s.created_at,
                        s.updated_at,
                        s.last_message_at,
                        (
                            SELECT m.message
                            FROM {MESSAGE_TABLE} m
                            WHERE m.conversation_id = s.conversation_id
                              AND m.login_id = s.login_id
                              AND m.property_id = s.property_id
                              AND m.role = 'user'
                            ORDER BY m.created_at ASC, m.id ASC
                            LIMIT 1
                        ) AS first_question
                    FROM {SESSION_TABLE} s
                    WHERE s.login_id = %s
                      AND s.property_id = %s
                      AND s.is_active = TRUE
                    ORDER BY
                        COALESCE(
                            s.last_message_at,
                            s.updated_at,
                            s.created_at
                        ) DESC,
                        s.created_at DESC
                    LIMIT %s
                    """,
                    (login_id, property_id, limit),
                )

                rows = cur.fetchall()

            results = []

            for row in rows:
                (
                    conversation_id,
                    screen_module,
                    selected_module,
                    active_module,
                    created_at,
                    updated_at,
                    last_message_at,
                    first_question,
                ) = row

                if not isinstance(conversation_id, UUID):
                    conversation_id = UUID(str(conversation_id))

                # Use the first user question as the recent-chat title.
                title = str(first_question or "New conversation").strip()
                if len(title) > 60:
                    title = title[:57] + "..."

                results.append(
                    {
                        "conversation_id": str(conversation_id),
                        "title": title,
                        "screen_module": screen_module,
                        "selected_module": selected_module,
                        "active_module": active_module,
                        "created_at": (
                            created_at.isoformat()
                            if created_at else None
                        ),
                        "updated_at": (
                            updated_at.isoformat()
                            if updated_at else None
                        ),
                        "last_message_at": (
                            last_message_at.isoformat()
                            if last_message_at else None
                        ),
                    }
                )

            return results

        finally:
            conn.close()

    @staticmethod
    def get_all_messages(
        conversation_id: UUID,
        login_id: int,
        property_id: int,
    ) -> List[ChatMessage]:
        """Return all messages in a conversation, oldest first."""

        conn = get_database_connection()

        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT {MESSAGE_COLUMNS}
                    FROM {MESSAGE_TABLE}
                    WHERE conversation_id = %s
                      AND login_id = %s
                      AND property_id = %s
                    ORDER BY created_at ASC, id ASC
                    """,
                    (conversation_id, login_id, property_id),
                )

                rows = cur.fetchall()

            return [_message(row) for row in rows]

        finally:
            conn.close()

    @staticmethod
    def get_history_for_llm(
        conversation_id: UUID,
        login_id: int,
        property_id: int,
        limit: int = 20,
    ) -> List[dict]:
        messages = ChatRepository.get_recent_messages(
            conversation_id=conversation_id,
            login_id=login_id,
            property_id=property_id,
            limit=limit,
        )

        return [
            {
                "role": message.role,
                "message": message.message,
                "module": message.module,
                "created_at": (
                    message.created_at.isoformat()
                    if message.created_at
                    else None
                ),
            }
            for message in messages
        ]
