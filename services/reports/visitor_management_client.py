import logging
import requests

logger = logging.getLogger(__name__)


class VisitorManagementClient:

    VISITOR_SUMMARY_URL = (
        "https://aereanew.panzerplayground.com/api/ops/v4/visitorsummary"
    )
#api
    VISITOR_TYPES_URL = (
        "https://aereanew.panzerplayground.com/api/ops/v4/visitor_types"
    )

    def get_report(
        self,
        login_id: int,
        authorization: str
    ) -> dict:

        try:

            headers = {
                "Authorization": authorization,
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded"
            }

            payload = {
                "login_id": login_id
            }

            # ----------------------------------
            # Visitor Summary
            # ----------------------------------

            summary_response = requests.post(
                self.VISITOR_SUMMARY_URL,
                headers=headers,
                data=payload,
                timeout=60
            )

            summary_response.raise_for_status()

            visitor_summary = (
                summary_response.json()
            )

            # ----------------------------------
            # Visitor Types
            # ----------------------------------

            types_response = requests.post(
                self.VISITOR_TYPES_URL,
                headers=headers,
                data=payload,
                timeout=60
            )

            types_response.raise_for_status()

            visitor_types = (
                types_response.json()
            )

            # ----------------------------------
            # Debug
            # ----------------------------------

            print("=" * 80)
            print("VISITOR MANAGEMENT REPORT")
            print("=" * 80)

            print(
                "TOTAL VISITORS :",
                len(
                    visitor_summary.get(
                        "data",
                        []
                    )
                )
            )

            print(
                "TOTAL VISITOR TYPES :",
                len(
                    visitor_types.get(
                        "types",
                        []
                    )
                )
            )

            print("=" * 80)

            # Uncomment while debugging
            #
            # import json
            # print(json.dumps(visitor_summary, indent=4))
            # print(json.dumps(visitor_types, indent=4))

            return {

                "visitor_summary":
                    visitor_summary,

                "visitor_types":
                    visitor_types

            }

        except requests.exceptions.RequestException as ex:

            logger.exception(
                "Visitor Management API request failed"
            )

            raise Exception(
                f"Visitor Management API Error: {str(ex)}"
            )

        except Exception as ex:

            logger.exception(
                "Unexpected Visitor Management client error"
            )

            raise Exception(
                f"Visitor Management Client Error: {str(ex)}"
            )