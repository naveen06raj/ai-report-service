import re
import logging
from datetime import datetime, date, timedelta
from services.reports.visitor_management_report import (
    VisitorManagementReportService
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
                - timedelta(
                    days=1
                )
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
            - timedelta(
                days=7
            )
        )
        end_date = (
            current_week_start
            - timedelta(
                days=1
            )
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
    # April 6 2026 to September 7 2026
    # April 6, 2026 until September 7, 2026
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
    # Examples:
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
# Visitor Pagination Helpers
# ============================================================
DEFAULT_VISITOR_PAGE_SIZE = 5
MAX_VISITOR_PAGE_SIZE = 50

def _history_role_and_text(item):
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

def _requested_visitor_page_size(question):
    text = str(question or "")
    for pattern in (r"\bnext\s+(\d+)\b", r"\b(?:show|display|get|list)\s+(?:me\s+)?(\d+)\b", r"\b(\d+)\s+(?:visitor\s+)?(?:records|visitors|items)\b"):
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return max(1, min(int(match.group(1)), MAX_VISITOR_PAGE_SIZE))
    return DEFAULT_VISITOR_PAGE_SIZE

def _is_next_visitor_page(question):
    """Recognize common next-page phrases, even when the user says records/items."""
    q = re.sub(r"\s+", " ", str(question or "").strip().lower())
    return bool(re.search(
        r"\b(next|more|continue|remaining)\b|\b(show|give|display|get)\s+(?:me\s+)?(?:the\s+)?next\b",
        q,
        re.IGNORECASE,
    ))

def _is_visitor_list_request(question):
    text = re.sub(r"\s+", " ", str(question or "").strip().lower())
    # Include generic page requests like “next 5 records/items”; module context
    # is supplied by the router/conversation history, not by the wording alone.
    return bool(
        re.search(r"\b(show|list|display|get|find)\b.*\b(visitor|visitors|registrations)\b", text)
        or re.search(r"\b(all|next|more)\s+(?:the\s+)?(?:visitor|visitors|registrations|records|items)\b", text)
        or re.search(r"\b(next|more|continue|remaining)\s+(?:\d+\s+)?(?:records|items|visitors|registrations)\b", text)
        or re.search(r"\bvisitor\s+records\b", text)
    )

def _find_record_list(value, path=(), parent_key=""):
    """Find the most likely list of visitor-registration dictionaries in nested API data."""
    candidates = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key).lower()
            if isinstance(child, list) and child and all(isinstance(row, dict) for row in child):
                sample_keys = set().union(*(set(str(k).lower() for k in row.keys()) for row in child[:5]))
                field_hits = sum(any(term in k for k in sample_keys) for term in ("ticket", "visit", "purpose", "status", "visitor", "invited", "unit"))
                context_hit = 5 if any(term in key_text for term in ("visitor", "registration", "record", "result", "data", "list")) else 0
                score = field_hits + context_hit
                if score >= 3:
                    candidates.append((score, path + (key,), child))
            nested = _find_record_list(child, path + (key,), key_text)
            if nested:
                candidates.append(nested)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            nested = _find_record_list(child, path + (index,), parent_key)
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

def _previous_visitor_page(conversation_history):
    pattern = re.compile(r"Showing\s+visitor\s+records\s+(\d+)\s*[-–]\s*(\d+)\s+of\s+(\d+)(?:\s*\(filter:\s*([^)]*)\))?", re.IGNORECASE)
    for item in reversed(conversation_history or []):
        role, content = _history_role_and_text(item)
        if role not in {"assistant", "ai", "bot"}:
            continue
        match = pattern.search(content)
        if match:
            return int(match.group(1)), int(match.group(2)), int(match.group(3)), (match.group(4) or "").strip()
    return 0, 0, 0, ""

def _is_visitor_context_followup(question):
    q = str(question or "").lower()
    return bool(re.search(r"\b(ones|those|these|them|next|more|continue|remaining|pending|entered|checked[ -]?in|registered|registration success|delivery|visiting|contractor)\b", q))


def _visitor_filter_from_question(question):
    """Return a simple status/purpose filter inferred from the current question."""
    q = str(question or "").lower()
    status_terms = {
        "pending": ("pending",),
        "entered": ("entered", "checked in", "checked-in", "already entered"),
        "registered": ("registered",),
        "registration success": ("registration success", "successfully registered"),
    }
    for status, terms in status_terms.items():
        if any(term in q for term in terms):
            return ("status", status)
    for purpose in ("delivery", "visiting", "visit", "contractor"):
        if re.search(rf"\b{re.escape(purpose)}\b", q) and re.search(r"\b(visitor|visitors|registration|registrations|purpose|show|list|filter)\b", q):
            return ("purpose", purpose)
    return None

def _filter_visitor_records(records, filter_spec):
    if not filter_spec:
        return records
    field, expected = filter_spec
    output = []
    for row in records:
        normalized = {str(k).lower().replace("_", " ").replace("-", " "): v for k, v in row.items()}
        if field == "status":
            actual = " ".join(str(v) for k, v in normalized.items() if "status" in k).lower()
            if expected in actual or (expected == "entered" and "enter" in actual) or (expected == "registered" and "registered" in actual):
                output.append(row)
        elif field == "purpose":
            actual = " ".join(str(v) for k, v in normalized.items() if "purpose" in k).lower()
            if expected in actual:
                output.append(row)
    return output

def _prepare_visitor_page(report_data, question, conversation_history):
    """Slice record lists before Gemini sees them; keep aggregate/report fields otherwise unchanged."""
    found = _find_record_list(report_data)
    if not found:
        logger.warning("Visitor pagination skipped: no visitor-record list found in report data")
        return report_data, None

    _, path, all_records = found
    previous_start, previous_end, previous_total, previous_filter_text = _previous_visitor_page(conversation_history)
    is_next = _is_next_visitor_page(question)
    is_list_request = (
        _is_visitor_list_request(question)
        or (previous_total > 0 and (_is_visitor_context_followup(question) or is_next))
    )
    if not is_list_request:
        return report_data, None

    filter_spec = _visitor_filter_from_question(question)
    if filter_spec is None and is_next and previous_filter_text:
        match = re.match(r"(status|purpose)=(.+)", previous_filter_text, re.IGNORECASE)
        if match:
            filter_spec = (match.group(1).lower(), match.group(2).strip().lower())

    filtered_records = _filter_visitor_records(all_records, filter_spec)
    total = len(filtered_records)
    page_size = _requested_visitor_page_size(question)
    start = min(previous_end, total) if is_next and previous_total > 0 else 0
    end = min(start + page_size, total)
    page_records = filtered_records[start:end]

    prompt_data = _replace_at_path(report_data, path, page_records)
    if not isinstance(prompt_data, dict):
        prompt_data = {"visitor_records": prompt_data}
    prompt_data["visitor_pagination"] = {
        "total_matching_records": total,
        "page_start": start + 1 if page_records else 0,
        "page_end": end,
        "page_size": page_size,
        "remaining_records": max(0, total - end),
        "filter": f"{filter_spec[0]}={filter_spec[1]}" if filter_spec else None,
        "instruction": "Only the visitor records provided in the selected record list are to be displayed. Do not invent records or counts.",
    }

    filter_label = f" (filter: {filter_spec[0]}={filter_spec[1]})" if filter_spec else ""
    if total == 0:
        footer = "No matching visitor records were found."
    elif start >= total:
        footer = f"No more visitor records. Total: {total}{filter_label}."
    else:
        footer = f"Showing visitor records {start + 1}-{end} of {total}{filter_label}."
    logger.info("Visitor pagination | start=%s end=%s total=%s filter=%s", start + 1 if page_records else 0, end, total, filter_spec)
    return prompt_data, footer

def _first_value(row, candidates):
    """Get a value from common API field-name variants without assuming status codes."""
    if not isinstance(row, dict):
        return None
    normalized = {str(key).lower().replace("-", "_").replace(" ", "_"): value for key, value in row.items()}
    for candidate in candidates:
        if candidate in normalized and normalized[candidate] not in (None, ""):
            return normalized[candidate]
    return None


def _format_visitor_record(row, number):
    ticket = _first_value(row, ("ticket", "ticket_no", "ticket_number", "registration_no", "registration_number", "visitor_ticket"))
    purpose = _first_value(row, ("purpose", "visit_purpose", "visitor_purpose"))
    status = _first_value(row, ("status", "visitor_status", "registration_status"))
    visit_date = _first_value(row, ("date_of_visit", "visit_date", "date", "visit_datetime", "date_time"))
    parts = [f"{number}."]
    if ticket is not None:
        parts.append(f"Ticket: {ticket},")
    if purpose is not None:
        parts.append(f"Purpose: {purpose},")
    if status is not None:
        parts.append(f"Status: {status},")
    if visit_date is not None:
        parts.append(f"Date of Visit: {visit_date}")
    if len(parts) == 1:
        parts.append(str(row))
    return " ".join(parts).rstrip(" ,")


def _deterministic_visitor_page_answer(report_data, footer, question):
    """Format the already-selected page directly; do not ask Gemini to invent records."""
    found = _find_record_list(report_data)
    if not found or not isinstance(report_data, dict):
        return None
    records = found[2]
    meta = report_data.get("visitor_pagination", {})
    if not isinstance(meta, dict) or not any(key in meta for key in ("total_matching_records", "page_start", "page_end")):
        return None
    total = int(meta.get("total_matching_records", 0) or 0)
    start = int(meta.get("page_start", 0) or 0)
    end = int(meta.get("page_end", 0) or 0)
    if not records:
        if footer and footer.startswith("No more"):
            return footer
        return footer or "No matching visitor records were found."
    lines = ["Here are the visitor records:"]
    lines.extend(_format_visitor_record(row, start + index) for index, row in enumerate(records))
    if footer:
        lines.extend(["", footer])
    if end < total:
        lines.extend(["", f"You can also ask:", f"- Show me the next {meta.get('page_size', DEFAULT_VISITOR_PAGE_SIZE)} records"])
    return "\n".join(lines)


# ============================================================
# Visitor Management Node
# ============================================================
def visitor_management_node(state):
    try:
        # ----------------------------------
        # Get State Values
        # ----------------------------------
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
                "Hi! How can I help you with Visitor Management?"
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
        if not start_date and not end_date and _is_visitor_context_followup(question):
            for history_item in reversed(conversation_history):
                history_role, history_text = _history_role_and_text(history_item)
                if history_role in {"user", "human"}:
                    previous_start, previous_end = extract_date_range(history_text)
                    if previous_start or previous_end:
                        start_date, end_date = previous_start, previous_end
                        break
        # ----------------------------------
        # Debug Date Range
        # ----------------------------------
        print("=" * 80)
        print("VISITOR MANAGEMENT CHAT DATE RANGE")
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
        # Get Visitor Management Report
        # ----------------------------------
        report_data = (
            VisitorManagementReportService()
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
        #
        # Visitor Management currently does
        # not have a separate analyzer in
        # your provided node, so keep the
        # original report data and add the
        # period information.
        # ----------------------------------
        report_data["reporting_period"] = {
            "start_date": start_date,
            "end_date": end_date
        }
        # ----------------------------------
        # Debug Report Data
        # ----------------------------------
        print("=" * 80)
        print("VISITOR MANAGEMENT REPORT DATA")
        print("=" * 80)
        print(
            report_data
        )
        print("=" * 80)
        # ----------------------------------
        # Build Prompt
        # ----------------------------------
        pagination_question = original_question or question
        report_data_for_prompt, pagination_footer = _prepare_visitor_page(
            report_data=report_data,
            question=pagination_question,
            conversation_history=conversation_history,
        )

        # For list/pagination requests, format the backend-selected records directly.
        # This prevents Gemini from saying records are unavailable when they are present
        # and prevents the model from changing the page range or inventing records.
        deterministic_answer = _deterministic_visitor_page_answer(
            report_data_for_prompt, pagination_footer, pagination_question
        )
        if deterministic_answer is not None:
            state["answer"] = deterministic_answer
            logger.info("Returned deterministic visitor page for question=%r", question)
            return state

        prompt = (
            PromptBuilder()
            .build_visitor_chat_prompt(
                report_data=report_data_for_prompt,
                question=question
            )
        )
        print("=" * 80)
        print("VISITOR MANAGEMENT CHAT PROMPT")
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
        print("VISITOR MANAGEMENT GEMINI RESPONSE")
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
        if pagination_footer:
            answer = f"{str(answer).rstrip()}\n\n{pagination_footer}"
            remaining_match = re.search(r"of (\d+)", pagination_footer)
            if remaining_match and "No more visitor records" not in pagination_footer and "No matching visitor records" not in pagination_footer:
                answer += "\nAsk for the next 5 visitors to continue, or specify a status/purpose to filter the list."
        print("=" * 80)
        print("VISITOR MANAGEMENT ANSWER")
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
            "Visitor Management Agent Failed"
        )
        state["answer"] = (
            f"Unable to process visitor management question: "
            f"{str(ex)}"
        )
        return state
