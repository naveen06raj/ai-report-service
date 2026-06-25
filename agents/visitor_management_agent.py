import logging

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


def visitor_management_node(state):

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
        # Get Visitor Management Report
        # ----------------------------------

        report_data = (
            VisitorManagementReportService()
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
            .build_visitor_chat_prompt(
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
            "Visitor Management Agent Failed"
        )

        state["answer"] = (
            f"Unable to process visitor management question: "
            f"{str(ex)}"
        )

        return state