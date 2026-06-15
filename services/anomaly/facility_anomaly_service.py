import json
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


class FacilityAnomalyService:

    def detect(
        self,
        analytics: dict
    ) -> dict:

        try:

            prompt = (
                PromptBuilder()
                .build_facility_anomaly_prompt(
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
                "Facility anomaly detection failed"
            )

            return {
                "anomalies": [
                    {
                        "severity": "low",
                        "title": "Detection Error",
                        "description": str(ex)
                    }
                ]
            }