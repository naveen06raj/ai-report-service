from typing import Optional, TypedDict


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
    # User Question
    # ============================================================

    question: str

    # ============================================================
    # Chatbot Context
    #
    # screen_module:
    #   The screen from which the chatbot was opened.
    #
    #   Examples:
    #       feedback
    #       facilities
    #       visitor
    #       financial
    #       key_collection
    #       defect
    #       None / main / dashboard
    #
    # selected_module:
    #   The module explicitly selected by the user
    #   through a chatbot button.
    #
    # detected_module:
    #   The module detected by the Agentic Router
    #   from the user's actual question.
    # ============================================================

    screen_module: Optional[str]

    selected_module: Optional[str]

    detected_module: Optional[str]

    # ============================================================
    # Router Information
    # ============================================================

    routing_confidence: Optional[float]

    routing_reason: Optional[str]

    # ============================================================
    # Backward Compatibility
    #
    # Some existing agents may still read current_module.
    # Keep this temporarily so existing module agents do not break.
    #
    # This should NOT be used for chatbot routing.
    # ============================================================

    current_module: Optional[str]

    # ============================================================
    # Final Answer
    # ============================================================

    answer: str