import json
import logging
import requests

logger = logging.getLogger(__name__)


class KeyCollectionClient:

    KEY_COLLECTION_URL = (
        "https://newaws.panzerplayground.com/api/ai/keycollectionlist"
    )

    def get_report(
        self,
        login_id: int,
        property_id: int,
        start_date: str,
        end_date: str,
        authorization: str
    ) -> dict:

        try:

            headers = {
                "Authorization": authorization,
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded"
            }

            payload = {
                "login_id": login_id,
                "property_id": property_id,
                "start_date": start_date,
                "end_date": end_date
            }

            # ----------------------------------
            # Debug Request
            # ----------------------------------

            print("=" * 80)
            print("KEY COLLECTION API REQUEST")
            print("=" * 80)

            print(
                "Login ID    :",
                login_id
            )

            print(
                "Property ID :",
                property_id
            )

            print(
                "Start Date  :",
                start_date
            )

            print(
                "End Date    :",
                end_date
            )

            print(
                "Payload     :",
                payload
            )

            print("=" * 80)

            # ----------------------------------
            # API Request
            # ----------------------------------

            response = requests.post(
                self.KEY_COLLECTION_URL,
                headers=headers,
                data=payload,
                timeout=60
            )

            print("=" * 80)
            print("KEY COLLECTION API RESPONSE")
            print("=" * 80)

            print(
                "Status:",
                response.status_code
            )

            print(
                "Body:",
                response.text
            )

            print("=" * 80)

            response.raise_for_status()

            key_collection = response.json()

            # ----------------------------------
            # Debug JSON
            # ----------------------------------

            print("=" * 80)
            print("KEY COLLECTION API JSON")
            print("=" * 80)

            print(
                json.dumps(
                    key_collection,
                    indent=4
                )
            )

            print("=" * 80)

            return key_collection

        except requests.exceptions.RequestException as ex:

            logger.exception(
                "Key Collection API request failed"
            )

            if ex.response is not None:

                print("=" * 80)
                print("KEY COLLECTION API ERROR")
                print("=" * 80)

                print(
                    "Status:",
                    ex.response.status_code
                )

                print(
                    "Body:",
                    ex.response.text
                )

                print("=" * 80)

            raise Exception(
                f"Key Collection API Error: {str(ex)}"
            )

        except ValueError as ex:

            logger.exception(
                "Invalid JSON returned by Key Collection API"
            )

            raise Exception(
                f"Key Collection API returned invalid JSON: {str(ex)}"
            )

        except Exception as ex:

            logger.exception(
                "Unexpected Key Collection client error"
            )

            raise Exception(
                f"Key Collection Client Error: {str(ex)}"
            )