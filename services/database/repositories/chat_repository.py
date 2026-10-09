import logging
from typing import List, Optional
from uuid import UUID, uuid4

from services.database.database import get_database_connection
from services.database.models import ChatMessage, ChatSession


logger = logging.getLogger(__name__)


class ChatRepository:
    """
    Repository responsible for chatbot conversation persistence.

    Handles:
        - Creating conversations
        - Fetching conversations
        - Saving user/assistant messages
        - Fetching recent conversation history
        - Updating active module/context
    """

    # ============================================================
    # CHAT SESSION
    # ============================================================

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
        """
        Create a new chatbot conversation session.

        A conversation belongs to:
            login_id + property_id + conversation_id
        """

        if conversation_id is None:
            conversation_id = uuid4()

        connection = None

        try:
            connection = get_database_connection()

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO chat_sessions (
                        conversation_id,
                        login_id,
                        property_id,
                        screen_module,
                        selected_module,
                        active_module,
                        conversation_summary,
                        is_active
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        TRUE
                    )
                    ON CONFLICT (conversation_id)
                    DO NOTHING
                    RETURNING
                        conversation_id,
                        login_id,
                        property_id,
                        screen_module,
                        selected_module,
                        active_module,
                        conversation_summary,
                        created_at,
                        updated_at,
                        last_message_at,
                        is_active
                    """,
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

                row = cursor.fetchone()

                # If conversation already existed, fetch it.
                if row is None:
                    cursor.execute(
                        """
                        SELECT
                            conversation_id,
                            login_id,
                            property_id,
                            screen_module,
                            selected_module,
                            active_module,
                            conversation_summary,
                            created_at,
                            updated_at,
                            last_message_at,
                            is_active
                        FROM chat_sessions
                        WHERE conversation_id = %s
                          AND login_id = %s
                          AND property_id = %s
                        """,
                        (
                            conversation_id,
                            login_id,
                            property_id,
                        ),
                    )

                    row = cursor.fetchone()

                    if row is None:
                        raise RuntimeError(
                            "Conversation could not be created or retrieved."
                        )

            connection.commit()

            return ChatSession(
                conversation_id=row[0],
                login_id=row[1],
                property_id=row[2],
                screen_module=row[3],
                selected_module=row[4],
                active_module=row[5],
                conversation_summary=row[6],
                created_at=row[7],
                updated_at=row[8],
                last_message_at=row[9],
                is_active=row[10],
            )

        except Exception:
            if connection:
                connection.rollback()

            logger.exception(
                "Failed to create chat session. "
                "conversation_id=%s login_id=%s property_id=%s",
                conversation_id,
                login_id,
                property_id,
            )

            raise

        finally:
            if connection:
                connection.close()

    # ============================================================
    # GET CHAT SESSION
    # ============================================================

    @staticmethod
    def get_session(
        conversation_id: UUID,
        login_id: int,
        property_id: int,
    ) -> Optional[ChatSession]:
        """
        Retrieve a conversation only when it belongs to the
        specified login_id and property_id.

        This prevents one user/property from accessing another
        conversation.
        """

        connection = None

        try:
            connection = get_database_connection()

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        conversation_id,
                        login_id,
                        property_id,
                        screen_module,
                        selected_module,
                        active_module,
                        conversation_summary,
                        created_at,
                        updated_at,
                        last_message_at,
                        is_active
                    FROM chat_sessions
                    WHERE conversation_id = %s
                      AND login_id = %s
                      AND property_id = %s
                    LIMIT 1
                    """,
                    (
                        conversation_id,
                        login_id,
                        property_id,
                    ),
                )

                row = cursor.fetchone()

            if not row:
                return None

            return ChatSession(
                conversation_id=row[0],
                login_id=row[1],
                property_id=row[2],
                screen_module=row[3],
                selected_module=row[4],
                active_module=row[5],
                conversation_summary=row[6],
                created_at=row[7],
                updated_at=row[8],
                last_message_at=row[9],
                is_active=row[10],
            )

        except Exception:
            logger.exception(
                "Failed to retrieve chat session. "
                "conversation_id=%s login_id=%s property_id=%s",
                conversation_id,
                login_id,
                property_id,
            )

            raise

        finally:
            if connection:
                connection.close()

    # ============================================================
    # GET OR CREATE SESSION
    # ============================================================

    @staticmethod
    def get_or_create_session(
        login_id: int,
        property_id: int,
        conversation_id: Optional[UUID] = None,
        screen_module: Optional[str] = None,
        selected_module: Optional[str] = None,
        active_module: Optional[str] = None,
    ) -> ChatSession:
        """
        Return an existing conversation when conversation_id is
        supplied and belongs to the user/property.

        Otherwise create a new conversation.
        """

        # --------------------------------------------------------
        # Existing conversation requested
        # --------------------------------------------------------

        if conversation_id is not None:
            existing_session = ChatRepository.get_session(
                conversation_id=conversation_id,
                login_id=login_id,
                property_id=property_id,
            )

            if existing_session:
                return existing_session

            # A conversation_id was supplied but does not belong
            # to this login/property.
            raise ValueError(
                "Conversation not found for the specified user and property."
            )

        # --------------------------------------------------------
        # Create new conversation
        # --------------------------------------------------------

        return ChatRepository.create_session(
            login_id=login_id,
            property_id=property_id,
            conversation_id=uuid4(),
            screen_module=screen_module,
            selected_module=selected_module,
            active_module=active_module,
        )

    # ============================================================
    # SAVE MESSAGE
    # ============================================================

    @staticmethod
    def save_message(
        conversation_id: UUID,
        login_id: int,
        property_id: int,
        role: str,
        message: str,
        module: Optional[str] = None,
    ) -> ChatMessage:
        """
        Save one message in a conversation.

        role should normally be:
            user
            assistant
        """

        if role not in {"user", "assistant"}:
            raise ValueError(
                "Invalid message role. Expected 'user' or 'assistant'."
            )

        if not message or not message.strip():
            raise ValueError(
                "Message cannot be empty."
            )

        connection = None

        try:
            connection = get_database_connection()

            with connection.cursor() as cursor:

                # ------------------------------------------------
                # Verify conversation ownership
                # ------------------------------------------------

                cursor.execute(
                    """
                    SELECT 1
                    FROM chat_sessions
                    WHERE conversation_id = %s
                      AND login_id = %s
                      AND property_id = %s
                      AND is_active = TRUE
                    LIMIT 1
                    """,
                    (
                        conversation_id,
                        login_id,
                        property_id,
                    ),
                )

                session_exists = cursor.fetchone()

                if not session_exists:
                    raise ValueError(
                        "Conversation not found or inactive."
                    )

                # ------------------------------------------------
                # Insert message
                # ------------------------------------------------

                cursor.execute(
                    """
                    INSERT INTO chat_messages (
                        conversation_id,
                        login_id,
                        property_id,
                        role,
                        message,
                        module
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    RETURNING
                        id,
                        conversation_id,
                        login_id,
                        property_id,
                        role,
                        message,
                        module,
                        created_at
                    """,
                    (
                        conversation_id,
                        login_id,
                        property_id,
                        role,
                        message.strip(),
                        module,
                    ),
                )

                row = cursor.fetchone()

                # ------------------------------------------------
                # Update session timestamps
                # ------------------------------------------------

                cursor.execute(
                    """
                    UPDATE chat_sessions
                    SET
                        updated_at = CURRENT_TIMESTAMP,
                        last_message_at = CURRENT_TIMESTAMP
                    WHERE conversation_id = %s
                      AND login_id = %s
                      AND property_id = %s
                    """,
                    (
                        conversation_id,
                        login_id,
                        property_id,
                    ),
                )

            connection.commit()

            return ChatMessage(
                id=row[0],
                conversation_id=row[1],
                login_id=row[2],
                property_id=row[3],
                role=row[4],
                message=row[5],
                module=row[6],
                created_at=row[7],
            )

        except Exception:
            if connection:
                connection.rollback()

            logger.exception(
                "Failed to save chat message. "
                "conversation_id=%s login_id=%s property_id=%s role=%s",
                conversation_id,
                login_id,
                property_id,
                role,
            )

            raise

        finally:
            if connection:
                connection.close()

    # ============================================================
    # GET RECENT MESSAGES
    # ============================================================

    @staticmethod
    def get_recent_messages(
        conversation_id: UUID,
        login_id: int,
        property_id: int,
        limit: int = 20,
    ) -> List[ChatMessage]:
        """
        Get the most recent conversation messages.

        The database query retrieves the newest messages first,
        then returns them in chronological order.
        """

        if limit <= 0:
            limit = 20

        # Prevent unnecessarily large history requests.
        limit = min(limit, 100)

        connection = None

        try:
            connection = get_database_connection()

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        conversation_id,
                        login_id,
                        property_id,
                        role,
                        message,
                        module,
                        created_at
                    FROM chat_messages
                    WHERE conversation_id = %s
                      AND login_id = %s
                      AND property_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (
                        conversation_id,
                        login_id,
                        property_id,
                        limit,
                    ),
                )

                rows = cursor.fetchall()

            # Convert newest-first result into chronological order.
            rows.reverse()

            return [
                ChatMessage(
                    id=row[0],
                    conversation_id=row[1],
                    login_id=row[2],
                    property_id=row[3],
                    role=row[4],
                    message=row[5],
                    module=row[6],
                    created_at=row[7],
                )
                for row in rows
            ]

        except Exception:
            logger.exception(
                "Failed to retrieve chat history. "
                "conversation_id=%s login_id=%s property_id=%s",
                conversation_id,
                login_id,
                property_id,
            )

            raise

        finally:
            if connection:
                connection.close()

    # ============================================================
    # UPDATE SESSION CONTEXT
    # ============================================================

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
        """
        Update the current context of an existing conversation.
        """

        connection = None

        try:
            connection = get_database_connection()

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE chat_sessions
                    SET
                        screen_module = COALESCE(%s, screen_module),
                        selected_module = COALESCE(%s, selected_module),
                        active_module = COALESCE(%s, active_module),
                        conversation_summary = COALESCE(
                            %s,
                            conversation_summary
                        ),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE conversation_id = %s
                      AND login_id = %s
                      AND property_id = %s
                    RETURNING
                        conversation_id,
                        login_id,
                        property_id,
                        screen_module,
                        selected_module,
                        active_module,
                        conversation_summary,
                        created_at,
                        updated_at,
                        last_message_at,
                        is_active
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

                row = cursor.fetchone()

            connection.commit()

            if not row:
                return None

            return ChatSession(
                conversation_id=row[0],
                login_id=row[1],
                property_id=row[2],
                screen_module=row[3],
                selected_module=row[4],
                active_module=row[5],
                conversation_summary=row[6],
                created_at=row[7],
                updated_at=row[8],
                last_message_at=row[9],
                is_active=row[10],
            )

        except Exception:
            if connection:
                connection.rollback()

            logger.exception(
                "Failed to update chat session context. "
                "conversation_id=%s login_id=%s property_id=%s",
                conversation_id,
                login_id,
                property_id,
            )

            raise

        finally:
            if connection:
                connection.close()

    # ============================================================
    # CLOSE SESSION
    # ============================================================

    @staticmethod
    def close_session(
        conversation_id: UUID,
        login_id: int,
        property_id: int,
    ) -> bool:
        """
        Mark a conversation as inactive.
        """

        connection = None

        try:
            connection = get_database_connection()

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE chat_sessions
                    SET
                        is_active = FALSE,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE conversation_id = %s
                      AND login_id = %s
                      AND property_id = %s
                    RETURNING conversation_id
                    """,
                    (
                        conversation_id,
                        login_id,
                        property_id,
                    ),
                )

                row = cursor.fetchone()

            connection.commit()

            return row is not None

        except Exception:
            if connection:
                connection.rollback()

            logger.exception(
                "Failed to close chat session. "
                "conversation_id=%s login_id=%s property_id=%s",
                conversation_id,
                login_id,
                property_id,
            )

            raise

        finally:
            if connection:
                connection.close()

    # ============================================================
    # CONVERT HISTORY FOR LLM
    # ============================================================

    @staticmethod
    def get_history_for_llm(
        conversation_id: UUID,
        login_id: int,
        property_id: int,
        limit: int = 20,
    ) -> List[dict]:
        """
        Return recent messages in a simple structure suitable
        for Gemini/LangChain/LangGraph context.
        """

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