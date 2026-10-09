from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class ChatSession:
    """
    Represents one chatbot conversation/session.
    """

    conversation_id: UUID
    login_id: int
    property_id: int

    screen_module: Optional[str] = None
    selected_module: Optional[str] = None
    active_module: Optional[str] = None

    conversation_summary: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_message_at: Optional[datetime] = None

    is_active: bool = True


@dataclass
class ChatMessage:
    """
    Represents one message inside a chatbot conversation.
    """

    id: Optional[int]

    conversation_id: UUID
    login_id: int
    property_id: int

    role: str
    message: str

    module: Optional[str] = None
    created_at: Optional[datetime] = None