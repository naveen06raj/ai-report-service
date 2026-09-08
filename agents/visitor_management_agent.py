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

        prompt = (
            PromptBuilder()
            .build_visitor_chat_prompt(
                report_data=report_data,
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