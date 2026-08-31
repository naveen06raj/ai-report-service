import logging

from services.reports.key_collection_report import (
    KeyCollectionReportService
)

from services.analytics.key_collection_analyzer import (
    KeyCollectionAnalyzer
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


def key_collection_node(state):

    try:

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
        # Get Key Collection Data
        # ----------------------------------

        report_data = (
            KeyCollectionReportService()
            .get_report(
                login_id=login_id,
                property_id=property_id,
                authorization=authorization
            )
        )

        # ----------------------------------
        # Convert Raw Data -> Analytics
        # ----------------------------------

        analytics = (
            KeyCollectionAnalyzer()
            .analyze(
                report_data
            )
        )

        # ----------------------------------
        # Build Prompt
        # ----------------------------------

        prompt = (
            PromptBuilder()
            .build_key_collection_chat_prompt(
                report_data=analytics,
                question=question
            )
        )

        print("=" * 80)
        print("KEY COLLECTION CHAT PROMPT")
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
        print("KEY COLLECTION GEMINI RESPONSE")
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
        print("KEY COLLECTION ANSWER")
        print("=" * 80)
        print(answer)
        print("=" * 80)

        state["answer"] = answer

        return state

    except Exception as ex:

        logger.exception(
            "Key Collection Agent Failed"
        )

        state["answer"] = (
            f"Unable to process key collection question: "
            f"{str(ex)}"
        )

        return state