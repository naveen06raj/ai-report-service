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


class VisitorManagementReportService:

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
                .build_visitor_management_report_prompt(
                    analytics
                )
            )

            # ----------------------------------
            # Gemini Response
            # ----------------------------------

            response = generate(
                prompt
            )

            # ----------------------------------
            # Parse JSON
            # ----------------------------------

            report = (
                LLMResponseParser()
                .parse_json(
                    response
                )
            )

            return report

        except Exception as ex:

            logger.exception(
                "Visitor management report generation failed"
            )

            return {

                "report": {

                    "title":
                        "Visitor Management Report",

                    "executive_summary":
                        "Unable to generate the visitor management report.",

                    "key_findings": [],

                    "key_risks": [
                        str(ex)
                    ],

                    "recommended_actions": [
                        "Review the analytics data and application logs."
                    ],

                    "priority":
                        "Low"

                }

            }