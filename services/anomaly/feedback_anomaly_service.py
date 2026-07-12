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


class FeedbackAnomalyService:

    def detect(
        self,
        analytics: dict
    ) -> dict:

        try:

            # ----------------------------------
            # Build Prompt
            # ----------------------------------

            prompt = (
                PromptBuilder()
                .build_feedback_anomaly_prompt(
                    analytics
                )
            )

            print("=" * 80)
            print("ANOMALY PROMPT CREATED")
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

            anomalies = (
                LLMResponseParser()
                .parse_json(
                    response
                )
            )

            print("=" * 80)
            print("ANOMALIES PARSED")
            print("=" * 80)

            return anomalies

        except Exception as ex:

            logger.exception(
                "Feedback anomaly detection failed"
            )

            return {
                "anomalies": [
                    {
                        "severity": "low",
                        "title": "Detection Error",
                        "description": str(ex),
                        "comparison": ""
                    }
                ]
            }