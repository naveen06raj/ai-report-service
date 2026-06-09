import json
import logging

from pathlib import Path

logger = logging.getLogger(__name__)


class PromptBuilder:

    def build_prompt(
        self,
        prompt_file: str,
        placeholders: dict
    ) -> str:

        try:

            project_root = (
                Path(__file__)
                .resolve()
                .parents[2]
            )

            prompt_path = (
                project_root /
                prompt_file
            )

            if not prompt_path.exists():

                raise FileNotFoundError(
                    f"Prompt file not found: {prompt_path}"
                )

            with open(
                prompt_path,
                "r",
                encoding="utf-8"
            ) as file:

                template = file.read()

            for key, value in placeholders.items():

                if isinstance(
                    value,
                    (dict, list)
                ):

                    value = json.dumps(
                        value,
                        indent=4
                    )

                template = template.replace(
                    f"{{{key}}}",
                    str(value)
                )

            return template

        except Exception as ex:

            logger.exception(
                "Failed to build prompt"
            )

            raise Exception(
                f"Prompt Builder Error: {str(ex)}"
            )

    # --------------------------------------------------
    # Summary Prompt
    # --------------------------------------------------

    def build_feedback_summary_prompt(
        self,
        analytics_data: dict
    ) -> str:

        return self.build_prompt(
            prompt_file=
            "prompts/summary/resident_feedback.txt",
            placeholders={
                "analytics_data":
                    analytics_data
            }
        )

    # --------------------------------------------------
    # Chat Prompt
    # --------------------------------------------------

    def build_feedback_chat_prompt(
        self,
        report_data: dict,
        question: str
    ) -> str:

        return self.build_prompt(
            prompt_file=
            "prompts/chat/feedback_chat.txt",
            placeholders={
                "report_data":
                    report_data,

                "question":
                    question
            }
        )

    # --------------------------------------------------
    # Anomaly Prompt
    # --------------------------------------------------

    def build_feedback_anomaly_prompt(
        self,
        analytics_data: dict
    ) -> str:

        return self.build_prompt(
            prompt_file=
            "prompts/anomaly/feedback_anomaly.txt",
            placeholders={
                "analytics_data":
                    analytics_data
            }
        )

    # --------------------------------------------------
    # Management Report Prompt
    # --------------------------------------------------

    def build_feedback_management_report_prompt(
        self,
        analytics_data: dict
    ) -> str:

        return self.build_prompt(
            prompt_file=
            "prompts/management_report/feedback_management_report.txt",
            placeholders={
                "analytics_data":
                    analytics_data
            }
        )

    # --------------------------------------------------
    # Router Prompt
    # --------------------------------------------------

    def build_router_prompt(
        self,
        question: str
    ) -> str:

        return self.build_prompt(
            prompt_file=
            "prompts/chat/router_prompt.txt",
            placeholders={
                "question":
                    question
            }
        )