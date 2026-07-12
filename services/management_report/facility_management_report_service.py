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

            return (
                LLMResponseParser()
                .parse_json(
                    response
                )
            )

        except Exception as ex:

            logger.exception(
                "Facility management report generation failed"
            )

            return {

                "report": {

                    "title":
                        "Facility Booking Management Report",

                    "executive_summary":
                        "Unable to generate the facility booking management report.",

                    "key_findings": [
                        str(ex)
                    ],

                    "key_risks": [
                        "Management report could not be generated."
                    ],

                    "recommended_actions": [
                        "Review the application logs.",
                        "Verify the analytics data.",
                        "Retry the report generation."
                    ],

                    "priority":
                        "Low"

                }

            }