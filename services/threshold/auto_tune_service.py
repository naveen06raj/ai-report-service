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


class AutoTuneService:

    def generate_auto_tune(
        self,
        authorization: str,
        login_id: int,
        property_id: int,
        period: str = "monthly"
    ) -> dict:

        try:

            # ----------------------------------
            # Fetch Threshold Configuration
            # ----------------------------------

            threshold_response = (
                ThresholdClient()
                .get_threshold_configs(
                    authorization=authorization,
                    login_id=login_id,
                    property_id=property_id,
                    period=period
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
                .build_auto_tune_prompt(
                    analytics
                )
            )

            print("=" * 80)
            print("AUTO TUNE PROMPT")
            print("=" * 80)
            print(prompt)
            print("=" * 80)

            # ----------------------------------
            # Generate AI Response
            # ----------------------------------

            response = generate(
                prompt
            )

            print("=" * 80)
            print("AUTO TUNE RESPONSE")
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
            print("AUTO TUNE PARSED")
            print("=" * 80)
            print(result)
            print("=" * 80)

            return result

        except Exception as ex:

            logger.exception(
                "Auto Tune failed"
            )

            return {
                "overall_status": "Failed",
                "summary": str(ex),
                "metrics": []
            }