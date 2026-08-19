import logging
import requests

logger = logging.getLogger(__name__)


class ThresholdClient:

    THRESHOLD_CONFIG_URL = (
        "https://newaws.panzerplayground.com/api/reports/analytics/threshold-configs"
    )

    def get_threshold_configs(
        self,
        authorization: str,
        login_id: int,
        property_id: int,
        period: str
    ) -> dict:

        try:

            headers = {
                "Authorization": authorization
            }

            params = {
                "login_id": login_id,
                "property": int(property_id),
                "period": period
            }

            response = requests.get(
                self.THRESHOLD_CONFIG_URL,
                headers=headers,
                params=params,
                timeout=60
            )

            print("=" * 80)
            print("THRESHOLD API URL")
            print(response.url)
            print("=" * 80)

            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:

            logger.exception(
                "Failed to fetch threshold configurations."
            )

            raise Exception(
                f"Threshold API Error: {str(e)}"
            )