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


class KeyCollectionRecommendationService:

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
                .build_key_collection_recommendation_prompt(
                    analytics
                )
            )

            print("=" * 80)
            print("KEY COLLECTION RECOMMENDATION PROMPT")
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

            recommendations = (
                LLMResponseParser()
                .parse_json(
                    response
                )
            )

            print("=" * 80)
            print("KEY COLLECTION RECOMMENDATIONS")
            print("=" * 80)
            print(recommendations)
            print("=" * 80)

            return recommendations

        except Exception as ex:

            logger.exception(
                "Key Collection recommendation generation failed"
            )

            return {

                "overall_status":
                    "Unavailable",

                "summary":
                    "Unable to generate recommendations.",

                "recommendations": [

                    {
                        "priority":
                            "Low",

                        "title":
                            "Recommendation Generation Failed",

                        "description":
                            str(ex)
                    }

                ]
            }