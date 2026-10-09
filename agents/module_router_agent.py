import json
import logging
import re
from typing import Any, Dict, List, Optional

from services.llm.gemini_client import generate


logger = logging.getLogger(__name__)


# ============================================================
# Supported Business Modules
# ============================================================

BUSINESS_MODULES = {
    "feedback",
    "facilities",
    "visitor",
    "financial",
    "key_collection",
    "defect",
}

# Fallback is not a business module.
# It is used when the question is unrelated or unclear.
ALLOWED_MODULES = BUSINESS_MODULES | {"fallback"}


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

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    "fallback": "fallback",
    "unknown": "fallback",
    "other": "fallback",
    "general": "fallback",
}


# ============================================================
# Special Context Values
# ============================================================

NO_MODULE_CONTEXTS = {
    "",
    "none",
    "null",
    "main",
    "dashboard",
    "home",
}


# ============================================================
# Format Conversation History
# ============================================================

def _format_conversation_history(
    conversation_history: Optional[List[Dict[str, Any]]],
    conversation_summary: Optional[str] = None,
    active_module: Optional[str] = None,
) -> str:
    """
    Format recent conversation context for the router.

    Conversation history is used only to understand the current
    question. It is NOT current report data.
    """

    sections: List[str] = []

    # --------------------------------------------------------
    # Active conversation module
    # --------------------------------------------------------

    if active_module:
        sections.append(
            "ACTIVE CONVERSATION MODULE:\n"
            f"{active_module}"
        )

    # --------------------------------------------------------
    # Conversation summary
    # --------------------------------------------------------

    if conversation_summary:
        summary = str(
            conversation_summary
        ).strip()

        if summary:
            sections.append(
                "CONVERSATION SUMMARY:\n"
                f"{summary[:4000]}"
            )

    # --------------------------------------------------------
    # No history
    # --------------------------------------------------------

    if not conversation_history:
        sections.append(
            "RECENT CONVERSATION:\n"
            "No previous conversation messages."
        )

        return "\n\n".join(sections)

    # --------------------------------------------------------
    # Only use latest 20 messages
    # --------------------------------------------------------

    recent_history = conversation_history[-20:]

    history_lines: List[str] = []

    for item in recent_history:

        if not isinstance(item, dict):
            continue

        role = str(
            item.get("role", "unknown")
        ).strip().lower()

        message = str(
            item.get("message", "")
        ).strip()

        if not message:
            continue

        # Prevent one huge message from consuming the prompt.
        message = message[:2000]

        role_label = {
            "user": "USER",
            "assistant": "ASSISTANT",
        }.get(
            role,
            role.upper(),
        )

        module = item.get("module")

        if module:
            history_lines.append(
                f"{role_label} [{module}]: {message}"
            )
        else:
            history_lines.append(
                f"{role_label}: {message}"
            )

    # --------------------------------------------------------
    # Build history section
    # --------------------------------------------------------

    if history_lines:
        sections.append(
            "RECENT CONVERSATION:\n"
            + "\n".join(history_lines)
        )
    else:
        sections.append(
            "RECENT CONVERSATION:\n"
            "No usable previous conversation messages."
        )

    return "\n\n".join(sections)


# ============================================================
# Router Prompt
# ============================================================

ROUTER_PROMPT = """
You are the module routing agent for a production Property Management AI system.

Your ONLY job is to:

1. Determine which module should handle the user's CURRENT question.
2. Rewrite the CURRENT question into a self-contained question when
   previous conversation context is required.

You must NOT answer the user's question.

============================================================
AVAILABLE BUSINESS MODULES
============================================================

1. feedback

- resident feedback
- complaints
- ratings
- feedback categories
- feedback trends
- feedback submissions

2. facilities

- facility bookings
- booking status
- facility usage
- facility revenue
- booking trends
- facility availability

3. visitor

- visitors
- visitor registrations
- visitor purpose
- visitor status
- visitor trends
- guest registrations

4. financial

- financial reports
- payments
- financial collections
- invoices
- outstanding amounts
- excess payments
- balances
- amount due

5. key_collection

- key collections
- key collection status
- collected keys
- pending key collections
- cancelled key collections
- key collection appointments
- key handover

6. defect

- defects
- maintenance defects
- defect status
- defect category
- defect priority
- maintenance issues
- reported defects

============================================================
FALLBACK
============================================================

Use "fallback" when:

- The question is unrelated to the six supported modules.
- The question is too unclear to safely identify a module.
- The question cannot be resolved from the supplied conversation context.

============================================================
CONVERSATION CONTEXT
============================================================

There are four possible sources of context:

A. CURRENT SCREEN MODULE

The business module screen from which the chatbot was opened.

B. SELECTED MODULE

The module explicitly selected by the user through a chatbot button.

C. ACTIVE CONVERSATION MODULE

The module currently associated with this conversation.

D. RECENT CONVERSATION HISTORY

Recent user and assistant messages from THIS conversation only.

IMPORTANT:

- Use conversation history only to understand references in the CURRENT question.
- Previous assistant answers are NOT current report data.
- Never treat old numbers, counts, records, or report results as current data.
- The selected business agent will fetch fresh report data for the current request.
- Do not carry conversation history between different conversation IDs.

============================================================
ROUTING PRIORITY
============================================================

Use this priority:

1. CURRENT USER QUESTION
2. SELECTED MODULE
3. ACTIVE CONVERSATION MODULE / RECENT CONVERSATION
4. CURRENT SCREEN MODULE
5. FALLBACK

The current user's explicit question always has the highest priority.

If the current question clearly belongs to another supported module,
switch to that module even if the previous conversation, selected
module, or current screen belongs to another module.

For follow-up questions such as:

- "How many were there?"
- "How many were cancelled?"
- "List them."
- "Show the closed ones."
- "What about last month?"
- "What about the previous month?"
- "How much was collected?"

use the recent conversation context to determine what the user is
referring to.

============================================================
QUESTION REWRITING
============================================================

Return "rewritten_question".

The rewritten question must:

- Preserve the current user's intent.
- Be self-contained when context is required.
- Resolve references such as "there", "them", "those", "it",
  "the first one", "last month", etc. using the conversation context.
- Preserve reporting periods already established in the conversation
  unless the current question changes them.
- Preserve the current business subject unless the user changes it.
- Never invent facts.
- Never invent report values.
- Never answer the question.
- Never add an unrelated subject.
- Never use previous report values as current values.

When the current question is already self-contained, return it
essentially unchanged.

============================================================
EXAMPLE 1: FOLLOW-UP MODULE CONTEXT
============================================================

Previous conversation:

USER:
Show me visitors for the last 3 months.

USER:
How many were delivery visitors?

Return:

{{
    "module": "visitor",
    "confidence": 0.99,
    "reason": "The current question continues the Visitor Management conversation.",
    "rewritten_question": "How many delivery visitors were there in the last 3 months?"
}}

============================================================
EXAMPLE 2: FOLLOW-UP DATE CHANGE
============================================================

Previous conversation:

USER:
How many visitors were there in the last 3 months?

USER:
What about last month?

Return:

{{
    "module": "visitor",
    "confidence": 0.99,
    "reason": "The user is changing the reporting period for the current Visitor question.",
    "rewritten_question": "How many visitors were there last month?"
}}

============================================================
EXAMPLE 3: KEY COLLECTION FOLLOW-UP
============================================================

Previous conversation:

USER:
Show me key collections for the last 3 months.

USER:
How many were cancelled?

Return:

{{
    "module": "key_collection",
    "confidence": 0.99,
    "reason": "The user is asking about cancelled key collections in the existing conversation.",
    "rewritten_question": "How many key collections were cancelled in the last 3 months?"
}}

============================================================
EXAMPLE 4: MODULE SWITCH
============================================================

Previous conversation:

USER:
Show me visitors for the last 3 months.

CURRENT QUESTION:

Show me financial reports.

Return:

{{
    "module": "financial",
    "confidence": 0.99,
    "reason": "The current question explicitly changes the subject to Financial Reports.",
    "rewritten_question": "Show me financial reports."
}}

============================================================
EXAMPLE 5: SCREEN MODULE MUST NOT OVERRIDE QUESTION
============================================================

Current screen:

feedback

Selected module:

feedback

Question:

Show me key collections for the last 3 months.

Return:

{{
    "module": "key_collection",
    "confidence": 0.99,
    "reason": "The current question is explicitly about key collections.",
    "rewritten_question": "Show me key collections for the last 3 months."
}}

============================================================
EXAMPLE 6: SELECTED MODULE
============================================================

Current screen:

feedback

Selected module:

visitor

Question:

How many visitors came last month?

Return:

{{
    "module": "visitor",
    "confidence": 0.99,
    "reason": "The current question is about Visitor Management.",
    "rewritten_question": "How many visitors came last month?"
}}

============================================================
EXAMPLE 7: FINANCIAL
============================================================

Current screen:

feedback

Selected module:

visitor

Question:

How much was collected this month?

Return:

{{
    "module": "financial",
    "confidence": 0.97,
    "reason": "The current question asks about financial collections.",
    "rewritten_question": "How much was collected this month?"
}}

============================================================
EXAMPLE 8: UNRELATED QUESTION
============================================================

Current screen:

financial

Selected module:

financial

Question:

What is the weather today?

Return:

{{
    "module": "fallback",
    "confidence": 0.99,
    "reason": "The question is unrelated to the supported Property Management modules.",
    "rewritten_question": "What is the weather today?"
}}

============================================================
EXAMPLE 9: UNCLEAR QUESTION WITH NO HISTORY
============================================================

Current screen:

feedback

Selected module:

feedback

Question:

Show me the latest report.

Return:

{{
    "module": "fallback",
    "confidence": 0.70,
    "reason": "The question is too unclear to identify a specific supported module.",
    "rewritten_question": "Show me the latest report."
}}

============================================================
ROUTING RULES
============================================================

- Select exactly ONE module.
- Allowed modules are:
  feedback
  facilities
  visitor
  financial
  key_collection
  defect
  fallback

- Never answer the user's question.
- Never invent a module.
- Never select a module outside the allowed list.
- Never use security.
- The current user's explicit question overrides all other context.
- A clear module mention in the current question takes priority.
- If the current question is a follow-up, use the conversation history.
- Use the active conversation module when a follow-up does not explicitly
  identify a new module and history supports that module.
- Use the selected module when the current question clearly belongs to it.
- Use the screen module only when the question does not identify a
  different module and no stronger conversation context applies.
- Use fallback when the question is unrelated or cannot safely be resolved.
- Confidence must be between 0.0 and 1.0.
- Keep the reason short.
- Return ONLY valid JSON.
- Do not return markdown.
- Do not return code fences.
- Do not return additional text.

============================================================
CURRENT SCREEN MODULE
============================================================

{screen_module}

============================================================
SELECTED MODULE
============================================================

{selected_module}

============================================================
ACTIVE CONVERSATION MODULE
============================================================

{active_module}

============================================================
CONVERSATION CONTEXT
============================================================

{conversation_context}

============================================================
CURRENT USER QUESTION
============================================================

{question}

============================================================
REQUIRED JSON
============================================================

{{
    "module": "module_name",
    "confidence": 0.0,
    "reason": "short reason",
    "rewritten_question": "self-contained current question"
}}
"""


# ============================================================
# Normalize Module
# ============================================================

def normalize_module(
    module: Optional[str],
) -> Optional[str]:
    """
    Normalize a module value into the canonical module name.

    Main/Dashboard/Home are treated as having no active module.
    """

    if module is None:
        return None

    value = str(
        module
    ).strip().lower()

    if value in NO_MODULE_CONTEXTS:
        return None

    return MODULE_ALIASES.get(value)


# ============================================================
# Clean Router Response
# ============================================================

def _clean_router_response(
    response: str,
) -> str:
    """
    Remove markdown code fences and surrounding whitespace.
    """

    if not isinstance(response, str):
        raise ValueError(
            "Router response must be a string."
        )

    cleaned = response.strip()

    # Remove opening ```json or ```
    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    # Remove closing ```
    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned,
    )

    return cleaned.strip()


# ============================================================
# Extract JSON Object
# ============================================================

def _extract_json_object(
    text: str,
) -> dict:
    """
    Parse a JSON object from the LLM response.

    Handles responses where the model accidentally returns
    surrounding text.
    """

    # --------------------------------------------------------
    # Try direct JSON first
    # --------------------------------------------------------

    try:
        result = json.loads(text)

        if isinstance(result, dict):
            return result

    except json.JSONDecodeError:
        pass

    # --------------------------------------------------------
    # Try extracting JSON from surrounding text
    # --------------------------------------------------------

    match = re.search(
        r"\{.*\}",
        text,
        flags=re.DOTALL,
    )

    if not match:
        raise ValueError(
            "Router returned invalid JSON."
        )

    json_text = match.group(0)

    try:
        result = json.loads(
            json_text
        )

    except json.JSONDecodeError as ex:
        raise ValueError(
            "Router returned invalid JSON: "
            f"{str(ex)}"
        ) from ex

    if not isinstance(result, dict):
        raise ValueError(
            "Router JSON response must be an object."
        )

    return result


# ============================================================
# Parse Router Response
# ============================================================

def parse_router_response(
    response: str,
) -> dict:
    """
    Parse and validate the router response.

    Returns:

    {
        "module": "...",
        "confidence": 0.0,
        "reason": "...",
        "rewritten_question": "..."
    }
    """

    cleaned = _clean_router_response(
        response
    )

    result = _extract_json_object(
        cleaned
    )

    # --------------------------------------------------------
    # Required fields
    # --------------------------------------------------------

    required_fields = {
        "module",
        "confidence",
        "reason",
    }

    missing_fields = (
        required_fields
        - set(result.keys())
    )

    if missing_fields:
        raise ValueError(
            "Router response is missing required fields: "
            + ", ".join(
                sorted(missing_fields)
            )
        )

    # --------------------------------------------------------
    # Module
    # --------------------------------------------------------

    raw_module = result.get(
        "module"
    )

    module = normalize_module(
        raw_module
    )

    if module not in ALLOWED_MODULES:
        raise ValueError(
            f"Router selected invalid module: {raw_module}"
        )

    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    raw_confidence = result.get(
        "confidence"
    )

    try:
        confidence = float(
            raw_confidence
        )

    except (TypeError, ValueError) as ex:
        raise ValueError(
            "Router returned invalid confidence: "
            f"{raw_confidence}"
        ) from ex

    if not 0.0 <= confidence <= 1.0:
        raise ValueError(
            "Router confidence must be between 0.0 and 1.0: "
            f"{confidence}"
        )

    # --------------------------------------------------------
    # Reason
    # --------------------------------------------------------

    reason = result.get(
        "reason"
    )

    if reason is None:
        reason = ""

    reason = str(
        reason
    ).strip()

    if not reason:
        reason = (
            "Module selected based on the current question "
            "and available conversation context."
        )

    # --------------------------------------------------------
    # Rewritten Question
    # --------------------------------------------------------

    rewritten_question = result.get(
        "rewritten_question"
    )

    if rewritten_question is None:
        rewritten_question = ""

    rewritten_question = str(
        rewritten_question
    ).strip()

    # --------------------------------------------------------
    # Return canonical response
    # --------------------------------------------------------

    return {
        "module": module,
        "confidence": round(
            confidence,
            4,
        ),
        "reason": reason,
        "rewritten_question": rewritten_question,
    }


# ============================================================
# Module Router
# ============================================================

def route_question(
    question: str,
    screen_module: Optional[str] = None,
    selected_module: Optional[str] = None,
    conversation_history: Optional[
        List[Dict[str, Any]]
    ] = None,
    conversation_summary: Optional[str] = None,
    active_module: Optional[str] = None,
) -> dict:
    """
    Route the current user question to the correct module.

    Routing priority:

        Current User Question
                ↓
        Selected Module
                ↓
        Active Conversation / History
                ↓
        Current Screen
                ↓
        Fallback

    Conversation history is used to resolve follow-up questions.
    """

    # --------------------------------------------------------
    # Validate question
    # --------------------------------------------------------

    if question is None:
        raise ValueError(
            "Question is required for module routing."
        )

    question = str(
        question
    ).strip()

    if not question:
        raise ValueError(
            "Question cannot be empty for module routing."
        )

    # --------------------------------------------------------
    # Normalize screen module
    # --------------------------------------------------------

    normalized_screen_module = normalize_module(
        screen_module
    )

    # --------------------------------------------------------
    # Normalize selected module
    # --------------------------------------------------------

    normalized_selected_module = normalize_module(
        selected_module
    )

    # --------------------------------------------------------
    # Normalize active conversation module
    # --------------------------------------------------------

    normalized_active_module = normalize_module(
        active_module
    )

    # --------------------------------------------------------
    # Warn about invalid screen module
    # --------------------------------------------------------

    if (
        screen_module is not None
        and str(screen_module).strip().lower()
        not in NO_MODULE_CONTEXTS
        and normalized_screen_module is None
    ):
        logger.warning(
            "Unknown screen module received: %s",
            screen_module,
        )

    # --------------------------------------------------------
    # Warn about invalid selected module
    # --------------------------------------------------------

    if (
        selected_module is not None
        and str(selected_module).strip().lower()
        not in NO_MODULE_CONTEXTS
        and normalized_selected_module is None
    ):
        logger.warning(
            "Unknown selected module received: %s",
            selected_module,
        )

    # --------------------------------------------------------
    # Warn about invalid active module
    # --------------------------------------------------------

    if (
        active_module is not None
        and str(active_module).strip().lower()
        not in NO_MODULE_CONTEXTS
        and normalized_active_module is None
    ):
        logger.warning(
            "Unknown active conversation module received: %s",
            active_module,
        )

    # --------------------------------------------------------
    # Context values sent to prompt
    # --------------------------------------------------------

    screen_context = (
        normalized_screen_module
        if normalized_screen_module
        else "none"
    )

    selected_context = (
        normalized_selected_module
        if normalized_selected_module
        else "none"
    )

    active_context = (
        normalized_active_module
        if normalized_active_module
        else "none"
    )

    # --------------------------------------------------------
    # Format conversation history
    # --------------------------------------------------------

    conversation_context = _format_conversation_history(
        conversation_history=conversation_history,
        conversation_summary=conversation_summary,
        active_module=(
            normalized_active_module
            if normalized_active_module
            else None
        ),
    )

    # --------------------------------------------------------
    # Build router prompt
    # --------------------------------------------------------

    prompt = ROUTER_PROMPT.format(
        screen_module=screen_context,
        selected_module=selected_context,
        active_module=active_context,
        conversation_context=conversation_context,
        question=question,
    )

    logger.info(
        "Running module router | "
        "screen=%s | "
        "selected=%s | "
        "active=%s | "
        "history_messages=%s | "
        "question=%s",
        screen_context,
        selected_context,
        active_context,
        len(conversation_history or []),
        question,
    )

    # --------------------------------------------------------
    # Call Gemini
    # --------------------------------------------------------

    try:
        response = generate(
            prompt
        )

    except Exception as ex:
        logger.exception(
            "Module router LLM call failed"
        )

        raise RuntimeError(
            "Module router LLM call failed: "
            f"{str(ex)}"
        ) from ex

    # --------------------------------------------------------
    # Parse router response
    # --------------------------------------------------------

    try:
        result = parse_router_response(
            response
        )

    except Exception as ex:
        logger.exception(
            "Module router response parsing failed | response=%s",
            response,
        )

        raise RuntimeError(
            "Module router response parsing failed: "
            f"{str(ex)}"
        ) from ex

    # --------------------------------------------------------
    # Fallback rewritten question
    # --------------------------------------------------------

    if not result.get(
        "rewritten_question"
    ):
        result["rewritten_question"] = question

    # --------------------------------------------------------
    # Log result
    # --------------------------------------------------------

    logger.info(
        "Router selected module=%s "
        "confidence=%.4f "
        "reason=%s "
        "rewritten_question=%s",
        result["module"],
        result["confidence"],
        result["reason"],
        result["rewritten_question"],
    )

    return result