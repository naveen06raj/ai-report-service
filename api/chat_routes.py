import logging
from typing import Optional

from fastapi import (
    APIRouter,
    Header,
    HTTPException,
)

from langfuse import (
    get_client,
    propagate_attributes,
)

from agents.module_router_agent import (
    normalize_module,
    route_question,
)

from graph.report_graph import (
    run_report_graph,
)


# ============================================================
# Logger
# ============================================================

logger = logging.getLogger(__name__)


# ============================================================
# Langfuse
# ============================================================

langfuse = get_client()


# ============================================================
# Router
# ============================================================

router = APIRouter(
    prefix="/chat",
    tags=["AI Chat"],
)


# ============================================================
# Supported Chatbot Modules
# ============================================================

CHAT_MODULES = [
    {
        "module": "feedback",
        "label": "Feedback",
    },
    {
        "module": "facilities",
        "label": "Facility Bookings",
    },
    {
        "module": "key_collection",
        "label": "Key Collection",
    },
    {
        "module": "visitor",
        "label": "Visitor Management",
    },
    {
        "module": "financial",
        "label": "Financial Reports",
    },
    {
        "module": "defect",
        "label": "Defects",
    },
]


# ============================================================
# Module Display Names
# ============================================================

MODULE_DISPLAY_NAMES = {
    "feedback": "Feedback",
    "facilities": "Facility Bookings",
    "key_collection": "Key Collection",
    "visitor": "Visitor Management",
    "financial": "Financial Reports",
    "defect": "Defects",
}


# ============================================================
# Greeting Messages
# ============================================================

COMMON_GREETING = (
    "Hi! How can I help you with your property management reports?"
)


MODULE_GREETINGS = {
    "feedback": (
        "Hi! You're on the Feedback screen. "
        "You can ask me anything related to Feedback."
    ),

    "facilities": (
        "Hi! You're on the Facility Bookings screen. "
        "You can ask me anything related to Facility Bookings."
    ),

    "key_collection": (
        "Hi! You're on the Key Collection screen. "
        "You can ask me anything related to Key Collection."
    ),

    "visitor": (
        "Hi! You're on the Visitor Management screen. "
        "You can ask me anything related to Visitor Management."
    ),

    "financial": (
        "Hi! You're on the Financial Reports screen. "
        "You can ask me anything related to Financial Reports."
    ),

    "defect": (
        "Hi! You're on the Defects screen. "
        "You can ask me anything related to Defects."
    ),
}


# ============================================================
# Helper: Build Module Buttons
# ============================================================

def get_module_options():
    """
    Return the six supported chatbot module options.

    These options are displayed whenever the chatbot is opened
    or when the user needs to select a module.
    """

    return CHAT_MODULES.copy()


# ============================================================
# Helper: Get Greeting
# ============================================================

def get_greeting(
    screen_module: Optional[str],
    selected_module: Optional[str] = None,
) -> str:
    """
    Generate the chatbot opening/selection greeting.

    Main / Dashboard:
        Common greeting.

    Module screen:
        Module-specific greeting.

    Selected module:
        Acknowledge the selected module.
    """

    # --------------------------------------------------------
    # User explicitly selected a module
    # --------------------------------------------------------

    if selected_module:
        display_name = MODULE_DISPLAY_NAMES.get(
            selected_module,
            selected_module.replace("_", " ").title(),
        )

        return (
            f"Hi! {display_name} is selected. "
            f"You can ask me anything related to {display_name}."
        )

    # --------------------------------------------------------
    # User opened chatbot from a supported module screen
    # --------------------------------------------------------

    if screen_module:
        return MODULE_GREETINGS.get(
            screen_module,
            COMMON_GREETING,
        )

    # --------------------------------------------------------
    # User opened chatbot from Main / Dashboard
    # --------------------------------------------------------

    return COMMON_GREETING


# ============================================================
# Helper: Normalize Screen Module
# ============================================================

def normalize_screen_context(
    module: Optional[str],
) -> Optional[str]:
    """
    Normalize the screen module.

    Main / Dashboard / Home represent no active business module.
    """

    if module is None:
        return None

    value = str(module).strip().lower()

    if value in {
        "",
        "main",
        "dashboard",
        "home",
        "none",
        "null",
    }:
        return None

    normalized = normalize_module(
        value
    )

    return normalized


# ============================================================
# POST /chat/ask
# ============================================================

@router.post("/ask")
async def ask_ai(
    request: dict,
    authorization: str = Header(None),
):
    """
    Main production Agentic Chatbot endpoint.

    Supported request concepts:

        screen_module
            Module screen where chatbot was opened.

        selected_module
            Module selected from chatbot buttons.

        question
            User's actual question.

    Examples
    --------

    Main screen opening:

        {
            "login_id": 66,
            "property_id": 1,
            "screen_module": "main",
            "selected_module": null,
            "question": ""
        }

    Feedback screen opening:

        {
            "login_id": 66,
            "property_id": 1,
            "screen_module": "feedback",
            "selected_module": null,
            "question": ""
        }

    Button selection:

        {
            "login_id": 66,
            "property_id": 1,
            "screen_module": "feedback",
            "selected_module": "visitor",
            "question": ""
        }

    Actual question:

        {
            "login_id": 66,
            "property_id": 1,
            "screen_module": "feedback",
            "selected_module": "feedback",
            "question": "Show me key collections last 3 months"
        }
    """

    root_span = None

    try:

        # ====================================================
        # Authorization Validation
        # ====================================================

        if not authorization:
            raise HTTPException(
                status_code=401,
                detail="Authorization header missing",
            )

        # ====================================================
        # Request Values
        # ====================================================

        login_id = request.get(
            "login_id"
        )

        property_id = request.get(
            "property_id"
        )

        # ----------------------------------------------------
        # New production fields
        # ----------------------------------------------------

        screen_module = request.get(
            "screen_module"
        )

        selected_module = request.get(
            "selected_module"
        )

        question = request.get(
            "question"
        )

        # ----------------------------------------------------
        # Backward compatibility
        #
        # Existing frontend may still send:
        #
        #     "module": "feedback"
        #
        # We temporarily accept it as screen_module.
        # ----------------------------------------------------

        if screen_module is None:
            screen_module = request.get(
                "module"
            )

        # ====================================================
        # Required Validation
        # ====================================================

        if login_id is None:
            raise HTTPException(
                status_code=400,
                detail="login_id is required",
            )

        if property_id is None:
            raise HTTPException(
                status_code=400,
                detail="property_id is required",
            )

        # Question is intentionally NOT required here.
        #
        # Empty question means:
        #
        #     chatbot opening
        #     OR
        #     module button selection
        #
        # In those cases we return greeting + buttons.
        # ====================================================

        # ====================================================
        # Convert IDs
        # ====================================================

        try:
            login_id = int(
                login_id
            )

            property_id = int(
                property_id
            )

        except (TypeError, ValueError):

            raise HTTPException(
                status_code=400,
                detail="login_id and property_id must be integers",
            )

        # ====================================================
        # Normalize Context
        # ====================================================

        normalized_screen_module = normalize_screen_context(
            screen_module
        )

        normalized_selected_module = normalize_module(
            selected_module
        )

        # ----------------------------------------------------
        # Validate selected module
        # ----------------------------------------------------

        if (
            selected_module is not None
            and str(selected_module).strip()
            and normalized_selected_module is None
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid selected_module: "
                    f"{selected_module}"
                ),
            )

        # ----------------------------------------------------
        # Convert question to clean string
        # ----------------------------------------------------

        if question is None:
            question = ""

        question = str(
            question
        ).strip()

        # ====================================================
        # Debug
        # ====================================================

        print("=" * 80)
        print("CHAT REQUEST")
        print("=" * 80)

        print(
            "LOGIN ID:",
            login_id,
        )

        print(
            "PROPERTY ID:",
            property_id,
        )

        print(
            "SCREEN MODULE:",
            normalized_screen_module,
        )

        print(
            "SELECTED MODULE:",
            normalized_selected_module,
        )

        print(
            "QUESTION:",
            question,
        )

        print("=" * 80)

        # ====================================================
        # Langfuse Parent Trace
        # ====================================================

        with langfuse.start_as_current_observation(
            as_type="span",
            name="agentic-chat-ask",
            input={
                "login_id": login_id,
                "property_id": property_id,
                "screen_module": normalized_screen_module,
                "selected_module": normalized_selected_module,
                "question": question,
            },
        ) as root_span:

            # Save for exception handling
            # outside the with block.
            root_span = root_span

            # ==================================================
            # Langfuse Attributes
            # ==================================================

            trace_tags = [
                "chat",
                "agentic",
            ]

            if normalized_screen_module:
                trace_tags.append(
                    normalized_screen_module
                )

            if normalized_selected_module:
                trace_tags.append(
                    normalized_selected_module
                )

            with propagate_attributes(
                user_id=str(login_id),
                session_id=str(property_id),
                tags=trace_tags,
                metadata={
                    "login_id": login_id,
                    "property_id": property_id,
                    "screen_module": normalized_screen_module,
                    "selected_module": normalized_selected_module,
                },
            ):

                # ==================================================
                # CASE 1:
                # Chatbot Opening / Module Button Selection
                #
                # No question = do NOT call Router Agent.
                # ==================================================

                if not question:

                    greeting = get_greeting(
                        screen_module=normalized_screen_module,
                        selected_module=normalized_selected_module,
                    )

                    response_data = {
                        "status": True,
                        "type": "greeting",
                        "login_id": login_id,
                        "property_id": property_id,
                        "screen_module": normalized_screen_module,
                        "selected_module": normalized_selected_module,
                        "detected_module": None,
                        "routing_confidence": None,
                        "question": "",
                        "answer": greeting,
                        "options": get_module_options(),
                    }

                    # ----------------------------------------------
                    # Langfuse output
                    # ----------------------------------------------

                    root_span.update(
                        output={
                            "type": "greeting",
                            "screen_module": normalized_screen_module,
                            "selected_module": normalized_selected_module,
                            "answer": greeting,
                        }
                    )

                    print("=" * 80)
                    print("CHAT GREETING")
                    print("=" * 80)

                    print(
                        "SCREEN MODULE:",
                        normalized_screen_module,
                    )

                    print(
                        "SELECTED MODULE:",
                        normalized_selected_module,
                    )

                    print(
                        "ANSWER:",
                        greeting,
                    )

                    print("=" * 80)

                    return response_data

                # ==================================================
                # CASE 2:
                # Actual User Question
                # ==================================================

                print("=" * 80)
                print("AGENTIC ROUTER")
                print("=" * 80)

                print(
                    "QUESTION:",
                    question,
                )

                print(
                    "SCREEN MODULE:",
                    normalized_screen_module,
                )

                print(
                    "SELECTED MODULE:",
                    normalized_selected_module,
                )

                # ----------------------------------------------
                # Router Agent
                # ----------------------------------------------

                routing_result = route_question(
                    question=question,
                    screen_module=normalized_screen_module,
                    selected_module=normalized_selected_module,
                )

                detected_module = routing_result.get(
                    "module"
                )

                routing_confidence = routing_result.get(
                    "confidence"
                )

                routing_reason = routing_result.get(
                    "reason"
                )

                print(
                    "DETECTED MODULE:",
                    detected_module,
                )

                print(
                    "ROUTING CONFIDENCE:",
                    routing_confidence,
                )

                print(
                    "ROUTING REASON:",
                    routing_reason,
                )

                print("=" * 80)

                # ==================================================
                # Run Module Graph
                # ==================================================

                response = run_report_graph(
                    question=question,
                    authorization=authorization,
                    login_id=login_id,
                    property_id=property_id,
                    period=None,
                    screen_module=normalized_screen_module,
                    selected_module=normalized_selected_module,
                    detected_module=detected_module,
                    routing_confidence=routing_confidence,
                    routing_reason=routing_reason,
                )

                # ==================================================
                # Langfuse Parent Output
                # ==================================================

                root_span.update(
                    output={
                        "detected_module": detected_module,
                        "routing_confidence": routing_confidence,
                        "routing_reason": routing_reason,
                        "answer": response,
                    }
                )

                # ==================================================
                # Trace Debug
                # ==================================================

                print("=" * 80)
                print("AGENTIC LANGFUSE TRACE")
                print("=" * 80)

                print(
                    "TRACE ID:",
                    root_span.trace_id,
                )

                print("=" * 80)

                # ==================================================
                # Final Response
                # ==================================================

                return {
                    "status": True,
                    "type": "answer",
                    "login_id": login_id,
                    "property_id": property_id,
                    "screen_module": normalized_screen_module,
                    "selected_module": normalized_selected_module,
                    "detected_module": detected_module,
                    "routing_confidence": routing_confidence,
                    "question": question,
                    "answer": response,
                }

    # ========================================================
    # HTTP Errors
    # ========================================================

    except HTTPException:
        raise

    # ========================================================
    # General Errors
    # ========================================================

    except Exception as ex:

        logger.exception(
            "Agentic chat request failed"
        )

        raise HTTPException(
            status_code=500,
            detail=str(ex),
        )

    finally:

        # ====================================================
        # Flush Langfuse
        # ====================================================

        try:
            langfuse.flush()

        except Exception:

            logger.exception(
                "Langfuse flush failed"
            )