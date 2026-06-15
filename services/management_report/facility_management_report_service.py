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


class FacilityManagementReportService:

    def generate(
        self,
        analytics: dict
    ) -> dict:

        try:

            prompt = (
                PromptBuilder()
                .build_facility_management_report_prompt(
                    analytics
                )
            )

            response = generate(
                prompt
            )

            report = (
                LLMResponseParser()
                .parse_json(
                    response
                )
            )

            return report

        except Exception as ex:

            logger.exception(
                "Facility management report generation failed"
            )

            return {
                "report": {
                    "title":
                        "Facility Booking Management Report",

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