import logging

from services.reports.monthly_report_client import (
    MonthlyReportClient
)

from services.analytics.monthly_report_analyzer import (
    MonthlyReportAnalyzer
)

from services.llm.prompt_builder import (
    PromptBuilder
)

from services.llm.gemini_client import (
    generate
)

logger = logging.getLogger(__name__)


class MonthlyReportService:

    def __init__(self):

        self.client = MonthlyReportClient()

        self.analyzer = MonthlyReportAnalyzer()

        self.prompt_builder = PromptBuilder()

    def generate(
        self,
        property_id: int,
        month: str,
        authorization: str
    ) -> str:

        try:

            # ----------------------------------
            # Get API Data
            # ----------------------------------

            report_data = (
                self.client
                .get_report(
                    property_id=property_id,
                    month=month,
                    authorization=authorization
                )
            )

            print("=" * 80)
            print("MONTHLY REPORT API DATA")
            print("=" * 80)
            print(report_data)
            print("=" * 80)

            # ----------------------------------
            # Analyze
            # ----------------------------------

            analytics = (
                self.analyzer
                .analyze(
                    report_data
                )
            )

            print("=" * 80)
            print("MONTHLY REPORT ANALYTICS")
            print("=" * 80)
            print(analytics)
            print("=" * 80)

            # ----------------------------------
            # Build Prompt
            # ----------------------------------

            prompt = (
                self.prompt_builder
                .build_monthly_report_prompt(
                    analytics_data=analytics
                )
            )

            print("=" * 80)
            print("MONTHLY REPORT PROMPT")
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
            print("MONTHLY REPORT RESPONSE")
            print("=" * 80)
            print(response)
            print("=" * 80)

            return response.strip()

        except Exception as ex:

            logger.exception(
                "Monthly Report generation failed"
            )

            raise Exception(
                f"Monthly Report Error: {str(ex)}"
            )