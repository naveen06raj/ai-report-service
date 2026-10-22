import re

import logging

from datetime import datetime, date, timedelta



from services.reports.facility_booking_report import (

    FacilityBookingReportService

)



from services.analytics.facility_booking_analyzer import (

    FacilityBookingAnalyzer

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

# Month Names

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





# ============================================================

# Date Helpers

# ============================================================



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





def subtract_months(input_date, months):



    year = input_date.year

    month = input_date.month



    total_months = (

        year * 12

        + (month - 1)

        - months

    )



    new_year = total_months // 12



    new_month = (

        total_months % 12

    ) + 1



    max_day = last_day_of_month(

        new_year,

        new_month

    ).day



    new_day = min(

        input_date.day,

        max_day

    )



    return date(

        new_year,

        new_month,

        new_day

    )





def format_date(input_date):



    return input_date.strftime(

        "%Y-%m-%d"

    )





# ============================================================

# Extract Date Range From Question

# ============================================================



def extract_date_range(question: str):



    if not question:



        return None, None



    question_lower = (

        question

        .lower()

        .strip()

    )



    today = date.today()



    # ========================================================

    # THIS MONTH

    #

    # Example:

    #

    # September 1, 2026

    # to

    # September 8, 2026

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

    # LAST / PREVIOUS MONTH

    #

    # Example:

    #

    # August 1, 2026

    # to

    # August 31, 2026

    # ========================================================



    if re.search(

        r"\b(last|previous)\s+month\b",

        question_lower

    ):



        previous_month = subtract_months(

            today,

            1

        )



        start_date = first_day_of_month(

            previous_month.year,

            previous_month.month

        )



        end_date = last_day_of_month(

            previous_month.year,

            previous_month.month

        )



        return (

            format_date(start_date),

            format_date(end_date)

        )



    # ========================================================

    # LAST N / PAST N / PREVIOUS N MONTHS

    #

    # Examples:

    #

    # last 3 months

    # past 3 months

    # previous 3 months

    # last 6 months

    # last 12 months

    #

    # These mean previous COMPLETE calendar months.

    # ========================================================



    match = re.search(

        r"\b(?:last|past|previous)\s+"

        r"(\d+|one|two|three|four|five|six|seven|eight|"

        r"nine|ten|eleven|twelve)\s+months?\b",

        question_lower

    )



    if match:



        number_text = match.group(

            1

        )



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

            "twelve": 12,

        }



        if number_text.isdigit():



            months_count = int(

                number_text

            )



        else:



            months_count = number_words.get(

                number_text

            )



        if months_count and months_count > 0:



            current_month_start = (

                first_day_of_month(

                    today.year,

                    today.month

                )

            )



            start_date = subtract_months(

                current_month_start,

                months_count

            )



            end_date = (

                current_month_start

                - timedelta(days=1)

            )



            return (

                format_date(start_date),

                format_date(end_date)

            )



    # ========================================================

    # THIS YEAR

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

    # LAST / PREVIOUS YEAR

    # ========================================================



    if re.search(

        r"\b(last|previous)\s+year\b",

        question_lower

    ):



        previous_year = (

            today.year - 1

        )



        start_date = date(

            previous_year,

            1,

            1

        )



        end_date = date(

            previous_year,

            12,

            31

        )



        return (

            format_date(start_date),

            format_date(end_date)

        )



    # ========================================================

    # THIS WEEK

    #

    # Monday -> Today

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

    # LAST / PREVIOUS WEEK

    #

    # Previous complete Monday-Sunday week.

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

    # EXPLICIT DATE RANGE

    #

    # Examples:

    #

    # April 6, 2026 to September 7, 2026

    #

    # April 6 2026 to September 7 2026

    #

    # April 6, 2026 until September 7, 2026

    #

    # April 6, 2026 - September 7, 2026

    # ========================================================



    pattern = (

        r"\b"

        r"(January|February|March|April|May|June|July|August|"

        r"September|October|November|December)"

        r"\s+"

        r"(\d{1,2})"

        r"(?:,\s*|\s+)"

        r"(\d{4})"

        r"\s+"

        r"(?:to|until|-)"

        r"\s+"

        r"(January|February|March|April|May|June|July|August|"

        r"September|October|November|December)"

        r"\s+"

        r"(\d{1,2})"

        r"(?:,\s*|\s+)"

        r"(\d{4})"

        r"\b"

    )



    match = re.search(

        pattern,

        question,

        re.IGNORECASE

    )



    if match:



        (

            start_month,

            start_day,

            start_year,

            end_month,

            end_day,

            end_year

        ) = match.groups()



        try:



            start_date = datetime.strptime(

                f"{start_month} {start_day} {start_year}",

                "%B %d %Y"

            ).date()



            end_date = datetime.strptime(

                f"{end_month} {end_day} {end_year}",

                "%B %d %Y"

            ).date()



            if start_date > end_date:



                logger.warning(

                    "Start date is after end date: %s - %s",

                    start_date,

                    end_date

                )



                return None, None



            return (

                format_date(start_date),

                format_date(end_date)

            )



        except ValueError:



            logger.warning(

                "Invalid date range found: %s",

                question

            )



            return None, None



    # ========================================================

    # SINGLE MONTH + YEAR

    #

    # Example:

    #

    # September 2026

    # August 2026

    # ========================================================



    month_year_pattern = (

        r"\b"

        r"(January|February|March|April|May|June|July|August|"

        r"September|October|November|December)"

        r"\s+"

        r"(\d{4})"

        r"\b"

    )



    month_year_match = re.search(

        month_year_pattern,

        question,

        re.IGNORECASE

    )



    if month_year_match:



        month_name = (

            month_year_match

            .group(1)

            .lower()

        )



        year = int(

            month_year_match.group(2)

        )



        month = MONTHS.get(

            month_name

        )



        if month:



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

    # NO DATE

    # ========================================================



    return None, None





# ============================================================


# ============================================================
# Facility Booking Pagination Helpers
# ============================================================
DEFAULT_FACILITY_PAGE_SIZE = 5
MAX_FACILITY_PAGE_SIZE = 50


def _history_role_and_text(item):
    if not isinstance(item, dict):
        return "", ""
    role = str(item.get("role") or item.get("type") or "").strip().lower()
    content = item.get("content") or item.get("message") or item.get("text") or item.get("answer") or ""
    if isinstance(content, list):
        content = " ".join(
            str(part.get("text") or part.get("content") or "")
            if isinstance(part, dict) else str(part)
            for part in content
        )
    return role, str(content)


def _requested_facility_page_size(question):
    q = str(question or "")
    patterns = (
        r"\bnext\s+(\d+)\b",
        r"\b(?:show|display|get|list)\s+(?:me\s+)?(\d+)\b",
        r"\b(\d+)\s+(?:facility\s+)?(?:booking|bookings|records|items)\b",
    )
    for pattern in patterns:
        match = re.search(pattern, q, re.IGNORECASE)
        if match:
            return max(1, min(int(match.group(1)), MAX_FACILITY_PAGE_SIZE))
    return DEFAULT_FACILITY_PAGE_SIZE


def _is_next_facility_page(question):
    return bool(re.search(
        r"\b(next|more|continue|remaining)\b",
        str(question or ""),
        re.IGNORECASE,
    ))


def _is_facility_list_request(question):
    q = str(question or "").lower()
    return bool(
        re.search(r"\b(show|list|display|get|find)\b.*\b(facilit(?:y|ies)|booking|bookings|reservations|records)\b", q)
        or re.search(r"\b(all|next|more)\s+(?:the\s+)?(?:facility\s+)?(?:bookings|reservations|records|items)\b", q)
        or re.search(r"\bfacility booking records\b", q)
    )


def _is_facility_context_followup(question):
    return bool(re.search(
        r"\b(next|more|continue|remaining|those|these|them|same|records|bookings|reservations)\b",
        str(question or ""),
        re.IGNORECASE,
    ))


def _find_facility_record_list(value, path=()):
    """Find a nested list of booking/reservation records in analytics or report data."""
    candidates = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key).lower().replace("_", " ")
            if isinstance(child, list) and child and all(isinstance(row, dict) for row in child):
                sample_keys = set().union(
                    *(set(str(k).lower().replace("_", " ") for k in row.keys())
                      for row in child[:5])
                )
                field_hits = sum(
                    any(term in field for field in sample_keys)
                    for term in ("booking", "facility", "reservation", "slot", "status", "start date", "end date", "user", "name")
                )
                context_hit = 6 if any(term in key_text for term in ("booking", "reservation", "facility", "records", "result", "list", "data")) else 0
                score = field_hits + context_hit
                if score >= 4:
                    candidates.append((score, path + (key,), child))
            nested = _find_facility_record_list(child, path + (key,))
            if nested:
                candidates.append(nested)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            nested = _find_facility_record_list(child, path + (index,))
            if nested:
                candidates.append(nested)
    return max(candidates, key=lambda item: item[0]) if candidates else None


def _replace_at_path(value, path, replacement):
    if not path:
        return replacement
    copied = dict(value) if isinstance(value, dict) else list(value)
    key = path[0]
    copied[key] = _replace_at_path(value[key], path[1:], replacement)
    return copied


def _previous_facility_page(conversation_history):
    pattern = re.compile(
        r"Showing\s+facility\s+booking\s+records\s+(\d+)\s*[-–]\s*(\d+)\s+of\s+(\d+)",
        re.IGNORECASE,
    )
    for item in reversed(conversation_history or []):
        role, content = _history_role_and_text(item)
        if role not in {"assistant", "ai", "bot"}:
            continue
        match = pattern.search(content)
        if match:
            return int(match.group(1)), int(match.group(2)), int(match.group(3))
    return 0, 0, 0


def _filter_facility_records(analytics, question):
    """Apply UI-equivalent facility/status filters to analyzer booking records."""
    if not isinstance(analytics, dict):
        return analytics
    records = analytics.get("facility_records")
    if not isinstance(records, list):
        return analytics

    q = re.sub(r"\s+", " ", str(question or "").strip().lower())
    facility_options = ("function room 1", "bbq pit 1", "bbq pit 2")
    selected_facility = next(
        (name for name in facility_options if name in q), None
    )
    status_aliases = {
        "new": ("new",),
        "confirmed": ("confirmed",),
        "cancelled": ("cancelled", "canceled"),
    }
    selected_status = next(
        (status for status, aliases in status_aliases.items()
         if any(re.search(rf"\b{re.escape(alias)}\b", q) for alias in aliases)),
        None,
    )
    # "All" means no status restriction, matching the UI's default.
    if not selected_facility and not selected_status:
        return analytics

    filtered = []
    for record in records:
        if not isinstance(record, dict):
            continue
        facility_value = str(record.get("facility") or "").strip().lower()
        status_value = str(record.get("status") or "").strip().lower()
        if selected_facility and selected_facility not in facility_value:
            continue
        if selected_status and status_value not in status_aliases[selected_status]:
            continue
        filtered.append(record)

    result = dict(analytics)
    result["facility_records"] = filtered
    result["applied_filters"] = {
        "facility": selected_facility or "All",
        "status": selected_status.title() if selected_status else "All",
    }
    return result


def _prepare_facility_page(analytics, question, conversation_history):
    """
    Paginate a detected facility-booking record list before it reaches Gemini.
    Returns (prompt_data, footer, page_records, is_list_request).
    """
    analytics = _filter_facility_records(analytics, question)
    found = _find_facility_record_list(analytics)
    previous_start, previous_end, previous_total = _previous_facility_page(conversation_history)
    is_next = _is_next_facility_page(question)
    is_list_request = _is_facility_list_request(question) or (
        previous_total > 0 and _is_facility_context_followup(question)
    )
    if not is_list_request:
        return analytics, None, None, False
    if not found:
        logger.warning(
            "Facility pagination requested, but no booking record list was detected in analytics. "
            "Gemini response will be used without deterministic pagination."
        )
        return analytics, None, None, True

    _, path, all_records = found
    total = len(all_records)
    page_size = _requested_facility_page_size(question)
    # The next offset is the previous page's ending record, not the old start.
    start = min(previous_end, total) if is_next and previous_total > 0 else 0
    end = min(start + page_size, total)
    page_records = all_records[start:end]

    prompt_data = _replace_at_path(analytics, path, page_records)
    if not isinstance(prompt_data, dict):
        prompt_data = {"facility_booking_records": prompt_data}
    prompt_data["facility_pagination"] = {
        "total_matching_records": total,
        "page_start": start + 1 if page_records else 0,
        "page_end": end,
        "page_size": page_size,
        "remaining_records": max(0, total - end),
        "instruction": "Use only the facility booking records in the selected list. Do not invent records or counts.",
    }

    if total == 0:
        footer = "No facility booking records were found."
    elif start >= total:
        footer = f"No more facility booking records. Total: {total}."
    else:
        footer = f"Showing facility booking records {start + 1}-{end} of {total}."
    logger.info(
        "Facility pagination | start=%s end=%s total=%s",
        start + 1 if page_records else 0, end, total,
    )
    return prompt_data, footer, page_records, True


def _format_facility_record(row, index):
    """Format a booking record without assuming a fixed API schema."""
    preferred = (
        "booking_id", "booking_reference", "reference", "facility_name",
        "facility", "name", "booking_date", "date", "start_time",
        "end_time", "status", "purpose", "unit", "user_name",
    )
    normalized = {str(k).lower().replace("-", "_").replace(" ", "_"): v for k, v in row.items()}
    used = set()
    parts = []
    for key in preferred:
        if key in normalized and normalized[key] not in (None, ""):
            label = key.replace("_", " ").title()
            parts.append(f"{label}: {normalized[key]}")
            used.add(key)
    if not parts:
        for key, value in row.items():
            if value not in (None, "") and not isinstance(value, (dict, list)):
                parts.append(f"{str(key).replace('_', ' ').title()}: {value}")
    return f"{index}. " + " | ".join(parts) if parts else f"{index}. Facility booking record"


def _deterministic_facility_list_answer(page_records, footer, start):
    lines = ["Here are the facility booking records:"]
    lines.extend(
        _format_facility_record(row, start + i + 1)
        for i, row in enumerate(page_records)
    )
    lines.extend(["", footer])
    if "No more facility booking records" not in footer and "No facility booking records were found" not in footer:
        if re.search(r"of\s+(\d+)", footer):
            lines.extend(["", "You can also ask:", "- Show me the next 5 records"])
    return "\n".join(lines)

# Facilities Node

# ============================================================



def facilities_node(state):



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
        conversation_history = state.get("conversation_history") or []
        original_question = str(state.get("original_question") or question or "").strip()



        authorization = state.get(

            "authorization"

        )



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

                "Hi! How can I help you with Facility Bookings?"

            )



            return state



        # ----------------------------------

        # Extract Date Range

        # ----------------------------------



        start_date, end_date = (

            extract_date_range(

                question

            )

        )



        # ----------------------------------

        # Debug Date Range

        # ----------------------------------



        print("=" * 80)

        print("FACILITY CHAT DATE RANGE")

        print("=" * 80)



        print(

            "QUESTION:",

            question

        )



        print(

            "START DATE:",

            start_date

        )



        print(

            "END DATE:",

            end_date

        )



        print("=" * 80)



        # ----------------------------------

        # Get Facility Booking Report

        # ----------------------------------



        report_data = (

            FacilityBookingReportService()

            .get_report(

                login_id=login_id,

                property_id=property_id,

                authorization=authorization,

                start_date=start_date,

                end_date=end_date

            )

        )



        # ----------------------------------

        # Analytics

        # ----------------------------------



        analytics = (

            FacilityBookingAnalyzer()

            .analyze(

                report_data

            )

        )



        # ----------------------------------

        # Add Reporting Period

        # ----------------------------------



        analytics["reporting_period"] = {

            "start_date": start_date,

            "end_date": end_date

        }



        # ----------------------------------

        # Debug Analytics

        # ----------------------------------



        print("=" * 80)

        print("FACILITY ANALYTICS")

        print("=" * 80)



        print(

            analytics

        )



        print("=" * 80)



        # ----------------------------------

        # Build Prompt

        # ----------------------------------



        pagination_question = original_question or question
        analytics_for_prompt, pagination_footer, page_records, is_list_request = (
            _prepare_facility_page(
                analytics=analytics,
                question=pagination_question,
                conversation_history=conversation_history,
            )
        )

        prompt = (
            PromptBuilder()
            .build_facility_chat_prompt(
                report_data=analytics_for_prompt,
                question=question
            )
        )



        print("=" * 80)

        print("FACILITY CHAT PROMPT")

        print("=" * 80)



        print(

            prompt

        )



        print("=" * 80)



        # ----------------------------------

        # Gemini Response

        # ----------------------------------



        llm_response = generate(

            prompt

        )



        print("=" * 80)

        print("GEMINI RESPONSE")

        print("=" * 80)



        print(

            llm_response

        )



        print("=" * 80)



        # ----------------------------------

        # Parse Response

        # ----------------------------------



        answer = (

            LLMResponseParser()

            .parse_text(

                llm_response

            )

        )

        # Use backend-selected records and pagination metadata as the source of truth.
        if pagination_footer and page_records is not None:
            footer_match = re.search(
                r"Showing facility booking records (\d+)[-–](\d+) of (\d+)",
                pagination_footer,
            )
            page_start = int(footer_match.group(1)) - 1 if footer_match else 0
            answer = _deterministic_facility_list_answer(
                page_records=page_records,
                footer=pagination_footer,
                start=page_start,
            )




        print("=" * 80)

        print("ANSWER GENERATED")

        print("=" * 80)



        print(

            answer

        )



        print("=" * 80)



        # ----------------------------------

        # Save Answer

        # ----------------------------------



        state["answer"] = answer



        return state



    except Exception as ex:



        logger.exception(

            "Facility Agent Failed"

        )



        state["answer"] = (

            f"Unable to process facility booking question: "

            f"{str(ex)}"

        )



        return state