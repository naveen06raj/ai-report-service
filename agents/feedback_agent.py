import logging

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


def feedback_node(state):

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
        # Get Feedback Data
        # ----------------------------------

        report_data = (
            FeedbackReportService()
            .get_report(
                login_id=login_id,
                authorization=authorization
            )
        )

        # ----------------------------------
        # Convert Raw Data -> Analytics
        # ----------------------------------

        analytics = (
            ResidentFeedbackAnalyzer()
            .analyze(
                report_data
            )
        )

        # ----------------------------------
        # Build Prompt
        # ----------------------------------

        prompt = (
            PromptBuilder()
            .build_feedback_chat_prompt(
                report_data=analytics,
                question=question
            )
        )

        print("=" * 80)
        print("CHAT PROMPT CREATED")
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

        print("=" * 80)
        print("ANSWER GENERATED")
        print("=" * 80)

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