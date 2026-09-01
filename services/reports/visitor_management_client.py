import logging
import requests

logger = logging.getLogger(__name__)


class VisitorManagementClient:

    VISITOR_SUMMARY_URL = (
        "https://newaws.panzerplayground.com/api/ai/visitorsummary"
    )

    VISITOR_TYPES_URL = (
        "https://newaws.panzerplayground.com/api/ai/visitor_types"
    )

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

            # ----------------------------------
            # Payload
            # ----------------------------------

            payload = {
                "login_id": login_id,
                "property_id": property_id
            }

            # Dates are optional
            if start_date:
                payload["start_date"] = start_date

            if end_date:
                payload["end_date"] = end_date

            print("=" * 80)
            print("VISITOR MANAGEMENT REQUEST")
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
                "AUTH EXISTS:",
                authorization is not None
            )

            print(
                "PAYLOAD:",
                payload
            )

            print("=" * 80)

            # --------------------------------------------------
            # Visitor Summary
            # --------------------------------------------------

            summary_response = requests.post(
                self.VISITOR_SUMMARY_URL,
                headers=headers,
                data=payload,
                timeout=60
            )

            print("=" * 80)
            print("VISITOR SUMMARY API")
            print("=" * 80)

            print(
                "STATUS:",
                summary_response.status_code
            )

            print(
                "BODY:",
                summary_response.text
            )

            print("=" * 80)

            summary_response.raise_for_status()

            visitor_summary = (
                summary_response.json()
            )

            # --------------------------------------------------
            # Visitor Types
            # --------------------------------------------------

            types_response = requests.post(
                self.VISITOR_TYPES_URL,
                headers=headers,
                data=payload,
                timeout=60
            )

            print("=" * 80)
            print("VISITOR TYPES API")
            print("=" * 80)

            print(
                "STATUS:",
                types_response.status_code
            )

            print(
                "BODY:",
                types_response.text
            )

            print("=" * 80)

            types_response.raise_for_status()

            visitor_types = (
                types_response.json()
            )

            # --------------------------------------------------
            # Success
            # --------------------------------------------------

            print("=" * 80)
            print("VISITOR MANAGEMENT SUCCESS")
            print("=" * 80)

            print(
                "TOTAL VISITORS:",
                len(
                    visitor_summary.get(
                        "data",
                        []
                    )
                )
            )

            print(
                "TOTAL TYPES:",
                len(
                    visitor_types.get(
                        "types",
                        []
                    )
                )
            )

            print("=" * 80)

            return {
                "visitor_summary":
                    visitor_summary,

                "visitor_types":
                    visitor_types
            }

        except requests.exceptions.RequestException as ex:

            print("=" * 80)
            print("REQUEST FAILED")
            print("=" * 80)

            if ex.response is not None:

                print(
                    "STATUS:",
                    ex.response.status_code
                )

                print(
                    "BODY:",
                    ex.response.text
                )

            logger.exception(
                "Visitor Management API request failed"
            )

            raise Exception(
                f"Visitor Management API Error: {str(ex)}"
            )

        except ValueError as ex:

            logger.exception(
                "Invalid JSON returned by Visitor Management API"
            )

            raise Exception(
                f"Visitor Management API returned invalid JSON: {str(ex)}"
            )

        except Exception as ex:

            logger.exception(
                "Unexpected Visitor Management client error"
            )

            raise Exception(
                f"Visitor Management Client Error: {str(ex)}"
            )