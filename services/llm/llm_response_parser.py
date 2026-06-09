import json
import logging

logger = logging.getLogger(__name__)


class LLMResponseParser:

    def parse_json(
        self,
        response_text: str
    ) -> dict:

        try:

            if not response_text:

                raise ValueError(
                    "Empty response received from LLM"
                )

            cleaned_text = (
                response_text
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

            return json.loads(
                cleaned_text
            )

        except json.JSONDecodeError as ex:

            logger.exception(
                "Failed to parse JSON response"
            )

            raise Exception(
                f"Invalid JSON response: {str(ex)}"
            )

        except Exception as ex:

            logger.exception(
                "JSON parser failed"
            )

            raise Exception(
                f"Parser Error: {str(ex)}"
            )

    def parse_text(
        self,
        response_text: str
    ) -> str:

        if not response_text:

            return ""

        return response_text.strip()

    def parse_router_response(
        self,
        response_text: str
    ) -> str:

        if not response_text:

            return "fallback"

        module = (
            response_text
            .strip()
            .lower()
        )

        allowed_modules = [
            "feedback",
            "facilities",
            "defect",
            "security",
            "fallback"
        ]

        if module not in allowed_modules:

            return "fallback"

        return module