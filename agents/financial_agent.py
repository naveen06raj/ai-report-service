import re
from datetime import date, datetime, timedelta

from graph.state import ReportState

from services.reports.financial_report import (
    FinancialReportService
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

    return new_year, new_month


def format_date(value):
    return value.strftime(
        "%Y-%m-%d"
    )


# ============================================================
# Extract Date Range
# ============================================================

def extract_date_range(question):

    question_lower = question.lower().strip()

    today = date.today()

    # --------------------------------------------------------
    # This Month
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Last / Previous Month
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Last / Past / Previous N Months
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # This Year
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Last / Previous Year
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # This Week
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Last / Previous Week
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Explicit Date Range
    #
    # Examples:
    # April 6, 2026 to September 7, 2026
    # April 6, 2026 until September 7, 2026
    # April 6, 2026 - September 7, 2026
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Specific Month + Year
    #
    # Example:
    # September 2026
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # No Date
    # --------------------------------------------------------

    return None, None


# ============================================================
# Financial Node
# ============================================================

def financial_node(
    state: ReportState
):

    try:

        login_id = state.get(
            "login_id"
        )

        property_id = state.get(
            "property_id"
        )

        authorization = state.get(
            "authorization"
        )

        question = state.get(
            "question"
        )

        # ====================================================
        # Validation
        # ====================================================

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

        # ====================================================
        # Simple Greeting
        # ====================================================

        greeting = question.strip().lower()

        if greeting in [
            "hi",
            "hello",
            "hey",
            "hi there",
            "hello there"
        ]:

            state["answer"] = (
                "Hi! How can I help you with Financial Reports?"
            )

            return state

        # ====================================================
        # Extract Date Range
        # ====================================================

        start_date, end_date = extract_date_range(
            question
        )

        print("=" * 80)
        print("FINANCIAL DATE RANGE")
        print("=" * 80)
        print(
            f"Start Date: {start_date}"
        )
        print(
            f"End Date:   {end_date}"
        )
        print("=" * 80)

        # ====================================================
        # Financial Report
        # ====================================================

        report_data = (
            FinancialReportService()
            .get_report(
                login_id=login_id,
                property_id=property_id,
                authorization=authorization,
                start_date=start_date,
                end_date=end_date
            )
        )

        # ====================================================
        # Add Reporting Period
        # ====================================================

        report_data["reporting_period"] = {
            "start_date": start_date,
            "end_date": end_date
        }

        # ====================================================
        # Check for Specific Invoice Number
        # ====================================================

        invoice_match = re.search(
            r"\b[A-Za-z]{2}\d{6,}-\d+\b",
            question
        )

        if invoice_match:

            invoice_no = invoice_match.group()

            # -----------------------------------------------
            # Extract Invoices
            # -----------------------------------------------

            invoices_data = report_data.get(
                "invoices",
                {}
            )

            invoice_list = []

            if isinstance(
                invoices_data,
                dict
            ):

                data = invoices_data.get(
                    "data",
                    {}
                )

                if isinstance(
                    data,
                    dict
                ):

                    invoice_list = data.get(
                        "invoices",
                        []
                    )

            elif isinstance(
                invoices_data,
                list
            ):

                invoice_list = invoices_data

            # -----------------------------------------------
            # Find Invoice
            # -----------------------------------------------

            invoice_id = None

            for invoice in invoice_list:

                if not isinstance(
                    invoice,
                    dict
                ):
                    continue

                current_invoice_no = str(
                    invoice.get(
                        "invoice_no",
                        ""
                    )
                ).strip()

                if (
                    current_invoice_no.lower()
                    ==
                    invoice_no.lower()
                ):

                    invoice_id = invoice.get(
                        "id"
                    )

                    break

            # -----------------------------------------------
            # Get Invoice Details
            # -----------------------------------------------

            if invoice_id:

                invoice_view = (
                    FinancialReportService()
                    .get_invoice_view(
                        login_id=login_id,
                        property_id=property_id,
                        invoice_id=invoice_id,
                        authorization=authorization
                    )
                )

                report_data[
                    "invoice_view"
                ] = invoice_view

        # ====================================================
        # Build Financial Chat Prompt
        # ====================================================

        prompt = (
            PromptBuilder()
            .build_financial_chat_prompt(
                report_data,
                question
            )
        )

        print("=" * 80)
        print("FINANCIAL GEMINI PROMPT")
        print("=" * 80)
        print(prompt)
        print("=" * 80)

        # ====================================================
        # Gemini
        # ====================================================

        response = generate(
            prompt
        )

        print("=" * 80)
        print("FINANCIAL GEMINI RESPONSE")
        print("=" * 80)
        print(response)
        print("=" * 80)

        # ====================================================
        # Parse Response as Plain Text
        # ====================================================

        answer = (
            LLMResponseParser()
            .parse_text(
                response
            )
        )

        print("=" * 80)
        print("FINANCIAL ANSWER")
        print("=" * 80)
        print(answer)
        print("=" * 80)

        state["answer"] = answer

        return state

    except Exception as ex:

        state["answer"] = (
            f"Financial Agent Error: {str(ex)}"
        )

        return state