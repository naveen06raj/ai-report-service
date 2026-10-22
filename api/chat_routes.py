import logging

import re
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional

import requests

from uuid import UUID



from fastapi import APIRouter, Header, HTTPException, Query



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



from services.database.repositories.chat_repository import (

    ChatRepository,

)


from uuid import UUID

from services.database.repositories.chat_repository import ChatRepository



# ============================================================

# Logger

# ============================================================



logger = logging.getLogger(__name__)





# ============================================================

# Langfuse

# ============================================================



langfuse = get_client()


PROPERTY_LIST_URL = "https://newaws.panzerplayground.com/api/ai/propertylist"


def get_property_name(property_id: int, authorization: str) -> str:
    """Resolve a property name from the authenticated property-list API."""
    try:
        response = requests.get(
            PROPERTY_LIST_URL,
            headers={"Authorization": authorization, "Accept": "application/json"},
            timeout=15,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict) or payload.get("response") != 1:
            raise ValueError("Property List API returned an unsuccessful response")
        data = payload.get("data") or {}
        properties = data.get("assinged_properties") or []
        for item in properties:
            try:
                matches = int(item.get("id")) == int(property_id)
            except (TypeError, ValueError):
                matches = False
            if matches and item.get("name"):
                return str(item["name"]).strip()
        raise ValueError(f"Property ID {property_id} was not found")
    except Exception:
        logger.exception("Could not resolve property name for property_id=%s", property_id)
        return "your property"


def get_time_based_greeting() -> str:
    """Return a greeting based on Singapore local time."""
    hour = datetime.now(ZoneInfo("Asia/Singapore")).hour
    if 5 <= hour < 12:
        return "Good morning"
    if 12 <= hour < 17:
        return "Good afternoon"
    return "Good evening"






# ============================================================

# Router

# ============================================================



router = APIRouter(

    prefix="/chat",

    tags=["AI Chat"],

)


# ============================================================
# Recent conversations and conversation history APIs
# ============================================================


@router.get("/recent")
async def get_recent_chats(
    login_id: int = Query(...),
    property_id: int = Query(...),
    authorization: str = Header(None),
):
    """Return up to five most recently active conversations."""
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing",
        )

    try:
        recent_chats = ChatRepository.get_recent_sessions(
            login_id=login_id,
            property_id=property_id,
            limit=5,
        )
        return {
            "status": True,
            "count": len(recent_chats),
            "recent_chats": recent_chats,
        }
    except Exception as exc:
        logger.exception("Failed to retrieve recent chats")
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve recent conversations",
        ) from exc


@router.get("/history/{conversation_id}")
async def get_chat_history(
    conversation_id: str,
    login_id: int = Query(...),
    property_id: int = Query(...),
    authorization: str = Header(None),
):
    """Load all saved messages for one conversation owned by this user/property."""
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing",
        )

    try:
        parsed_id = UUID(conversation_id)
    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid conversation_id",
        ) from exc

    try:
        session = ChatRepository.get_session(
            conversation_id=parsed_id,
            login_id=login_id,
            property_id=property_id,
        )
        if session is None:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found",
            )

        messages = ChatRepository.get_all_messages(
            conversation_id=parsed_id,
            login_id=login_id,
            property_id=property_id,
        )

        return {
            "status": True,
            "conversation_id": str(parsed_id),
            "screen_module": session.screen_module,
            "selected_module": session.selected_module,
            "active_module": session.active_module,
            "messages": [
                {
                    "role": message.role,
                    "message": message.message,
                    "module": message.module,
                    "created_at": (
                        message.created_at.isoformat()
                        if message.created_at else None
                    ),
                }
                for message in messages
            ],
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to load conversation history")
        raise HTTPException(
            status_code=500,
            detail="Unable to load conversation history",
        ) from exc






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

# Business Modules

# ============================================================



BUSINESS_MODULES = {

    "feedback",

    "facilities",

    "visitor",

    "financial",

    "key_collection",

    "defect",

}





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

    """



    return CHAT_MODULES.copy()





# ============================================================

# Helper: Detect Simple Greeting

# ============================================================



def is_greeting(question: str) -> bool:

    """

    Detect simple greetings.



    Greetings must be handled before router/database report

    execution.

    """



    if not question:

        return False



    value = str(

        question

    ).strip().lower()



    # Remove common trailing punctuation.

    value = re.sub(

        r"[!?,.]+$",

        "",

        value,

    ).strip()



    greetings = {

        "hi",

        "hello",

        "hey",

        "hi there",

        "hello there",

        "hey there",

        "good morning",

        "good afternoon",

        "good evening",

    }



    return value in greetings





# ============================================================

# Helper: Get Greeting

# ============================================================



def get_greeting(
    screen_module: Optional[str],
    selected_module: Optional[str] = None,
    property_name: str = "your property",
) -> str:
    """Return the initial EMMA welcome or a module-selection confirmation."""
    if selected_module:
        display_name = MODULE_DISPLAY_NAMES.get(
            selected_module, selected_module.replace("_", " ").title()
        )
        return f"You have selected {display_name}. How can I help you with {display_name}?"
    return (
        f"{get_time_based_greeting()}! I'm EMMA, your operational assistant "
        f"for {property_name}. How can I help you today?"
    )


def normalize_screen_context(

    module: Optional[str],

) -> Optional[str]:

    """

    Normalize the screen module.



    Main / Dashboard / Home represent no active business module.

    """



    if module is None:

        return None



    value = str(

        module

    ).strip().lower()



    if value in {

        "",

        "main",

        "dashboard",

        "home",

        "none",

        "null",

    }:

        return None



    return normalize_module(

        value

    )





# ============================================================

# Helper: Parse Conversation ID

# ============================================================



def parse_conversation_id(

    conversation_id,

) -> Optional[UUID]:

    """

    Validate and convert a conversation_id into UUID.

    """



    if conversation_id is None:

        return None



    value = str(

        conversation_id

    ).strip()



    if not value:

        return None



    try:

        return UUID(value)



    except ValueError as ex:

        raise HTTPException(

            status_code=400,

            detail="conversation_id must be a valid UUID",

        ) from ex





# ============================================================

# Helper: Determine Active Module

# ============================================================



def determine_active_module(

    detected_module: Optional[str],

    selected_module: Optional[str],

    existing_active_module: Optional[str],

    screen_module: Optional[str],

) -> Optional[str]:

    """

    Determine the module that should remain active for the

    conversation after the current request.



    Fallback does not replace an existing business module.

    """



    # --------------------------------------------------------

    # Current detected business module

    # --------------------------------------------------------



    if detected_module in BUSINESS_MODULES:

        return detected_module



    # --------------------------------------------------------

    # Preserve existing conversation module

    # --------------------------------------------------------



    if existing_active_module in BUSINESS_MODULES:

        return existing_active_module



    # --------------------------------------------------------

    # Selected module

    # --------------------------------------------------------



    if selected_module in BUSINESS_MODULES:

        return selected_module



    # --------------------------------------------------------

    # Current screen

    # --------------------------------------------------------



    if screen_module in BUSINESS_MODULES:

        return screen_module



    return None





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



    Conversation behavior:



    1. New Chat

       conversation_id = null



       No previous history is loaded.



    2. First real question

       A new conversation is created.



    3. Existing conversation

       conversation_id is supplied.



       Only that conversation's history is loaded.



    4. Follow-up question

       Previous conversation history is supplied to the router.



    5. The router can rewrite the question into a

       self-contained question.



    6. The module graph receives the conversation context.



    7. User and assistant messages are saved to the same

       conversation_id.

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



        conversation_id_value = request.get(

            "conversation_id"

        )



        screen_module = request.get(

            "screen_module"

        )



        selected_module = request.get(

            "selected_module"

        )



        question = request.get(

            "question"

        )



        # ====================================================

        # Backward Compatibility

        # ====================================================



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



        except (

            TypeError,

            ValueError,

        ) as ex:



            raise HTTPException(

                status_code=400,

                detail=(

                    "login_id and property_id "

                    "must be integers"

                ),

            ) from ex



        # ====================================================

        # Normalize Question

        # ====================================================



        if question is None:

            question = ""



        question = str(

            question

        ).strip()



        # ====================================================

        # Normalize Screen Module

        # ====================================================



        normalized_screen_module = (

            normalize_screen_context(

                screen_module

            )

        )



        # ====================================================

        # Normalize Selected Module

        # ====================================================



        normalized_selected_module = normalize_module(

            selected_module

        )



        # ====================================================

        # Validate Selected Module

        # ====================================================



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



        # ====================================================

        # Parse Conversation ID

        # ====================================================



        conversation_id = parse_conversation_id(

            conversation_id_value

        )



        # ====================================================

        # Debug Request

        # ====================================================



        print("=" * 80)

        print("CHAT REQUEST")

        print("=" * 80)

        print("LOGIN ID:", login_id)

        print("PROPERTY ID:", property_id)

        print(

            "CONVERSATION ID:",

            conversation_id,

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

        # CASE 1:

        # Greeting / Chatbot Opening / Module Selection

        # ====================================================



        # ----------------------------------------------------

        # Opening / Button selection

        #

        # No database conversation is created here.

        # ----------------------------------------------------



        if not question:



            property_name = get_property_name(property_id, authorization)

            greeting = get_greeting(

                screen_module=normalized_screen_module,

                selected_module=normalized_selected_module,

                property_name=property_name,

            )



            response_data = {

                "status": True,

                "type": "module_selection" if normalized_selected_module else "greeting",

                "login_id": login_id,

                "property_id": property_id,

                "conversation_id": (

                    str(conversation_id)

                    if conversation_id

                    else None

                ),

                "screen_module": normalized_screen_module,

                "selected_module": normalized_selected_module,

                "detected_module": None,

                "routing_confidence": None,

                "question": "",

                "answer": greeting,

                "options": get_module_options() if not normalized_selected_module else [],

            }



            print("=" * 80)

            print("CHAT GREETING")

            print("=" * 80)

            print(

                "CONVERSATION ID:",

                conversation_id,

            )

            print(

                "ANSWER:",

                greeting,

            )

            print("=" * 80)



            return response_data



        # ----------------------------------------------------

        # Simple greeting

        #

        # IMPORTANT:

        # Do not call router.

        # Do not call report graph.

        # Do not save greeting as chat history.

        # ----------------------------------------------------



        if is_greeting(question):



            property_name = get_property_name(property_id, authorization)

            greeting = get_greeting(

                screen_module=normalized_screen_module,

                selected_module=normalized_selected_module,

                property_name=property_name,

            )



            response_data = {

                "status": True,

                "type": "module_selection" if normalized_selected_module else "greeting",

                "login_id": login_id,

                "property_id": property_id,

                "conversation_id": (

                    str(conversation_id)

                    if conversation_id

                    else None

                ),

                "screen_module": normalized_screen_module,

                "selected_module": normalized_selected_module,

                "detected_module": None,

                "routing_confidence": None,

                "question": question,

                "answer": greeting,

                "options": get_module_options() if not normalized_selected_module else [],

            }



            print("=" * 80)

            print("SIMPLE GREETING")

            print("=" * 80)

            print(

                "QUESTION:",

                question,

            )

            print(

                "CONVERSATION ID:",

                conversation_id,

            )

            print(

                "ANSWER:",

                greeting,

            )

            print("=" * 80)



            return response_data



        # ====================================================

        # CASE 2:

        # Real User Question

        # ====================================================



        # ====================================================

        # Load / Create Conversation

        # ====================================================



        conversation_history = []

        conversation_summary = None

        existing_active_module = None



        # ----------------------------------------------------

        # Existing conversation

        # ----------------------------------------------------



        if conversation_id:



            print("=" * 80)

            print("LOADING EXISTING CONVERSATION")

            print("=" * 80)

            print(

                "CONVERSATION ID:",

                conversation_id,

            )



            try:

                session = ChatRepository.get_or_create_session(

                    login_id=login_id,

                    property_id=property_id,

                    conversation_id=conversation_id,

                )



            except ValueError as ex:



                raise HTTPException(

                    status_code=404,

                    detail=str(ex),

                ) from ex



            # ------------------------------------------------

            # Session context

            # ------------------------------------------------



            existing_active_module = normalize_module(

                session.active_module

            )



            conversation_summary = (

                session.conversation_summary

            )



            stored_screen_module = normalize_screen_context(

                session.screen_module

            )



            stored_selected_module = normalize_module(

                session.selected_module

            )



            # ------------------------------------------------

            # Use request context first.

            # Stored conversation context is fallback.

            # ------------------------------------------------



            effective_screen_module = (

                normalized_screen_module

                or stored_screen_module

            )



            effective_selected_module = (

                normalized_selected_module

                or stored_selected_module

            )



            # ------------------------------------------------

            # Load previous messages

            # ------------------------------------------------



            conversation_history = (

                ChatRepository.get_history_for_llm(

                    conversation_id=conversation_id,

                    login_id=login_id,

                    property_id=property_id,

                    limit=20,

                )

            )



            print(

                "PREVIOUS HISTORY MESSAGES:",

                len(conversation_history),

            )



            print(

                "EXISTING ACTIVE MODULE:",

                existing_active_module,

            )



            print("=" * 80)



        # ----------------------------------------------------

        # New conversation

        # ----------------------------------------------------



        else:



            print("=" * 80)

            print("NEW CONVERSATION")

            print("=" * 80)

            print(

                "No conversation_id supplied."

            )

            print(

                "Previous history will NOT be used."

            )



            conversation_history = []

            conversation_summary = None

            existing_active_module = None



            effective_screen_module = (

                normalized_screen_module

            )



            effective_selected_module = (

                normalized_selected_module

            )



            # ------------------------------------------------

            # Create conversation now because the user has

            # submitted the first real question.

            #

            # We do NOT create a session when the chatbot

            # is merely opened.

            # ------------------------------------------------



            session = ChatRepository.create_session(

                login_id=login_id,

                property_id=property_id,

                screen_module=effective_screen_module,

                selected_module=effective_selected_module,

                active_module=None,

            )



            conversation_id = (

                session.conversation_id

            )



            print(

                "NEW CONVERSATION CREATED:",

                conversation_id,

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

                "conversation_id": str(

                    conversation_id

                ),

                "screen_module": (

                    effective_screen_module

                ),

                "selected_module": (

                    effective_selected_module

                ),

                "active_module": (

                    existing_active_module

                ),

                "question": question,

                "history_messages": len(

                    conversation_history

                ),

            },

        ) as root_span:



            # ==================================================

            # Langfuse Attributes

            # ==================================================



            trace_tags = [

                "chat",

                "agentic",

            ]



            if effective_screen_module:

                trace_tags.append(

                    effective_screen_module

                )



            if effective_selected_module:

                trace_tags.append(

                    effective_selected_module

                )



            if existing_active_module:

                trace_tags.append(

                    existing_active_module

                )



            with propagate_attributes(

                user_id=str(login_id),

                session_id=str(

                    conversation_id

                ),

                tags=trace_tags,

                metadata={

                    "login_id": login_id,

                    "property_id": property_id,

                    "conversation_id": str(

                        conversation_id

                    ),

                    "screen_module": (

                        effective_screen_module

                    ),

                    "selected_module": (

                        effective_selected_module

                    ),

                    "active_module": (

                        existing_active_module

                    ),

                },

            ):



                # ==================================================

                # Print Conversation Context

                # ==================================================



                print("=" * 80)

                print("CONVERSATION CONTEXT")

                print("=" * 80)



                print(

                    "CONVERSATION ID:",

                    conversation_id,

                )



                print(

                    "HISTORY COUNT:",

                    len(conversation_history),

                )



                print(

                    "ACTIVE MODULE:",

                    existing_active_module,

                )



                print(

                    "CURRENT QUESTION:",

                    question,

                )



                print("=" * 80)



                # ==================================================

                # Router

                # ==================================================



                print("=" * 80)

                print("AGENTIC ROUTER")

                print("=" * 80)



                routing_result = route_question(

                    question=question,

                    screen_module=(

                        effective_screen_module

                    ),

                    selected_module=(

                        effective_selected_module

                    ),

                    conversation_history=(

                        conversation_history

                    ),

                    conversation_summary=(

                        conversation_summary

                    ),

                    active_module=(

                        existing_active_module

                    ),

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



                rewritten_question = routing_result.get(

                    "rewritten_question"

                )




                # Conversation-history intent is handled by a dedicated graph path.
                # Default preserves compatibility with routers that do not return intent_type.
                intent_type = routing_result.get("intent_type", "report_query")
                if not isinstance(intent_type, str) or not intent_type.strip():
                    intent_type = "report_query"
                intent_type = intent_type.strip().lower()
                print("INTENT TYPE:", intent_type)

                if not rewritten_question:

                    rewritten_question = question



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



                print(

                    "REWRITTEN QUESTION:",

                    rewritten_question,

                )



                print("=" * 80)



                # ==================================================

                # Determine Active Conversation Module

                # ==================================================



                final_active_module = (

                    determine_active_module(

                        detected_module=detected_module,

                        selected_module=(

                            effective_selected_module

                        ),

                        existing_active_module=(

                            existing_active_module

                        ),

                        screen_module=(

                            effective_screen_module

                        ),

                    )

                )



                print("=" * 80)

                print("ACTIVE CONVERSATION MODULE")

                print("=" * 80)



                print(

                    "FINAL ACTIVE MODULE:",

                    final_active_module,

                )



                print("=" * 80)



                # ==================================================

                # Save User Message

                # ==================================================



                ChatRepository.save_message(

                    conversation_id=conversation_id,

                    login_id=login_id,

                    property_id=property_id,

                    role="user",

                    message=question,

                    module=(

                        detected_module

                        if detected_module

                        else final_active_module

                    ),

                )



                print("=" * 80)

                print("USER MESSAGE SAVED")

                print("=" * 80)



                print(

                    "CONVERSATION ID:",

                    conversation_id,

                )



                print(

                    "MESSAGE:",

                    question,

                )



                print(

                    "MODULE:",

                    detected_module,

                )



                print("=" * 80)



                # ==================================================

                # Run Module Graph

                # ==================================================



                print("=" * 80)

                print("RUNNING REPORT GRAPH")

                print("=" * 80)



                response = run_report_graph(

                    question=question,

                    authorization=authorization,

                    login_id=login_id,

                    property_id=property_id,

                    period=None,



                    # Current context

                    screen_module=(

                        effective_screen_module

                    ),



                    selected_module=(

                        effective_selected_module

                    ),



                    # Current router decision

                    detected_module=(

                        detected_module

                    ),



                    routing_confidence=(

                        routing_confidence

                    ),



                    routing_reason=(

                        routing_reason

                    ),



                    # Conversation context

                    conversation_id=str(

                        conversation_id

                    ),



                    conversation_history=(

                        conversation_history

                    ),



                    conversation_summary=(

                        conversation_summary

                    ),



                    active_module=(

                        final_active_module

                    ),



                    # Context-aware question

                    rewritten_question=(

                        rewritten_question

                    ),


                    # Dedicated route for conversation-history questions.
                    intent_type=intent_type,
                )



                print(

                    "GRAPH RESPONSE:",

                    response,

                )



                print("=" * 80)



                # ==================================================

                # Save Assistant Message

                # ==================================================



                ChatRepository.save_message(

                    conversation_id=conversation_id,

                    login_id=login_id,

                    property_id=property_id,

                    role="assistant",

                    message=str(

                        response

                    ).strip(),

                    module=(

                        detected_module

                        if detected_module

                        in BUSINESS_MODULES

                        else final_active_module

                    ),

                )



                print("=" * 80)

                print("ASSISTANT MESSAGE SAVED")

                print("=" * 80)



                print(

                    "CONVERSATION ID:",

                    conversation_id,

                )



                print(

                    "MODULE:",

                    detected_module,

                )



                print("=" * 80)



                # ==================================================

                # Update Conversation Context

                # ==================================================



                ChatRepository.update_session_context(

                    conversation_id=conversation_id,

                    login_id=login_id,

                    property_id=property_id,



                    screen_module=(

                        effective_screen_module

                    ),



                    selected_module=(

                        effective_selected_module

                    ),



                    active_module=(

                        final_active_module

                    ),



                    # We intentionally do not generate a new

                    # conversation summary here yet.

                    conversation_summary=None,

                )



                print("=" * 80)

                print("CONVERSATION CONTEXT UPDATED")

                print("=" * 80)



                print(

                    "ACTIVE MODULE:",

                    final_active_module,

                )



                print("=" * 80)



                # ==================================================

                # Langfuse Parent Output

                # ==================================================



                root_span.update(

                    output={

                        "conversation_id": str(

                            conversation_id

                        ),

                        "detected_module": (

                            detected_module

                        ),

                        "routing_confidence": (

                            routing_confidence

                        ),

                        "routing_reason": (

                            routing_reason

                        ),

                        "rewritten_question": (

                            rewritten_question

                        ),

                        "intent_type": intent_type,

                        "active_module": (

                            final_active_module

                        ),

                        "answer": response,

                    }

                )



                # ==================================================

                # Langfuse Trace Debug

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



                    # IMPORTANT:

                    # Frontend must save this ID and send the

                    # same ID for follow-up questions.

                    "conversation_id": str(

                        conversation_id

                    ),



                    "screen_module": (

                        effective_screen_module

                    ),



                    "selected_module": (

                        effective_selected_module

                    ),



                    "detected_module": (

                        detected_module

                    ),



                    "active_module": (

                        final_active_module

                    ),



                    "routing_confidence": (

                        routing_confidence

                    ),



                    "question": question,



                    "rewritten_question": (

                        rewritten_question

                    ),

                    "intent_type": intent_type,

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



    # ========================================================

    # Langfuse Flush

    # ========================================================



    finally:



        try:

            langfuse.flush()



        except Exception:

            logger.exception(

                "Langfuse flush failed"

            )