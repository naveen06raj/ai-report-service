import json
import logging
import requests

logger = logging.getLogger(__name__)


class FeedbackClient:

    FEEDBACK_OPTIONS_URL = (
        "https://aereanew.panzerplayground.com/api/ops/v4/feedbackoptions"
    )

    FEEDBACK_LIST_URL = (
        "https://aereanew.panzerplayground.com/api/ops/v4/feedbacklist"
    )

    def get_report(
        self,
        login_id: int,
        authorization: str
    ) -> dict:

        try:

            headers = {
                "Authorization": authorization,
                "Accept": "application/json"
            }

            payload = {
                "login_id": login_id
            }

            # ----------------------------------
            # Feedback Types
            # ----------------------------------

            options_response = requests.post(
                self.FEEDBACK_OPTIONS_URL,
                headers=headers,
                data=payload,
                timeout=60
            )

            options_response.raise_for_status()

            feedback_options = (
                options_response.json()
            )

            # ----------------------------------
            # Feedback List
            # ----------------------------------

            list_response = requests.post(
                self.FEEDBACK_LIST_URL,
                headers=headers,
                data=payload,
                timeout=60
            )

            list_response.raise_for_status()

            feedback_list = (
                list_response.json()
            )

            # ----------------------------------
            # DEBUG
            # ----------------------------------

            print("=" * 80)
            print("FEEDBACK LIST API RESPONSE")
            print("=" * 80)
            print(
                json.dumps(
                    feedback_list,
                    indent=4
                )
            )
            print("=" * 80)

            return {
                "feedback_options": feedback_options,
                "feedback_list": feedback_list
            }

        except requests.exceptions.RequestException as ex:

            logger.exception(
                "Feedback API request failed"
            )

            raise Exception(
                f"Feedback API Error: {str(ex)}"
            )

        except Exception as ex:

            logger.exception(
                "Unexpected feedback client error"
            )

            raise Exception(
                f"Feedback Client Error: {str(ex)}"
            )