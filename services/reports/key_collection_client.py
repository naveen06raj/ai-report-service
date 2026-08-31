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
                "property_id": property_id
            }

            response = requests.post(
                self.KEY_COLLECTION_URL,
                headers=headers,
                data=payload,
                timeout=60
            )

            response.raise_for_status()

            key_collection = response.json()

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

            print("=" * 80)
            print("KEY COLLECTION API RESPONSE")
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

            raise Exception(
                f"Key Collection API Error: {str(ex)}"
            )

        except Exception as ex:

            logger.exception(
                "Unexpected Key Collection client error"
            )

            raise Exception(
                f"Key Collection Client Error: {str(ex)}"
            )