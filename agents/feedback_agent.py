import re



import logging



from datetime import datetime, date, timedelta



from services.reports.feedback_report import (



    FeedbackReportService



)



from services.analytics.resident_feedback_analyzer import (



    ResidentFeedbackAnalyzer



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



    """



    Return the first day of the given month.



    """



    return date(



        year,



        month,



        1



    )



def last_day_of_month(year, month):



    """



    Return the last day of the given month.



    """



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



    """



    Subtract complete calendar months from a date.



    Example:



    September 8, 2026 - 1 month



    -> August 8, 2026



    """



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



    # Keep the day within the target month.



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



    """



    Convert date object to YYYY-MM-DD.



    """



    return input_date.strftime(



        "%Y-%m-%d"



    )



# ============================================================



# Extract Date Range From Question



# ============================================================



def extract_date_range(question: str):



    if not question:



        return None, None



    question_lower = question.lower().strip()



    # --------------------------------------------------------



    # Use today's date.



    #



    # Example:



    # If today is September 8, 2026:



    #



    # today = 2026-09-08



    # --------------------------------------------------------



    today = date.today()



    # ========================================================



    # THIS MONTH



    #



    # Example:



    #



    # "this month"



    #



    # September 1, 2026 -> September 8, 2026



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



    # Examples:



    #



    # "last month"



    # "previous month"



    #



    # September 8, 2026



    # ->



    # August 1, 2026 -> August 31, 2026



    # ========================================================



    if re.search(



        r"\b(last|previous)\s+month\b",



        question_lower



    ):



        previous_month_date = subtract_months(



            today,



            1



        )



        start_date = first_day_of_month(



            previous_month_date.year,



            previous_month_date.month



        )



        end_date = last_day_of_month(



            previous_month_date.year,



            previous_month_date.month



        )



        return (



            format_date(start_date),



            format_date(end_date)



        )



    # ========================================================



    # LAST N MONTHS



    #



    # Examples:



    #



    # "last 3 months"



    # "last 6 months"



    # "last 12 months"



    #



    # On September 8, 2026:



    #



    # last 3 months



    # ->



    # June 1, 2026 -> August 31, 2026



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



            # Start from the first day of the



            # current month and go back N months.



            current_month_start = first_day_of_month(



                today.year,



                today.month



            )



            start_date = subtract_months(



                current_month_start,



                months_count



            )



            # Last day of previous month.



            end_date = current_month_start - timedelta(



                days=1



            )



            return (



                format_date(start_date),



                format_date(end_date)



            )



    # ========================================================



    # THIS YEAR



    #



    # Example:



    #



    # January 1, 2026 -> September 8, 2026



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



    #



    # Example:



    #



    # January 1, 2025 -> December 31, 2025



    # ========================================================



    if re.search(



        r"\b(last|previous)\s+year\b",



        question_lower



    ):



        previous_year = today.year - 1



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



    # Monday -> today



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



    # Supported:



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



                "Invalid date range found in question: %s",



                question



            )



            return None, None



    # ========================================================



    # SINGLE MONTH + YEAR



    #



    # Examples:



    #



    # "September 2026"



    # "Show feedback for August 2026"



    #



    # Returns the complete calendar month.



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



        month_name = month_year_match.group(



            1



        ).lower()



        year = int(



            month_year_match.group(



                2



            )



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



    # NO DATE FOUND



    #



    # Examples:



    #



    # "Give me a feedback overview"



    # "What are the main complaints?"



    #



    # The backend will receive only:



    #



    # login_id



    # property_id



    # ========================================================



    return None, None



# ============================================================



# ============================================================



# Feedback Pagination Helpers



# ============================================================





DEFAULT_FEEDBACK_PAGE_SIZE = 5



MAX_FEEDBACK_PAGE_SIZE = 50





def _history_role_and_text(item):



    """Read common message formats returned by ChatRepository."""



    if not isinstance(item, dict):



        return "", ""





    role = str(item.get("role") or item.get("type") or "").strip().lower()



    content = (



        item.get("content")



        or item.get("message")



        or item.get("text")



        or item.get("answer")



        or ""



    )





    # Some repositories store message content as a list of text blocks.



    if isinstance(content, list):



        parts = []



        for part in content:



            if isinstance(part, dict):



                parts.append(str(part.get("text") or part.get("content") or ""))



            else:



                parts.append(str(part))



        content = " ".join(parts)





    return role, str(content)





def _is_feedback_context_followup(question):

    """Return True when a short follow-up relies on prior feedback context."""

    value = str(question or "").strip().lower()

    patterns = (

        r"\b(next|more|continue|remaining)\b",

        r"\b(show|list|display|get)\s+(?:me\s+)?(?:the\s+)?(?:closed|open|resolved)\s+ones\b",

        r"\b(show|list|display|get)\s+(?:me\s+)?(?:the\s+)?ones\b",

        r"\b(show|list|display|get)\s+(?:me\s+)?(?:all\s+)?(?:the\s+)?(?:closed|open|resolved)\b",

        r"\b(?:those|them|that|same period|same date range)\b",

        r"\b(filter|filtered)\b",

    )

    return any(re.search(pattern, value, re.IGNORECASE) for pattern in patterns)





def _previous_feedback_date_range(conversation_history):

    """Recover the most recent explicit reporting period from prior user messages."""

    for item in reversed(conversation_history or []):

        role, content = _history_role_and_text(item)

        if role not in {"user", "human", "client"}:

            continue

        start_date, end_date = extract_date_range(content)

        if start_date and end_date:

            return start_date, end_date

    return None, None





def _requested_feedback_page_size(question):



    """Return a safe page size from phrases such as 'next 10 records'."""



    value = str(question or "")



    patterns = (



        r"\bnext\s+(\d+)\b",



        r"\b(?:show|display|get|list)\s+(?:me\s+)?(\d+)\b",



        r"\b(\d+)\s+(?:feedback\s+)?(?:records|items)\b",



    )





    for pattern in patterns:



        match = re.search(pattern, value, re.IGNORECASE)



        if match:



            return max(1, min(int(match.group(1)), MAX_FEEDBACK_PAGE_SIZE))





    return DEFAULT_FEEDBACK_PAGE_SIZE





def _is_next_feedback_page(question):



    return bool(



        re.search(



            r"\b(next|more|continue|remaining)\b",



            str(question or ""),



            re.IGNORECASE,



        )



    )





def _is_feedback_list_request(question):

    value = str(question or "").lower()

    patterns = (

        r"\bshow\b.*\bfeedback\b",

        r"\blist\b.*\bfeedback\b",

        r"\bdisplay\b.*\bfeedback\b",

        r"\bfeedback\s+records\b",

        r"\ball\s+feedback\b",

        r"\bnext\b.*\b(feedback|records|items|page|ones)\b",

        r"\bmore\b.*\b(feedback|records|items|ones)\b",

        r"\b(?:first|next|previous)\s+\d+\s+(?:feedback\s+)?(?:records|items)\b",

        r"\b(show|list|display)\b.*\b(open|closed|resolved)\b",

        r"\b(open|closed|resolved)\s+(ones|feedback|records)\b",

        r"\b(show|list|display)\b.*\b(category|drains|sewage|facilities|plumbing|electrical|cleaning|pests?)\b",

    )

    return any(re.search(pattern, value) for pattern in patterns)





def _feedback_filter_from_text(text):

    """Extract a supported status/category filter from a question."""

    value = str(text or "").lower()

    status_match = re.search(r"\b(open|closed|resolved)\b", value)

    if status_match:

        return {"kind": "status", "value": status_match.group(1).title()}



    # Match known category names without relying on the LLM to filter a page.

    categories = (

        "drains & sewage", "drains and sewage", "pests control",

        "facilities", "plumbing", "electrical", "cleaning",

    )

    for category in categories:

        if category in value:

            canonical = "Drains & Sewage" if category in ("drains & sewage", "drains and sewage") else category.title()

            return {"kind": "category", "value": canonical}

    return None





def _active_feedback_filter(question, conversation_history):

    """Use the current filter, or retain the last explicit filter for page follow-ups."""

    current_filter = _feedback_filter_from_text(question)

    if current_filter:

        return current_filter



    for item in reversed(conversation_history or []):

        role, content = _history_role_and_text(item)

        if role not in {"user", "human", "client"}:

            continue

        candidate = _feedback_filter_from_text(content)

        if candidate:

            return candidate

        # Stop at a new explicit request to show all feedback; don't retain an old filter.

        if re.search(r"\b(all|full)\s+(feedback|records)\b", content, re.IGNORECASE):

            return None

    return None





def _apply_feedback_filter(records, active_filter):

    if not active_filter:

        return list(records)



    kind = active_filter["kind"]

    expected = str(active_filter["value"]).strip().casefold()

    filtered = []

    for record in records:

        if not isinstance(record, dict):

            continue

        if kind == "status":

            actual = str(record.get("status") or record.get("Status") or "").strip().casefold()

            if actual == expected:

                filtered.append(record)

        elif kind == "category":

            actual = str(record.get("category") or record.get("Category") or "").strip().casefold()

            aliases = {expected}

            if expected == "drains & sewage":

                aliases.add("drains and sewage")

            if actual in aliases:

                filtered.append(record)

        else:

            filtered.append(record)

    return filtered





def _previous_feedback_page(conversation_history):

    """Return (start, end, total) from the latest generic or filtered page marker."""

    footer_pattern = re.compile(

        r"Showing\s+(?:[A-Za-z& ]+\s+)?feedback\s+records\s+(\d+)\s*[-–]\s*(\d+)\s+of\s+(\d+)",

        re.IGNORECASE,

    )

    simple_pattern = re.compile(r"Showing\s+(\d+)\s+of\s+(\d+)\s+records", re.IGNORECASE)



    for item in reversed(conversation_history or []):

        role, content = _history_role_and_text(item)

        if role not in {"assistant", "ai", "bot"}:

            continue

        match = footer_pattern.search(content)

        if match:

            return int(match.group(1)), int(match.group(2)), int(match.group(3))

        match = simple_pattern.search(content)

        if match:

            shown, total = int(match.group(1)), int(match.group(2))

            return (1, shown, total) if shown > 0 else (0, 0, total)

    return 0, 0, 0





def _prepare_feedback_page(analytics, question, conversation_history):

    """Filter the complete record list first, then select the requested page."""

    prompt_data = dict(analytics)

    all_records = analytics.get("feedback_records") or []

    if not isinstance(all_records, list):

        logger.warning("analytics['feedback_records'] is not a list; pagination skipped")

        return prompt_data, None



    active_filter = _active_feedback_filter(question, conversation_history)

    matching_records = _apply_feedback_filter(all_records, active_filter)

    total = len(matching_records)



    previous_start, previous_end, previous_total = _previous_feedback_page(conversation_history)

    is_next = _is_next_feedback_page(question)

    is_list_request = _is_feedback_list_request(question) or (is_next and previous_total > 0)

    if not is_list_request:

        return prompt_data, None



    page_size = _requested_feedback_page_size(question)

    if is_next:

        # The previous page footer must match this filtered result set. If it does

        # not, start at page one rather than incorrectly applying an all-record offset.

        same_total = previous_total == total

        start = min(previous_end, total) if previous_total > 0 and same_total else 0

    else:

        start = 0



    end = min(start + page_size, total)

    selected_records = matching_records[start:end]



    prompt_data["feedback_records"] = selected_records

    prompt_data["feedback_records_preview"] = selected_records

    prompt_data["feedback_record_display_limit"] = page_size

    prompt_data["feedback_record_count"] = total

    prompt_data["feedback_records_remaining"] = max(0, total - end)

    prompt_data["active_feedback_filter"] = active_filter

    remaining = max(0, total - end)
    # A next page exists whenever at least one record remains. That final page
    # may contain fewer than five records, and must still be reachable.
    has_next = end < total

    prompt_data["pagination"] = {
        "start": start + 1 if selected_records else 0,
        "end": end,
        "total": total,
        "has_next": has_next,
    }



    filter_label = f"{active_filter['value'].lower()} " if active_filter else ""

    if total == 0:

        footer = f"No matching {filter_label}feedback records were found."

    elif start >= total:

        footer = f"No more {filter_label}feedback records. Total: {total}."

    else:

        footer = f"Showing {filter_label}feedback records {start + 1}-{end} of {total}."



    logger.info(

        "Feedback pagination | filter=%s start=%s end=%s total=%s page_size=%s next=%s",

        active_filter,

        start + 1 if selected_records else 0,

        end,

        total,

        page_size,

        is_next,

    )

    return prompt_data, footer





# Feedback Node



# ============================================================



def feedback_node(state):



    try:



        # ----------------------------------------------------



        # Get State Values



        # ----------------------------------------------------



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





        original_question = str(state.get("original_question") or question or "").strip()



        conversation_history = state.get("conversation_history") or []



        # ----------------------------------------------------



        # Validation



        # ----------------------------------------------------



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



        # ----------------------------------------------------



        # Simple Greeting



        # ----------------------------------------------------



        greeting = question.strip().lower()



        if greeting in [



            "hi",



            "hello",



            "hey",



            "hi there",



            "hello there"



        ]:



            state["answer"] = (



                "Hi! How can I help you with Feedback?"



            )



            return state



        # ----------------------------------------------------



        # Extract Date Range



        # ----------------------------------------------------



        start_date, end_date = extract_date_range(question)



        # Reuse the prior reporting period for follow-up requests such as

        # "Show me the closed ones" and "Show me the next 5 records".

        # An explicit date range in the current question takes priority.

        if (

            not start_date

            and not end_date

            and _is_feedback_context_followup(question)

        ):

            previous_start_date, previous_end_date = _previous_feedback_date_range(

                conversation_history

            )

            if previous_start_date and previous_end_date:

                start_date = previous_start_date

                end_date = previous_end_date

                logger.info(

                    "Reusing feedback reporting period from conversation history: %s to %s",

                    start_date,

                    end_date,

                )



        # ----------------------------------------------------



        # Debug Date Range



        # ----------------------------------------------------



        print("=" * 80)



        print("FEEDBACK CHAT DATE RANGE")



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



        # ----------------------------------------------------



        # Get Feedback Data



        #



        # Dates are optional.



        #



        # With dates:



        #   Backend receives start_date/end_date.



        #



        # Without dates:



        #   Backend receives only login_id/property_id.



        # ----------------------------------------------------



        report_data = (



            FeedbackReportService()



            .get_report(



                login_id=login_id,



                property_id=property_id,



                authorization=authorization,



                start_date=start_date,



                end_date=end_date



            )



        )



        # ----------------------------------------------------



        # Convert Raw Data -> Analytics



        #



        # Backend is responsible for filtering feedback



        # records by the requested date range.



        # ----------------------------------------------------



        analytics = (



            ResidentFeedbackAnalyzer()



            .analyze(



                report_data



            )



        )



        # ----------------------------------------------------



        # Add Reporting Period



        #



        # This tells Gemini what period the analytics



        # represent.



        # ----------------------------------------------------



        analytics["reporting_period"] = {



            "start_date": start_date,



            "end_date": end_date



        }



        # ----------------------------------------------------



        # Debug Analytics



        # ----------------------------------------------------



        print("=" * 80)



        print("FEEDBACK ANALYTICS")



        print("=" * 80)



        print(



            analytics



        )



        print("=" * 80)



        # ----------------------------------------------------



        # Build Prompt



        # ----------------------------------------------------



        # ----------------------------------------------------



        # Prepare current feedback page before calling Gemini



        # ----------------------------------------------------





        pagination_question = " ".join(part for part in (str(question or ""), str(original_question or "")) if part)



        analytics_for_prompt, pagination_footer = _prepare_feedback_page(



            analytics=analytics,



            question=pagination_question,



            conversation_history=conversation_history,



        )





        prompt = (



            PromptBuilder()



            .build_feedback_chat_prompt(



                report_data=analytics_for_prompt,



                question=question



            )



        )



        # ----------------------------------------------------



        # Debug Prompt



        # ----------------------------------------------------



        print("=" * 80)



        print("FEEDBACK CHAT PROMPT")



        print("=" * 80)



        print(



            prompt



        )



        print("=" * 80)



        # ----------------------------------------------------



        # Gemini Response



        # ----------------------------------------------------



        llm_response = generate(



            prompt



        )



        # ----------------------------------------------------



        # Debug Gemini Response



        # ----------------------------------------------------



        print("=" * 80)



        print("GEMINI RESPONSE")



        print("=" * 80)



        print(



            llm_response



        )



        print("=" * 80)



        # ----------------------------------------------------



        # Parse Response



        #



        # Feedback chatbot returns plain text.



        # ----------------------------------------------------



        answer = (



            LLMResponseParser()



            .parse_text(



                llm_response



            )



        )





        # Do not offer another page when fewer than page_size records remain.
        pagination = analytics_for_prompt.get("pagination", {})
        if not pagination.get("has_next", False):
            answer = re.sub(
                r"(?im)^.*(?:show\s+me\s+)?next\s+\d+\s+(?:feedback\s+)?(?:records|items).*?(?:\n|$)",
                "",
                answer,
            ).strip()

        # Append a deterministic page marker. The next request reads this marker



        # from persisted conversation history to calculate its starting offset.



        if pagination_footer:



            answer = f"{answer.rstrip()}\n\n{pagination_footer}"



        # ----------------------------------------------------



        # Debug Final Answer



        # ----------------------------------------------------



        print("=" * 80)



        print("ANSWER GENERATED")



        print("=" * 80)



        print(



            answer



        )



        print("=" * 80)



        # ----------------------------------------------------



        # Save Answer To State



        # ----------------------------------------------------



        state["answer"] = answer



        return state



    except Exception as ex:



        logger.exception(



            "Feedback Agent Failed"



        )



        state["answer"] = (



            f"Unable to process feedback question: "



            f"{str(ex)}"



        )



        return state
