from services.llm.prompt_builder import (
    PromptBuilder
)

from services.llm.gemini_client import (
    generate
)

from services.llm.llm_response_parser import (
    LLMResponseParser
)


class FinancialManagementReportService:

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
                .build_financial_management_report_prompt(
                    analytics
                )
            )

            print("=" * 80)
            print("FINANCIAL MANAGEMENT REPORT PROMPT")
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
            print("RAW GEMINI RESPONSE")
            print("=" * 80)
            print(response)
            print("=" * 80)

            # ----------------------------------
            # Parse Response
            # ----------------------------------

            report = (
                LLMResponseParser()
                .parse_json(
                    response
                )
            )

            print("=" * 80)
            print("FINANCIAL MANAGEMENT REPORT GENERATED")
            print("=" * 80)

            return report

        except Exception as ex:

            raise Exception(
                f"Financial Management Report Error: {str(ex)}"
            )