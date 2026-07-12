import logging

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


class FeedbackManagementReportService:

    def generate(
        self,
        analytics: dict
    ) -> dict:

        try:

            # ----------------------------------
            # Build Prompt
            # ----------------------------------

            prompt = (
                PromptBuilder()
                .build_feedback_management_report_prompt(
                    analytics
                )
            )

            print("=" * 80)
            print("MANAGEMENT REPORT PROMPT")
            print("=" * 80)
            print(prompt)
            print("=" * 80)

            # ----------------------------------
            # Gemini
            # ----------------------------------

            response = generate(
                prompt
            )

            print("=" * 80)
            print("GEMINI RESPONSE")
            print("=" * 80)
            print(response)
            print("=" * 80)

            # ----------------------------------
            # Parse JSON
            # ----------------------------------

            report = (
                LLMResponseParser()
                .parse_json(
                    response
                )
            )

            print("=" * 80)
            print("MANAGEMENT REPORT GENERATED")
            print("=" * 80)

            return report

        except Exception as ex:

            logger.exception(
                "Management report generation failed"
            )

            return {
                "report": {
                    "title":
                        "Resident Feedback Management Report",

                    "executive_summary":
                        "Unable to generate management report.",

                    "key_findings": [
                        str(ex)
                    ],

                    "key_risks": [],

                    "recommended_actions": [
                        "Review application logs."
                    ],

                    "priority":
                        "Low"
                }
            }