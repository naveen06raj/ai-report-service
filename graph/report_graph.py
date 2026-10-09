import logging
from typing import List, Optional

from langgraph.graph import END, StateGraph

from graph.state import ReportState

from agents.feedback_agent import feedback_node
from agents.facilities_agent import facilities_node
from agents.visitor_management_agent import visitor_management_node
from agents.financial_agent import financial_node
from agents.key_agent import key_collection_node
from agents.defect_agent import defect_node
from agents.fallback_agent import fallback_node


logger = logging.getLogger(__name__)


# ============================================================
# Supported Modules
# ============================================================

SUPPORTED_MODULES = {
    "feedback",
    "facilities",
    "visitor",
    "financial",
    "key_collection",
    "defect",
}


# ============================================================
# Module Aliases
# ============================================================

MODULE_ALIASES = {
    # --------------------------------------------------------
    # Feedback
    # --------------------------------------------------------

    "feedback": "feedback",
    "feedbacks": "feedback",
    "complaint": "feedback",
    "complaints": "feedback",
    "resident_feedback": "feedback",
    "resident feedback": "feedback",

    # --------------------------------------------------------
    # Facilities
    # --------------------------------------------------------

    "facility": "facilities",
    "facilities": "facilities",
    "facility_booking": "facilities",
    "facility_bookings": "facilities",
    "facility booking": "facilities",
    "facility bookings": "facilities",
    "booking": "facilities",
    "bookings": "facilities",

    # --------------------------------------------------------
    # Visitor
    # --------------------------------------------------------

    "visitor": "visitor",
    "visitors": "visitor",
    "visitor_management": "visitor",
    "visitor management": "visitor",
    "visitor_registration": "visitor",
    "visitor_registrations": "visitor",
    "visitor registration": "visitor",
    "visitor registrations": "visitor",
    "guest": "visitor",
    "guests": "visitor",

    # --------------------------------------------------------
    # Financial
    # --------------------------------------------------------

    "financial": "financial",
    "finance": "financial",
    "financial_report": "financial",
    "financial_reports": "financial",
    "financial report": "financial",
    "financial reports": "financial",
    "payment": "financial",
    "payments": "financial",
    "collection": "financial",
    "collections": "financial",
    "invoice": "financial",
    "invoices": "financial",
    "financial collection": "financial",
    "financial collections": "financial",
    "amount due": "financial",
    "outstanding": "financial",
    "outstanding amount": "financial",
    "balances": "financial",

    # --------------------------------------------------------
    # Key Collection
    # --------------------------------------------------------

    "key": "key_collection",
    "keys": "key_collection",
    "key_collection": "key_collection",
    "key_collections": "key_collection",
    "keycollection": "key_collection",
    "keycollections": "key_collection",
    "key collection": "key_collection",
    "key collections": "key_collection",
    "key handover": "key_collection",

    # --------------------------------------------------------
    # Defect
    # --------------------------------------------------------

    "defect": "defect",
    "defects": "defect",
    "maintenance_defect": "defect",
    "maintenance_defects": "defect",
    "maintenance defect": "defect",
    "maintenance defects": "defect",
}


# ============================================================
# Normalize Module
# ============================================================

def normalize_module(
    module: Optional[str],
) -> Optional[str]:
    """
    Convert a module name or alias to the canonical module name.

    Main / Dashboard / Home / None are treated as having
    no active business module.
    """

    if module is None:
        return None

    value = str(
        module
    ).strip().lower()

    if not value:
        return None

    if value in {
        "main",
        "dashboard",
        "home",
        "none",
        "null",
    }:
        return None

    normalized = MODULE_ALIASES.get(
        value
    )

    if normalized in SUPPORTED_MODULES:
        return normalized

    return None


# ============================================================
# Determine Active Module
# ============================================================

def get_active_module(
    state: ReportState,
) -> str:
    """
    Determine which module should be executed.

    Priority:

        1. detected_module
        2. selected_module
        3. active_module
        4. screen_module
        5. current_module
        6. fallback

    detected_module normally comes from the Agentic Router.
    active_module comes from the current conversation history.
    """

    # --------------------------------------------------------
    # 1. Current router decision
    # --------------------------------------------------------

    detected_module = normalize_module(
        state.get("detected_module")
    )

    if detected_module:
        logger.info(
            "Using detected module: %s",
            detected_module,
        )

        return detected_module

    # --------------------------------------------------------
    # 2. Explicit button selection
    # --------------------------------------------------------

    selected_module = normalize_module(
        state.get("selected_module")
    )

    if selected_module:
        logger.info(
            "Using selected module: %s",
            selected_module,
        )

        return selected_module

    # --------------------------------------------------------
    # 3. Existing conversation active module
    # --------------------------------------------------------

    active_module = normalize_module(
        state.get("active_module")
    )

    if active_module:
        logger.info(
            "Using active conversation module: %s",
            active_module,
        )

        return active_module

    # --------------------------------------------------------
    # 4. Current screen
    # --------------------------------------------------------

    screen_module = normalize_module(
        state.get("screen_module")
    )

    if screen_module:
        logger.info(
            "Using screen module: %s",
            screen_module,
        )

        return screen_module

    # --------------------------------------------------------
    # 5. Backward compatibility
    # --------------------------------------------------------

    current_module = normalize_module(
        state.get("current_module")
    )

    if current_module:
        logger.info(
            "Using legacy current_module: %s",
            current_module,
        )

        return current_module

    # --------------------------------------------------------
    # 6. Fallback
    # --------------------------------------------------------

    logger.info(
        "No valid module identified. Using fallback."
    )

    return "fallback"


# ============================================================
# Route Module
# ============================================================

def route_module(
    state: ReportState,
):
    """
    LangGraph conditional routing function.
    """

    active_module = get_active_module(
        state
    )

    logger.info(
        "Graph routing to module: %s",
        active_module,
    )

    return active_module


# ============================================================
# Start Node
# ============================================================

def start_node(
    state: ReportState,
):
    """
    Initial graph node.

    The module router is executed outside this graph.

    This graph only executes the module selected by the router
    or the available conversation/screen context.
    """

    logger.info(
        "Report graph started | "
        "conversation_id=%s | "
        "detected=%s | "
        "selected=%s | "
        "active=%s | "
        "screen=%s | "
        "history_messages=%s",
        state.get("conversation_id"),
        state.get("detected_module"),
        state.get("selected_module"),
        state.get("active_module"),
        state.get("screen_module"),
        len(
            state.get(
                "conversation_history",
                [],
            )
        ),
    )

    logger.info(
        "Original question: %s",
        state.get(
            "original_question"
        ),
    )

    logger.info(
        "Effective question: %s",
        state.get(
            "question"
        ),
    )

    return state


# ============================================================
# Graph Definition
# ============================================================

workflow = StateGraph(
    ReportState
)


# ============================================================
# Start Node
# ============================================================

workflow.add_node(
    "start",
    start_node,
)


# ============================================================
# Business Module Nodes
# ============================================================

workflow.add_node(
    "feedback",
    feedback_node,
)

workflow.add_node(
    "facilities",
    facilities_node,
)

workflow.add_node(
    "visitor",
    visitor_management_node,
)

workflow.add_node(
    "financial",
    financial_node,
)

workflow.add_node(
    "key_collection",
    key_collection_node,
)

workflow.add_node(
    "defect",
    defect_node,
)


# ============================================================
# Fallback Node
# ============================================================

workflow.add_node(
    "fallback",
    fallback_node,
)


# ============================================================
# Entry Point
# ============================================================

workflow.set_entry_point(
    "start"
)


# ============================================================
# Conditional Routing
# ============================================================

workflow.add_conditional_edges(
    "start",
    route_module,
    {
        "feedback": "feedback",
        "facilities": "facilities",
        "visitor": "visitor",
        "financial": "financial",
        "key_collection": "key_collection",
        "defect": "defect",
        "fallback": "fallback",
    },
)


# ============================================================
# End Edges
# ============================================================

workflow.add_edge(
    "feedback",
    END,
)

workflow.add_edge(
    "facilities",
    END,
)

workflow.add_edge(
    "visitor",
    END,
)

workflow.add_edge(
    "financial",
    END,
)

workflow.add_edge(
    "key_collection",
    END,
)

workflow.add_edge(
    "defect",
    END,
)

workflow.add_edge(
    "fallback",
    END,
)


# ============================================================
# Compile Graph
# ============================================================

graph = workflow.compile()


# ============================================================
# Public Function
# ============================================================

def run_report_graph(
    question: str,
    authorization: str,
    login_id: int = None,
    property_id: int = None,
    period: str = None,
    screen_module: str = None,
    selected_module: str = None,
    detected_module: str = None,
    routing_confidence: float = None,
    routing_reason: str = None,
    conversation_id: str = None,
    conversation_history: Optional[List[dict]] = None,
    conversation_summary: str = None,
    active_module: str = None,
    rewritten_question: str = None,
) -> str:
    """
    Execute the module-specific report graph.

    Conversation fields:

        conversation_id
            Unique ID for one chat conversation.

        conversation_history
            Recent messages from this conversation only.

        conversation_summary
            Optional summary of the conversation context.

        active_module
            Last active module in this conversation.

        rewritten_question
            Context-aware version of the user's current question.

    The existing module agents continue to use `state["question"]`.
    Therefore, `question` is populated with the rewritten question
    when one is available.
    """

    # ========================================================
    # Normalize Context
    # ========================================================

    normalized_screen_module = normalize_module(
        screen_module
    )

    normalized_selected_module = normalize_module(
        selected_module
    )

    normalized_detected_module = normalize_module(
        detected_module
    )

    normalized_active_module = normalize_module(
        active_module
    )

    # ========================================================
    # Conversation History
    # ========================================================

    if conversation_history is None:
        conversation_history = []

    # ========================================================
    # Effective Question
    # ========================================================

    original_question = (
        str(
            question
        ).strip()
    )

    effective_question = original_question

    if rewritten_question is not None:
        rewritten_value = str(
            rewritten_question
        ).strip()

        if rewritten_value:
            effective_question = rewritten_value

    # ========================================================
    # Build Graph State
    # ========================================================

    state: ReportState = {
        # ----------------------------------------------------
        # Authentication
        # ----------------------------------------------------

        "authorization": authorization,

        # ----------------------------------------------------
        # Login / Property
        # ----------------------------------------------------

        "login_id": login_id,
        "property_id": property_id,

        # ----------------------------------------------------
        # Reporting Period
        # ----------------------------------------------------

        "period": period,

        # ----------------------------------------------------
        # Conversation
        # ----------------------------------------------------

        "conversation_id": conversation_id,
        "conversation_history": conversation_history,
        "conversation_summary": conversation_summary,

        # ----------------------------------------------------
        # User Questions
        # ----------------------------------------------------

        "original_question": original_question,
        "rewritten_question": effective_question,

        # Existing agents read this field.
        # Give them the context-aware question.
        "question": effective_question,

        # ----------------------------------------------------
        # Chatbot Context
        # ----------------------------------------------------

        "screen_module": normalized_screen_module,
        "selected_module": normalized_selected_module,
        "detected_module": normalized_detected_module,
        "active_module": normalized_active_module,

        # ----------------------------------------------------
        # Router Information
        # ----------------------------------------------------

        "routing_confidence": routing_confidence,
        "routing_reason": routing_reason,

        # ----------------------------------------------------
        # Backward Compatibility
        # ----------------------------------------------------

        "current_module": (
            normalized_detected_module
            or normalized_selected_module
            or normalized_active_module
            or normalized_screen_module
            or ""
        ),

        # ----------------------------------------------------
        # Final Answer
        # ----------------------------------------------------

        "answer": "",
    }

    # ========================================================
    # Execution Logging
    # ========================================================

    logger.info(
        "Running report graph | "
        "conversation_id=%s | "
        "screen=%s | "
        "selected=%s | "
        "active=%s | "
        "detected=%s | "
        "history_messages=%s | "
        "confidence=%s",
        conversation_id,
        normalized_screen_module,
        normalized_selected_module,
        normalized_active_module,
        normalized_detected_module,
        len(conversation_history),
        routing_confidence,
    )

    logger.info(
        "Original question: %s",
        original_question,
    )

    logger.info(
        "Effective question: %s",
        effective_question,
    )

    logger.info(
        "Conversation summary available: %s",
        bool(conversation_summary),
    )

    # ========================================================
    # Execute Graph
    # ========================================================

    try:
        result = graph.invoke(
            state
        )

    except Exception as ex:
        logger.exception(
            "Report graph execution failed | conversation_id=%s",
            conversation_id,
        )

        raise RuntimeError(
            f"Report graph execution failed: {str(ex)}"
        ) from ex

    # ========================================================
    # Return Answer
    # ========================================================

    answer = result.get(
        "answer"
    )

    if answer is None:
        return "No response generated."

    answer = str(
        answer
    ).strip()

    if not answer:
        return "No response generated."

    return answer