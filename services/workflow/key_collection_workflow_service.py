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


class KeyCollectionWorkflowService:

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
                .build_key_collection_workflow_prompt(
                    analytics
                )
            )

            print("=" * 80)
            print("KEY COLLECTION WORKFLOW PROMPT")
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

            workflow = (
                LLMResponseParser()
                .parse_json(
                    response
                )
            )

            print("=" * 80)
            print("KEY COLLECTION WORKFLOW GENERATED")
            print("=" * 80)
            print(workflow)
            print("=" * 80)

            return workflow

        except Exception as ex:

            logger.exception(
                "Key Collection workflow generation failed"
            )

            return {

                "workflow": [

                    {
                        "priority":
                            "Low",

                        "task":
                            "Workflow generation failed.",

                        "owner":
                            "System",

                        "reason":
                            str(ex)
                    }

                ]

            }