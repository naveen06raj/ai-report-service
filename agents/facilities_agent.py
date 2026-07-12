import logging

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


def facilities_node(state):

    try:

        login_id = state.get(
            "login_id"
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

        if not authorization:

            raise Exception(
                "Authorization token is required."
            )

        if not question:

            raise Exception(
                "Question is required."
            )

        # ----------------------------------
        # Get Facility Booking Report
        # ----------------------------------

        report_data = (
            FacilityBookingReportService()
            .get_report(
                login_id=login_id,
                authorization=authorization
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
        # Build Prompt
        # ----------------------------------

        prompt = (
            PromptBuilder()
            .build_facility_chat_prompt(
                report_data=analytics,
                question=question
            )
        )

        print("=" * 80)
        print("FACILITY CHAT PROMPT")
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
        print("GEMINI RESPONSE")
        print("=" * 80)
        print(llm_response)
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