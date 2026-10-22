import logging

import re

from datetime import date, timedelta

from services.reports.key_collection_report import (

    KeyCollectionReportService

)

from services.analytics.key_collection_analyzer import (

    KeyCollectionAnalyzer

)

from services.llm.prompt_builder import (

    PromptBuilder

)

from services.llm.gemini_client import (

    generate

)

from services.llm.llm_response_parser import (

    LLMResponseParser

)

logger = logging.getLogger(__name__)

# ============================================================

# Date Helpers

# ============================================================

MONTHS = {

    "january": 1,

    "february": 2,

    "march": 3,

    "april": 4,

    "may": 5,

    "june": 6,

    "july": 7,

    "august": 8,

    "september": 9,

    "october": 10,

    "november": 11,

    "december": 12,

}

def first_day_of_month(year, month):

    return date(

        year,

        month,

        1

    )

def last_day_of_month(year, month):

    if month == 12:

        next_month = date(

            year + 1,

            1,

            1

        )

    else:

        next_month = date(

            year,

            month + 1,

            1

        )

    return next_month - timedelta(

        days=1

    )

def subtract_months(

    year,

    month,

    months

):

    total_months = (

        year * 12

        + (month - 1)

        - months

    )

    new_year = total_months // 12

    new_month = (

        total_months % 12

    ) + 1

    return (

        new_year,

        new_month

    )

def format_date(value):

    return value.strftime(

        "%Y-%m-%d"

    )

# ============================================================

# Extract Date Range

# ============================================================

def extract_date_range(question):

    question_lower = (

        question

        .lower()

        .strip()

    )

    today = date.today()

    # ========================================================

    # This Month

    # ========================================================

    if re.search(

        r"\bthis\s+month\b",

        question_lower

    ):

        start_date = first_day_of_month(

            today.year,

            today.month

        )

        end_date = today

        return (

            format_date(start_date),

            format_date(end_date)

        )

    # ========================================================

    # Last / Previous Month

    # ========================================================

    if re.search(

        r"\b(last|previous)\s+month\b",

        question_lower

    ):

        year, month = subtract_months(

            today.year,

            today.month,

            1

        )

        start_date = first_day_of_month(

            year,

            month

        )

        end_date = last_day_of_month(

            year,

            month

        )

        return (

            format_date(start_date),

            format_date(end_date)

        )

    # ========================================================

    # Last / Past / Previous N Months

    # ========================================================

    months_match = re.search(

        r"\b(last|past|previous)\s+"

        r"(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)"

        r"\s+months?\b",

        question_lower

    )

    if months_match:

        value = months_match.group(2)

        number_words = {

            "one": 1,

            "two": 2,

            "three": 3,

            "four": 4,

            "five": 5,

            "six": 6,

            "seven": 7,

            "eight": 8,

            "nine": 9,

            "ten": 10,

            "eleven": 11,

            "twelve": 12

        }

        if value.isdigit():

            months_count = int(value)

        else:

            months_count = number_words[value]

        if 1 <= months_count <= 12:

            start_year, start_month = subtract_months(

                today.year,

                today.month,

                months_count

            )

            end_year, end_month = subtract_months(

                today.year,

                today.month,

                1

            )

            start_date = first_day_of_month(

                start_year,

                start_month

            )

            end_date = last_day_of_month(

                end_year,

                end_month

            )

            return (

                format_date(start_date),

                format_date(end_date)

            )

    # ========================================================

    # This Year

    # ========================================================

    if re.search(

        r"\bthis\s+year\b",

        question_lower

    ):

        start_date = date(

            today.year,

            1,

            1

        )

        end_date = today

        return (

            format_date(start_date),

            format_date(end_date)

        )

    # ========================================================

    # Last / Previous Year

    # ========================================================

    if re.search(

        r"\b(last|previous)\s+year\b",

        question_lower

    ):

        year = today.year - 1

        start_date = date(

            year,

            1,

            1

        )

        end_date = date(

            year,

            12,

            31

        )

        return (

            format_date(start_date),

            format_date(end_date)

        )

    # ========================================================

    # This Week

    # ========================================================

    if re.search(

        r"\bthis\s+week\b",

        question_lower

    ):

        start_date = (

            today

            - timedelta(

                days=today.weekday()

            )

        )

        end_date = today

        return (

            format_date(start_date),

            format_date(end_date)

        )

    # ========================================================

    # Last / Previous Week

    # ========================================================

    if re.search(

        r"\b(last|previous)\s+week\b",

        question_lower

    ):

        current_week_start = (

            today

            - timedelta(

                days=today.weekday()

            )

        )

        start_date = (

            current_week_start

            - timedelta(days=7)

        )

        end_date = (

            current_week_start

            - timedelta(days=1)

        )

        return (

            format_date(start_date),

            format_date(end_date)

        )

    # ========================================================

    # Explicit Date Range

    #

    # Examples:

    # April 6, 2026 to September 7, 2026

    # April 6, 2026 until September 7, 2026

    # April 6, 2026 - September 7, 2026

    # ========================================================

    date_pattern = (

        r"(January|February|March|April|May|June|July|August|"

        r"September|October|November|December)"

        r"\s+(\d{1,2}),?\s+(\d{4})"

    )

    range_pattern = (

        date_pattern

        + r"\s*(?:to|until|-)\s*"

        + date_pattern

    )

    range_match = re.search(

        range_pattern,

        question,

        re.IGNORECASE

    )

    if range_match:

        start_month = MONTHS[

            range_match.group(1).lower()

        ]

        start_day = int(

            range_match.group(2)

        )

        start_year = int(

            range_match.group(3)

        )

        end_month = MONTHS[

            range_match.group(4).lower()

        ]

        end_day = int(

            range_match.group(5)

        )

        end_year = int(

            range_match.group(6)

        )

        start_date = date(

            start_year,

            start_month,

            start_day

        )

        end_date = date(

            end_year,

            end_month,

            end_day

        )

        return (

            format_date(start_date),

            format_date(end_date)

        )

    # ========================================================

    # Specific Month + Year

    #

    # Example:

    # September 2026

    # ========================================================

    month_year_match = re.search(

        r"\b("

        r"January|February|March|April|May|June|July|August|"

        r"September|October|November|December"

        r")\s+(\d{4})\b",

        question,

        re.IGNORECASE

    )

    if month_year_match:

        month = MONTHS[

            month_year_match.group(1).lower()

        ]

        year = int(

            month_year_match.group(2)

        )

        start_date = first_day_of_month(

            year,

            month

        )

        end_date = last_day_of_month(

            year,

            month

        )

        return (

            format_date(start_date),

            format_date(end_date)

        )

    # ========================================================

    # No Date

    # ========================================================

    return None, None

# ============================================================

# Key Collection Node

# ============================================================

# ============================================================
# Key Collection Pagination Helpers
# ============================================================

DEFAULT_KEY_PAGE_SIZE = 5
MAX_KEY_PAGE_SIZE = 50


def _key_history_text(item):
    if not isinstance(item, dict):
        return "", ""
    role = str(item.get("role") or item.get("type") or "").strip().lower()
    content = item.get("content") or item.get("message") or item.get("text") or item.get("answer") or ""
    if isinstance(content, list):
        content = " ".join(
            str(part.get("text") or part.get("content") or "") if isinstance(part, dict) else str(part)
            for part in content
        )
    return role, str(content)


def _key_page_size(question):
    patterns = (
        r"\bnext\s+(\d+)\b",
        r"\b(?:show|display|get|list)\s+(?:me\s+)?(\d+)\b",
        r"\b(\d+)\s+(?:key\s+collection\s+)?(?:records|items)\b",
    )
    for pattern in patterns:
        match = re.search(pattern, str(question or ""), re.IGNORECASE)
        if match:
            return max(1, min(int(match.group(1)), MAX_KEY_PAGE_SIZE))
    return DEFAULT_KEY_PAGE_SIZE


def _key_previous_page(history):
    pattern = re.compile(
        r"Showing\s+(?:key\s+collection\s+)?records\s+(\d+)-(\d+)\s+of\s+(\d+)",
        re.IGNORECASE,
    )
    for item in reversed(history or []):
        role, content = _key_history_text(item)
        if role not in {"assistant", "ai", "bot"}:
            continue
        match = pattern.search(content)
        if match:
            return int(match.group(1)), int(match.group(2)), int(match.group(3))
    return 0, 0, 0


def _key_list_request(question):
    value = str(question or "").lower()
    asks_to_list = re.search(r"\b(show|list|display|get|next|more|continue|remaining|all)\b", value)
    refers_to_records = re.search(r"\b(key|collection|record|item|ones|them)\b|\b(next|more|continue|remaining)\b", value)
    return bool(asks_to_list and refers_to_records)


def _prepare_key_collection_page(analytics, question, history):
    """Paginate a record list while preserving the remaining analytics fields."""
    prompt_data = dict(analytics)
    candidates = []
    for key, value in analytics.items():
        if not isinstance(value, list) or not value or not all(isinstance(item, dict) for item in value):
            continue
        key_lower = str(key).lower()
        score = 0
        if "record" in key_lower:
            score += 5
        if "key_collection" in key_lower or "keycollection" in key_lower:
            score += 8
        elif "collection" in key_lower or "key" in key_lower:
            score += 3
        if score:
            candidates.append((score, key, value))

    if not candidates or not _key_list_request(question):
        return prompt_data, None, None

    _, record_key, records = max(candidates, key=lambda item: item[0])
    total = len(records)
    _, previous_end, previous_total = _key_previous_page(history)
    is_next = bool(re.search(r"\b(next|more|continue|remaining)\b", str(question or ""), re.IGNORECASE))
    page_size = _key_page_size(question)
    start = min(previous_end, total) if is_next and previous_total == total and previous_end > 0 else 0
    end = min(start + page_size, total)
    selected = records[start:end]

    prompt_data[record_key] = selected
    prompt_data["key_collection_records_preview"] = selected
    pagination = {
        "start": start + 1 if selected else 0,
        "end": end,
        "total": total,
        "remaining": max(0, total - end),
        "has_next": end < total,
    }
    prompt_data["key_collection_pagination"] = pagination
    footer = (
        f"Showing key collection records {start + 1}-{end} of {total}."
        if selected else "No key collection records were found."
    )
    return prompt_data, footer, pagination


def key_collection_node(state):

    try:

        login_id = state.get(

            "login_id"

        )

        property_id = state.get(

            "property_id"

        )

        question = state.get(

            "question"

        )

        authorization = state.get(

            "authorization"

        )
        conversation_history = state.get("conversation_history") or []
        original_question = str(state.get("original_question") or question or "").strip()

        # ----------------------------------

        # Validation

        # ----------------------------------

        if not login_id:

            raise Exception(

                "login_id is required."

            )

        if not property_id:

            raise Exception(

                "property_id is required."

            )

        if not authorization:

            raise Exception(

                "Authorization token is required."

            )

        if not question:

            raise Exception(

                "Question is required."

            )

        # ----------------------------------

        # Simple Greeting

        # ----------------------------------

        greeting = question.strip().lower()

        if greeting in [

            "hi",

            "hello",

            "hey",

            "hi there",

            "hello there"

        ]:

            state["answer"] = (

                "Hi! How can I help you with Key Collection?"

            )

            return state

        # ----------------------------------

        # Extract Date Range

        # ----------------------------------

        start_date, end_date = extract_date_range(

            question

        )

        print("=" * 80)

        print("KEY COLLECTION DATE RANGE")

        print("=" * 80)

        print(

            "Start Date:",

            start_date

        )

        print(

            "End Date  :",

            end_date

        )

        print("=" * 80)

        # ----------------------------------

        # Get Key Collection Data

        # ----------------------------------

        report_data = (

            KeyCollectionReportService()

            .get_report(

                login_id=login_id,

                property_id=property_id,

                authorization=authorization,

                start_date=start_date,

                end_date=end_date

            )

        )

        # ----------------------------------

        # Add Reporting Period

        # ----------------------------------

        report_data["reporting_period"] = {

            "start_date": start_date,

            "end_date": end_date

        }

        # ----------------------------------

        # Convert Raw Data -> Analytics

        # ----------------------------------

        analytics = (

            KeyCollectionAnalyzer()

            .analyze(

                report_data

            )

        )

        # ----------------------------------

        # Add Reporting Period to Analytics

        # ----------------------------------

        analytics["reporting_period"] = {

            "start_date": start_date,

            "end_date": end_date

        }

        # ----------------------------------

        # Build Prompt

        # ----------------------------------

        pagination_question = " ".join(
            part for part in (str(question or ""), original_question) if part
        )
        analytics_for_prompt, pagination_footer, pagination = _prepare_key_collection_page(
            analytics=analytics,
            question=pagination_question,
            history=conversation_history,
        )

        prompt = (
            PromptBuilder()
            .build_key_collection_chat_prompt(
                report_data=analytics_for_prompt,
                question=question
            )
        )

        print("=" * 80)

        print("KEY COLLECTION CHAT PROMPT")

        print("=" * 80)

        print(prompt)

        print("=" * 80)

        # ----------------------------------

        # Gemini Response

        # ----------------------------------

        llm_response = generate(

            prompt

        )

        print("=" * 80)

        print("KEY COLLECTION GEMINI RESPONSE")

        print("=" * 80)

        print(llm_response)

        print("=" * 80)

        # ----------------------------------

        # Parse Response

        # ----------------------------------

        answer = (
            LLMResponseParser()
            .parse_text(llm_response)
        )

        # Hide the next-page suggestion when the current page is the last page.
        if pagination is not None and not pagination.get("has_next", False):
            answer = re.sub(
                r"(?im)^.*next\s+\d+\s+(?:key\s+collection\s+)?(?:records|items).*?(?:\n|$)",
                "",
                answer,
            ).strip()

        if pagination_footer:
            answer = f"{answer.rstrip()}\n\n{pagination_footer}"

        print("=" * 80)

        print("KEY COLLECTION ANSWER")

        print("=" * 80)

        print(answer)

        print("=" * 80)

        state["answer"] = answer

        return state

    except Exception as ex:

        logger.exception(

            "Key Collection Agent Failed"

        )

        state["answer"] = (

            f"Unable to process key collection question: "

            f"{str(ex)}"

        )

        return state
