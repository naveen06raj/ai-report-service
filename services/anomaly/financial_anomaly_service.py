from services.llm.gemini_client import (
    generate
)

from services.llm.prompt_builder import (
    PromptBuilder
)

from services.llm.llm_response_parser import (
    LLMResponseParser
)


class FinancialAnomalyService:

    def detect(
        self,
        analytics_data: dict
    ) -> dict:

        try:

            # ----------------------------------
            # Build Prompt
            # ----------------------------------

            prompt = (
                PromptBuilder()
                .build_financial_anomaly_prompt(
                    analytics_data
                )
            )

            # ----------------------------------
            # Gemini
            # ----------------------------------

            response = generate(
                prompt
            )

            # ----------------------------------
            # Parse JSON
            # ----------------------------------

            return (
                LLMResponseParser()
                .parse_json(
                    response
                )
            )

        except Exception as ex:

            raise Exception(
                f"Financial Anomaly Detection Error: {str(ex)}"
            )