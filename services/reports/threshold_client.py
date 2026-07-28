import logging
import requests

logger = logging.getLogger(__name__)


class ThresholdClient:

    THRESHOLD_CONFIG_URL = (
        "https://newaws.panzerplayground.com/api/reports/analytics/threshold-configs"
    )

    def get_threshold_configs(
        self,
        authorization: str
    ) -> dict:

        try:

            headers = {
                "Authorization": authorization
            }

            response = requests.get(
                self.THRESHOLD_CONFIG_URL,
                headers=headers,
                timeout=60
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:

            logger.exception(
                "Failed to fetch threshold configurations."
            )

            raise Exception(
                f"Threshold API Error: {str(e)}"
            )