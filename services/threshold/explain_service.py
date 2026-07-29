import logging

from services.reports.threshold_client import ThresholdClient
from services.analytics.threshold_analyzer import ThresholdAnalyzer
from services.llm.prompt_builder import PromptBuilder
from services.llm.gemini_client import generate
from services.llm.llm_response_parser import LLMResponseParser

logger = logging.getLogger(__name__)


class ThresholdExplainService:

    def __init__(self):
        self.client = ThresholdClient()
        self.analyzer = ThresholdAnalyzer()
        self.prompt_builder = PromptBuilder()

    def generate(
        self,
        authorization: str,
        property_id: str,
        period: str,
        config_key: str
    ) -> dict:

        try:

            logger.info(
                "Generating AI explanation for threshold: %s",
                config_key
            )

            # --------------------------------------------------
            # Fetch Threshold Configurations
            # --------------------------------------------------

            threshold_response = self.client.get_threshold_configs(
                authorization=authorization
            )

            # --------------------------------------------------
            # Analyze Data
            # --------------------------------------------------

            analytics = self.analyzer.analyze(
                threshold_response
            )

            # --------------------------------------------------
            # Find Selected Metric
            # --------------------------------------------------

            metric = next(
                (
                    item
                    for item in analytics["thresholds"]
                    if item["config_key"] == config_key
                ),
                None
            )

            if metric is None:
                raise ValueError(
                    f"Threshold '{config_key}' not found."
                )

            # --------------------------------------------------
            # Add Request Context
            # --------------------------------------------------

            metric["property_id"] = property_id
            metric["period"] = period

            # --------------------------------------------------
            # Build Prompt
            # --------------------------------------------------

            prompt = self.prompt_builder.build_threshold_explain_prompt(
                metric
            )

            print("=" * 80)
            print("THRESHOLD EXPLAIN PROMPT")
            print("=" * 80)
            print(prompt)
            print("=" * 80)

            # --------------------------------------------------
            # Generate AI Response
            # --------------------------------------------------

            response = generate(prompt)

            print("=" * 80)
            print("RAW GEMINI RESPONSE")
            print("=" * 80)
            print(repr(response))
            print("=" * 80)

            # --------------------------------------------------
            # Parse JSON
            # --------------------------------------------------

            result = (
                LLMResponseParser()
                .parse_json(
                    response
                )
            )

            print("=" * 80)
            print("PARSED RESPONSE")
            print("=" * 80)
            print(result)
            print("=" * 80)

            return result

        except Exception as ex:

            logger.exception(
                "Threshold Explain failed"
            )

            raise