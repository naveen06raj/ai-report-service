import logging

from services.reports.feedback_report import (
    FeedbackReportService
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


def feedback_node(state):

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
        # Get Feedback Report
        # ----------------------------------

        report_data = (
            FeedbackReportService()
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
            .build_feedback_chat_prompt(
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
            "Feedback Agent Failed"
        )

        state["answer"] = (
            f"Unable to process feedback question: "
            f"{str(ex)}"
        )

        return state