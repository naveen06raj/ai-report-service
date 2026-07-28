import logging

from services.reports.threshold_client import ThresholdClient
from services.analytics.threshold_analyzer import ThresholdAnalyzer

from services.llm.prompt_builder import PromptBuilder

from services.llm.gemini_client import (
    generate
)

from services.llm.llm_response_parser import (
    LLMResponseParser
)

logger = logging.getLogger(__name__)


class ThresholdAdvisorService:

    def generate_advisor(
        self,
        authorization: str,
        property_id: str = None,
        period: str = "monthly"
    ) -> dict:

        try:

            # ----------------------------------
            # Fetch Threshold Configuration
            # ----------------------------------

            threshold_response = (
                ThresholdClient()
                .get_threshold_configs(
                    authorization=authorization
                )
            )

            # ----------------------------------
            # Analyze Data
            # ----------------------------------

            analytics = (
                ThresholdAnalyzer()
                .analyze(
                    threshold_response
                )
            )

            # ----------------------------------
            # Build Prompt
            # ----------------------------------

            prompt = (
                PromptBuilder()
                .build_threshold_advisor_prompt(
                    analytics
                )
            )

            print("=" * 80)
            print("THRESHOLD ADVISOR PROMPT")
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

            result = (
                LLMResponseParser()
                .parse_json(
                    response
                )
            )

            print("=" * 80)
            print("THRESHOLD ADVISOR PARSED")
            print("=" * 80)

            return result

        except Exception as ex:

            logger.exception(
                "Threshold advisor failed"
            )

            return {
                "overall_health": "Unknown",
                "summary": str(ex),
                "recommendations": []
            }