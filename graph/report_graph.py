import logging
from typing import Optional

from langgraph.graph import StateGraph, END

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
    # Feedback
    "feedback": "feedback",
    "feedbacks": "feedback",
    "complaint": "feedback",
    "complaints": "feedback",

    # Facilities
    "facility": "facilities",
    "facilities": "facilities",
    "facility_booking": "facilities",
    "facility_bookings": "facilities",
    "booking": "facilities",
    "bookings": "facilities",

    # Visitor
    "visitor": "visitor",
    "visitors": "visitor",
    "visitor_management": "visitor",
    "visitor_registration": "visitor",
    "visitor_registrations": "visitor",

    # Financial
    "financial": "financial",
    "finance": "financial",
    "financial_report": "financial",
    "financial_reports": "financial",
    "payment": "financial",
    "payments": "financial",
    "collection": "financial",
    "collections": "financial",
    "invoice": "financial",
    "invoices": "financial",

    # Key Collection
    "key": "key_collection",
    "keys": "key_collection",
    "key_collection": "key_collection",
    "key_collections": "key_collection",
    "keycollection": "key_collection",
    "keycollections": "key_collection",

    # Defect
    "defect": "defect",
    "defects": "defect",
    "maintenance_defect": "defect",
    "maintenance_defects": "defect",
}


# ============================================================
# Normalize Module
# ============================================================

def normalize_module(
    module: Optional[str]
) -> Optional[str]:
    """
    Convert a module name or alias to its canonical module name.

    Main / Dashboard / Home are treated as having no active
    business module.
    """

    if module is None:
        return None

    value = str(module).strip().lower()

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

    normalized = MODULE_ALIASES.get(value)

    if normalized in SUPPORTED_MODULES:
        return normalized

    return None


# ============================================================
# Determine Active Module
# ============================================================

def get_active_module(
    state: ReportState
) -> str:
    """
    Determine which module should be executed.

    Priority:

        1. detected_module
        2. selected_module
        3. screen_module
        4. fallback

    detected_module normally comes from the Module Router Agent.
    """

    # --------------------------------------------------------
    # 1. Router decision
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
    # 3. Current screen
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
    # 4. Backward compatibility with old state field
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
    # 5. Nothing identified
    # --------------------------------------------------------

    logger.info(
        "No valid module identified. Using fallback."
    )

    return "fallback"


# ============================================================
# Route Module
# ============================================================

def route_module(
    state: ReportState
):
    """
    LangGraph conditional routing function.
    """

    active_module = get_active_module(state)

    logger.info(
        "Graph routing to module: %s",
        active_module,
    )

    return active_module


# ============================================================
# Start Node
# ============================================================

def start_node(
    state: ReportState
):
    """
    Initial graph node.

    The router itself is executed outside this graph.
    This graph only executes the selected/detected module.
    """

    logger.info(
        "Report graph started | detected=%s | selected=%s | screen=%s",
        state.get("detected_module"),
        state.get("selected_module"),
        state.get("screen_module"),
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
) -> str:
    """
    Execute the module-specific report graph.

    Context:

        screen_module
            -> screen where chatbot was opened

        selected_module
            -> module explicitly selected by the user

        detected_module
            -> module selected by the Router Agent

    Priority:

        detected_module
            ↓
        selected_module
            ↓
        screen_module
            ↓
        fallback
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

    # ========================================================
    # Build Graph State
    # ========================================================

    state = {
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
        # User Question
        # ----------------------------------------------------
        "question": question,

        # ----------------------------------------------------
        # Chatbot Context
        # ----------------------------------------------------
        "screen_module": normalized_screen_module,
        "selected_module": normalized_selected_module,
        "detected_module": normalized_detected_module,

        # ----------------------------------------------------
        # Router Information
        # ----------------------------------------------------
        "routing_confidence": routing_confidence,
        "routing_reason": routing_reason,

        # ----------------------------------------------------
        # Backward Compatibility
        #
        # Some existing agents may still use current_module.
        # Keep it populated with the screen module first and
        # detected module as fallback.
        # ----------------------------------------------------
        "current_module": (
            normalized_screen_module
            or normalized_detected_module
            or normalized_selected_module
            or ""
        ),

        # ----------------------------------------------------
        # Final Answer
        # ----------------------------------------------------
        "answer": "",
    }

    # ========================================================
    # Log Execution Information
    # ========================================================

    logger.info(
        "Running report graph | "
        "screen=%s | selected=%s | detected=%s | "
        "confidence=%s | question=%s",
        normalized_screen_module,
        normalized_selected_module,
        normalized_detected_module,
        routing_confidence,
        question,
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
            "Report graph execution failed"
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

    answer = str(answer).strip()

    if not answer:
        return "No response generated."

    return answer