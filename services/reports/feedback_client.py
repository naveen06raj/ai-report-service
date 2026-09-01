import json
import logging
import requests

logger = logging.getLogger(__name__)


class FeedbackClient:

    FEEDBACK_OPTIONS_URL = (
        "https://newaws.panzerplayground.com/api/ai/feedbackoptions"
    )

    FEEDBACK_LIST_URL = (
        "https://newaws.panzerplayground.com/api/ai/feedbacklist"
    )

    TIMEOUT = 60

    def get_report(
        self,
        login_id: int,
        property_id: int,
        authorization: str,
        start_date: str = None,
        end_date: str = None
    ) -> dict:

        try:

            headers = {
                "Authorization": authorization,
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded"
            }

            # ==================================================
            # Payload
            # ==================================================

            payload = {
                "login_id": login_id,
                "property_id": property_id
            }

            # Dates are optional
            if start_date:
                payload["start_date"] = start_date

            if end_date:
                payload["end_date"] = end_date

            # ==================================================
            # Debug Request
            # ==================================================

            print("=" * 80)
            print("FEEDBACK API REQUEST")
            print("=" * 80)

            print(
                "LOGIN ID:",
                login_id
            )

            print(
                "PROPERTY ID:",
                property_id
            )

            print(
                "START DATE:",
                start_date
            )

            print(
                "END DATE:",
                end_date
            )

            print(
                "OPTIONS URL:",
                self.FEEDBACK_OPTIONS_URL
            )

            print(
                "LIST URL:",
                self.FEEDBACK_LIST_URL
            )

            print(
                "PAYLOAD:",
                payload
            )

            print("=" * 80)

            # ==================================================
            # Feedback Options
            # ==================================================

            options_response = requests.post(
                self.FEEDBACK_OPTIONS_URL,
                headers=headers,
                data=payload,
                timeout=self.TIMEOUT
            )

            print("=" * 80)
            print("FEEDBACK OPTIONS RESPONSE")
            print("=" * 80)

            print(
                "STATUS:",
                options_response.status_code
            )

            print(
                "BODY:",
                options_response.text
            )

            print("=" * 80)

            options_response.raise_for_status()

            feedback_options = (
                options_response.json()
            )

            # ==================================================
            # Feedback List
            # ==================================================

            list_response = requests.post(
                self.FEEDBACK_LIST_URL,
                headers=headers,
                data=payload,
                timeout=self.TIMEOUT
            )

            print("=" * 80)
            print("FEEDBACK LIST RESPONSE")
            print("=" * 80)

            print(
                "STATUS:",
                list_response.status_code
            )

            print(
                "BODY:",
                list_response.text
            )

            print("=" * 80)

            list_response.raise_for_status()

            feedback_list = (
                list_response.json()
            )

            # ==================================================
            # Debug JSON
            # ==================================================

            print("=" * 80)
            print("FEEDBACK LIST API JSON")
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

            if ex.response is not None:

                print("=" * 80)
                print("FEEDBACK API ERROR RESPONSE")
                print("=" * 80)

                print(
                    "STATUS:",
                    ex.response.status_code
                )

                print(
                    "BODY:",
                    ex.response.text
                )

                print("=" * 80)

            raise Exception(
                f"Feedback API Error: {str(ex)}"
            )

        except ValueError as ex:

            logger.exception(
                "Invalid JSON returned by Feedback API"
            )

            raise Exception(
                f"Feedback API returned invalid JSON: {str(ex)}"
            )

        except Exception as ex:

            logger.exception(
                "Unexpected feedback client error"
            )

            raise Exception(
                f"Feedback Client Error: {str(ex)}"
            )