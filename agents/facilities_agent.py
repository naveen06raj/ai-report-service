import logging

from services.reports.facility_booking_report import (
    FacilityBookingReportService
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

        property_id = state.get(
            "property_id"
        )

        period = state.get(
            "period"
        )

        question = state.get(
            "question"
        )

        authorization = state.get(
            "authorization"
        )

        # ----------------------------------
        # Get Facility Booking Report
        # ----------------------------------

        report_data = (
            FacilityBookingReportService()
            .get_report(
                property_id=property_id,
                period=period,
                authorization=authorization
            )
        )

        # ----------------------------------
        # Build Prompt
        # ----------------------------------

        prompt = (
            PromptBuilder()
            .build_facility_chat_prompt(
                report_data=report_data,
                question=question
            )
        )

        # ----------------------------------
        # Gemini Response
        # ----------------------------------

        llm_response = generate(
            prompt
        )

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
            "Facilities Agent Failed"
        )

        state["answer"] = (
            f"Unable to process facility booking question: "
            f"{str(ex)}"
        )

        return state