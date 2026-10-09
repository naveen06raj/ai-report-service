from typing import Any, Dict, List, Optional, TypedDict


class ReportState(
    TypedDict,
    total=False
):

    # ============================================================
    # Common Login / Authentication
    # ============================================================

    login_id: int
    authorization: str

    # ============================================================
    # Financial
    # ============================================================

    invoice_id: int

    # ============================================================
    # Property / Reporting Period
    # ============================================================

    property_id: int
    period: str

    # ============================================================
    # Conversation
    # ============================================================

    conversation_id: str

    conversation_history: List[Dict[str, Any]]

    conversation_summary: Optional[str]

    # ============================================================
    # User Question
    # ============================================================

    # Original question exactly as entered by the user.
    original_question: str

    # Context-aware question generated from the current question
    # and previous conversation history.
    rewritten_question: Optional[str]

    # Existing agents continue reading this field.
    # It will contain rewritten_question when available,
    # otherwise the original question.
    question: str

    # ============================================================
    # Chatbot Context
    # ============================================================

    # Screen from which chatbot was opened.
    screen_module: Optional[str]

    # Module explicitly selected through chatbot buttons.
    selected_module: Optional[str]

    # Module detected by router for the current question.
    detected_module: Optional[str]

    # Module currently active in the conversation.
    active_module: Optional[str]

    # ============================================================
    # Router Information
    # ============================================================

    routing_confidence: Optional[float]

    routing_reason: Optional[str]

    # ============================================================
    # Backward Compatibility
    # ============================================================

    current_module: Optional[str]

    # ============================================================
    # Final Answer
    # ============================================================

    answer: str