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


class VisitorManagementAnomalyService:

    def detect(
        self,
        analytics: dict
    ) -> dict:

        try:

            prompt = (
                PromptBuilder()
                .build_visitor_anomaly_prompt(
                    analytics
                )
            )

            response = generate(
                prompt
            )

            anomalies = (
                LLMResponseParser()
                .parse_json(
                    response
                )
            )

            return anomalies

        except Exception as ex:

            logger.exception(
                "Visitor management anomaly detection failed"
            )

            return {
                "anomalies": [
                    {
                        "severity": "Low",
                        "title": "Detection Error",
                        "description": str(ex),
                        "comparison": ""
                    }
                ]
            }