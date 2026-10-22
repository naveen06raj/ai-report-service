
import logging
import requests

logger = logging.getLogger(__name__)


class PropertyListClient:

    PROPERTY_LIST_URL = (
        "https://newaws.panzerplayground.com/api/ai/propertylist"
    )

    def get_property_list(self, authorization: str) -> dict:
        try:
            headers = {
                "Authorization": authorization,
                "Accept": "application/json",
            }

            response = requests.get(
                self.PROPERTY_LIST_URL,
                headers=headers,
                timeout=30,
            )

            response.raise_for_status()
            result = response.json()

            if not isinstance(result, dict):
                raise ValueError(
                    "Property API returned an invalid response"
                )

            return result

        except requests.exceptions.RequestException as ex:
            logger.exception("Property List API request failed")
            raise Exception(
                f"Property List API Error: {ex}"
            ) from ex

        except ValueError as ex:
            logger.exception("Invalid Property List API response")
            raise Exception(
                f"Property List API returned invalid JSON: {ex}"
            ) from ex
