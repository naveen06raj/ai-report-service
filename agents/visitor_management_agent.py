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
        # Get Visitor Management Report
        # ----------------------------------

        report_data = (
            VisitorManagementReportService()
            .get_report(
                login_id=login_id,
                property_id=property_id,
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

        print("=" * 80)
        print("VISITOR MANAGEMENT CHAT PROMPT")
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
        print("VISITOR MANAGEMENT GEMINI RESPONSE")
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

        print("=" * 80)
        print("VISITOR MANAGEMENT ANSWER")
        print("=" * 80)
        print(answer)
        print("=" * 80)

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