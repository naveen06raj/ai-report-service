import logging
import requests

logger = logging.getLogger(__name__)


class MonthlyReportClient:

    MONTHLY_REPORT_URL = (
        "https://newaws.panzerplayground.com/api/reports/analytics/monthly-reports-ratio"
    )

    TIMEOUT = 60

    def get_report(
        self,
        property_id: int,
        month: str,
        authorization: str
    ) -> dict:

        try:

            # ----------------------------------
            # Headers
            # ----------------------------------

            headers = {
                "Authorization": authorization,
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

            # ----------------------------------
            # Request Body
            # ----------------------------------

            payload = {
                "property_id": int(property_id),
                "month": month
            }

            print("=" * 80)
            print("MONTHLY REPORT API REQUEST")
            print("=" * 80)
            print(
                "URL:",
                self.MONTHLY_REPORT_URL
            )
            print(
                "PROPERTY ID:",
                property_id
            )
            print(
                "MONTH:",
                month
            )
            print("=" * 80)

            # ----------------------------------
            # API Request
            # ----------------------------------

            response = requests.post(
                self.MONTHLY_REPORT_URL,
                headers=headers,
                json=payload,
                timeout=self.TIMEOUT
            )

            print("=" * 80)
            print("MONTHLY REPORT API RESPONSE")
            print("=" * 80)
            print(
                "STATUS:",
                response.status_code
            )
            print(
                "BODY:",
                response.text
            )
            print("=" * 80)

            response.raise_for_status()

            result = response.json()

            # ----------------------------------
            # API Response Validation
            # ----------------------------------

            if result.get("status") is not True:

                raise Exception(
                    result.get(
                        "message",
                        "Monthly Report API returned an error."
                    )
                )

            return result

        except requests.exceptions.RequestException as ex:

            logger.exception(
                "Monthly Report API request failed"
            )

            raise Exception(
                f"Monthly Report API Error: {str(ex)}"
            )

        except ValueError as ex:

            logger.exception(
                "Invalid Monthly Report API response"
            )

            raise Exception(
                f"Monthly Report JSON Error: {str(ex)}"
            )

        except Exception as ex:

            logger.exception(
                "Unexpected Monthly Report client error"
            )

            raise Exception(
                f"Monthly Report Client Error: {str(ex)}"
            )