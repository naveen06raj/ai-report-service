import json
import logging
import re
from typing import Optional

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
# Router Prompt
# ============================================================

ROUTER_PROMPT = """
You are the module routing agent for a production Property Management AI system.

Your ONLY job is to determine which module should handle the user's question.

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
- The question does not contain enough information for routing.

============================================================
CHATBOT CONTEXT
============================================================

The chatbot can have three kinds of context:

A. CURRENT SCREEN MODULE

This is the module screen from which the chatbot was opened.

Examples:

feedback
facilities
visitor
financial
key_collection
defect

The value may also be "none" when the chatbot was opened from
the Main/Dashboard screen.

------------------------------------------------------------

B. SELECTED MODULE

This is the module explicitly selected by the user through a
chatbot option/button.

It may be "none" when the user has not selected a module.

------------------------------------------------------------

C. USER QUESTION

This is the actual question typed by the user.

============================================================
ROUTING PRIORITY
============================================================

Use this priority:

1. USER QUESTION
2. SELECTED MODULE
3. CURRENT SCREEN MODULE
4. FALLBACK

The user's actual question has the highest priority.

If the question clearly belongs to a different module than the
current screen or selected module, route to the module identified
by the question.

Do NOT force the question to the current screen module.

============================================================
EXAMPLES
============================================================

Example 1

Current screen:
feedback

Selected module:
feedback

Question:
"How many complaints did we receive this month?"

Return:
{{"module":"feedback","confidence":0.98,"reason":"The user is asking about resident complaints and feedback."}}

------------------------------------------------------------

Example 2

Current screen:
feedback

Selected module:
feedback

Question:
"Show me key collections for the last 3 months."

Return:
{{"module":"key_collection","confidence":0.99,"reason":"The question is explicitly about key collections."}}

Do NOT select feedback because the user is currently on the
Feedback screen.

------------------------------------------------------------

Example 3

Current screen:
feedback

Selected module:
visitor

Question:
"Show me visitors this month."

Return:
{{"module":"visitor","confidence":0.99,"reason":"The user is asking about visitor records."}}

------------------------------------------------------------

Example 4

Current screen:
feedback

Selected module:
visitor

Question:
"How much was collected this month?"

Return:
{{"module":"financial","confidence":0.97,"reason":"The question is asking about financial collection amounts."}}

The question overrides the selected Visitor module.

------------------------------------------------------------

Example 5

Current screen:
main

Selected module:
none

Question:
"Show me open defects."

Return:
{{"module":"defect","confidence":0.99,"reason":"The user is asking about defects and their status."}}

------------------------------------------------------------

Example 6

Current screen:
main

Selected module:
none

Question:
"Show me financial collections this month."

Return:
{{"module":"financial","confidence":0.99,"reason":"The question is asking about financial collections."}}

------------------------------------------------------------

Example 7

Current screen:
financial

Selected module:
financial

Question:
"What is the weather today?"

Return:
{{"module":"fallback","confidence":0.99,"reason":"The question is unrelated to the supported Property Management modules."}}

------------------------------------------------------------

Example 8

Current screen:
feedback

Selected module:
feedback

Question:
"Show me the latest report."

Return:
{{"module":"fallback","confidence":0.70,"reason":"The question is too unclear to safely identify a specific module."}}

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
- If the question explicitly identifies another supported module,
  route to that module.
- The user's actual question overrides the selected module when
  the question clearly belongs to another module.
- If the question clearly belongs to the selected module, use it.
- If there is no selected module and the question clearly belongs
  to the current screen module, use the current screen module.
- If the current screen is Main/Dashboard and no module is selected,
  use the user's question to determine the module.
- Use fallback when the question is unrelated or ambiguous.
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
USER QUESTION
============================================================

{question}

============================================================
REQUIRED JSON
============================================================

{{
    "module": "module_name",
    "confidence": 0.0,
    "reason": "short reason"
}}
"""


# ============================================================
# Normalize Module
# ============================================================

def normalize_module(module: Optional[str]) -> Optional[str]:
    """
    Normalize a module value into the canonical module name.

    Main/Dashboard/Home are treated as having no active module.
    """

    if module is None:
        return None

    value = str(module).strip().lower()

    if value in NO_MODULE_CONTEXTS:
        return None

    return MODULE_ALIASES.get(value)


# ============================================================
# Clean Router Response
# ============================================================

def _clean_router_response(response: str) -> str:
    """
    Remove markdown code fences and surrounding whitespace.
    """

    if not isinstance(response, str):
        raise ValueError(
            "Router response must be a string."
        )

    cleaned = response.strip()

    # Opening code fence
    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    # Closing code fence
    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned,
    )

    return cleaned.strip()


# ============================================================
# Extract JSON Object
# ============================================================

def _extract_json_object(text: str) -> dict:
    """
    Parse a JSON object from the LLM response.

    Handles cases where the model accidentally returns
    additional text around the JSON.
    """

    try:
        result = json.loads(text)

        if isinstance(result, dict):
            return result

    except json.JSONDecodeError:
        pass

    # Try extracting JSON object from surrounding text
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
        result = json.loads(json_text)
    except json.JSONDecodeError as ex:
        raise ValueError(
            f"Router returned invalid JSON: {str(ex)}"
        ) from ex

    if not isinstance(result, dict):
        raise ValueError(
            "Router JSON response must be an object."
        )

    return result


# ============================================================
# Parse Router Response
# ============================================================

def parse_router_response(response: str) -> dict:
    """
    Parse and validate the router response.

    Returns exactly:

    {
        "module": "...",
        "confidence": 0.0,
        "reason": "..."
    }
    """

    cleaned = _clean_router_response(response)

    result = _extract_json_object(cleaned)

    # --------------------------------------------------------
    # Required fields
    # --------------------------------------------------------

    required_fields = {
        "module",
        "confidence",
        "reason",
    }

    missing_fields = required_fields - set(result.keys())

    if missing_fields:
        raise ValueError(
            "Router response is missing required fields: "
            + ", ".join(sorted(missing_fields))
        )

    # --------------------------------------------------------
    # Module
    # --------------------------------------------------------

    raw_module = result.get("module")

    module = normalize_module(raw_module)

    if module not in ALLOWED_MODULES:
        raise ValueError(
            f"Router selected invalid module: {raw_module}"
        )

    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    raw_confidence = result.get("confidence")

    try:
        confidence = float(raw_confidence)
    except (TypeError, ValueError) as ex:
        raise ValueError(
            f"Router returned invalid confidence: {raw_confidence}"
        ) from ex

    if not 0.0 <= confidence <= 1.0:
        raise ValueError(
            f"Router confidence must be between 0.0 and 1.0: "
            f"{confidence}"
        )

    # --------------------------------------------------------
    # Reason
    # --------------------------------------------------------

    reason = result.get("reason")

    if reason is None:
        reason = ""

    reason = str(reason).strip()

    if not reason:
        reason = "Module selected based on the user question."

    # --------------------------------------------------------
    # Return canonical response
    # --------------------------------------------------------

    return {
        "module": module,
        "confidence": round(confidence, 4),
        "reason": reason,
    }


# ============================================================
# Module Router
# ============================================================

def route_question(
    question: str,
    screen_module: Optional[str] = None,
    selected_module: Optional[str] = None,
) -> dict:
    """
    Route the user's question to the correct module.

    Priority:

        User Question
            ↓
        Selected Module
            ↓
        Current Screen
            ↓
        Fallback

    Parameters
    ----------
    question:
        Actual user question.

    screen_module:
        Module of the screen where the chatbot was opened.

    selected_module:
        Module explicitly selected by the user.
    """

    # --------------------------------------------------------
    # Validate question
    # --------------------------------------------------------

    if question is None:
        raise ValueError(
            "Question is required for module routing."
        )

    question = str(question).strip()

    if not question:
        raise ValueError(
            "Question cannot be empty for module routing."
        )

    # --------------------------------------------------------
    # Normalize screen context
    # --------------------------------------------------------

    normalized_screen_module = normalize_module(
        screen_module
    )

    # --------------------------------------------------------
    # Normalize selected context
    # --------------------------------------------------------

    normalized_selected_module = normalize_module(
        selected_module
    )

    # --------------------------------------------------------
    # Warn only when a real value is invalid
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
    # Context values sent to the prompt
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

    # --------------------------------------------------------
    # Build router prompt
    # --------------------------------------------------------

    prompt = ROUTER_PROMPT.format(
        screen_module=screen_context,
        selected_module=selected_context,
        question=question,
    )

    logger.info(
        "Running module router | screen=%s | selected=%s | question=%s",
        screen_context,
        selected_context,
        question,
    )

    # --------------------------------------------------------
    # Call Gemini
    # --------------------------------------------------------

    try:
        response = generate(prompt)

    except Exception as ex:
        logger.exception(
            "Module router LLM call failed"
        )

        raise RuntimeError(
            f"Module router LLM call failed: {str(ex)}"
        ) from ex

    # --------------------------------------------------------
    # Parse router response
    # --------------------------------------------------------

    try:
        result = parse_router_response(response)

    except Exception as ex:
        logger.exception(
            "Module router response parsing failed | response=%s",
            response,
        )

        raise RuntimeError(
            f"Module router response parsing failed: {str(ex)}"
        ) from ex

    # --------------------------------------------------------
    # Log routing result
    # --------------------------------------------------------

    logger.info(
        "Router selected module=%s confidence=%.4f reason=%s",
        result["module"],
        result["confidence"],
        result["reason"],
    )

    return result