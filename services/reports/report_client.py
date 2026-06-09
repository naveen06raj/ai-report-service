import requests
import logging

logger = logging.getLogger(__name__)


class ReportClient:

    REPORT_API_URL = (
        "https://aereanew.panzerplayground.com/api/reports/properties"
    )

    def get_report(
        self,
        property_id: str,
        period: str,
        authorization: str
    ) -> dict:

        try:

            headers = {
                "Authorization": authorization,
                "Accept": "application/json"
            }

            payload = {
                "property": property_id,
                "period": period
            }

            response = requests.post(
                self.REPORT_API_URL,
                json=payload,
                headers=headers,
                timeout=60
            )

            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as ex:

            logger.exception(
                "Report API request failed"
            )

            raise Exception(
                f"Report API Error: {str(ex)}"
            )

        except Exception as ex:

            logger.exception(
                "Unexpected report client error"
            )

            raise Exception(
                f"Report Client Error: {str(ex)}"
            )