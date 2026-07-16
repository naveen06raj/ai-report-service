import logging
import requests

logger = logging.getLogger(__name__)


class FinancialReportClient:

    PAYMENT_OVERVIEW_URL = (
        "https://newaws.panzerplayground.com/api/ops/v4/paymentoverview"
    )

    INVOICE_SEARCH_URL = (
        "https://newaws.panzerplayground.com/api/ops/v4/report_search"
    )

    BATCH_LIST_URL = (
        "https://newaws.panzerplayground.com/api/ops/v4/batches"
    )

    INVOICE_VIEW_URL = (
    "https://newaws.panzerplayground.com/api/ops/v4/invoiceview"
)

    def _post(
        self,
        session,
        url,
        headers,
        payload
    ):

        response = session.post(
            url,
            headers=headers,
            data=payload,
            timeout=60
        )

        response.raise_for_status()

        result = response.json()

        if result.get("response") != 1:

            raise Exception(
                result.get(
                    "message",
                    "Unknown API Error"
                )
            )

        return result

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

            session = requests.Session()

            # --------------------------------------------------
            # Payment Overview
            # --------------------------------------------------

            payment_overview = self._post(
                session=session,
                url=self.PAYMENT_OVERVIEW_URL,
                headers=headers,
                payload={
                    "login_id": login_id
                }
            )

            # --------------------------------------------------
            # Invoice Search
            # --------------------------------------------------

            invoice_search = self._post(
                session=session,
                url=self.INVOICE_SEARCH_URL,
                headers=headers,
                payload={
                    "login_id": login_id,
                    "batch_file_no": "",
                    "invoice_no": "",
                    "building": "",
                    "unit": "",
                    "fromdate": "",
                    "todate": "",
                    "status": ""
                }
            )

            # --------------------------------------------------
            # Batch List
            # --------------------------------------------------

            batch_list = self._post(
                session=session,
                url=self.BATCH_LIST_URL,
                headers=headers,
                payload={
                    "login_id": login_id
                }
            )

            # --------------------------------------------------
            # Debug
            # --------------------------------------------------

            print("=" * 80)
            print("FINANCIAL REPORT")
            print("=" * 80)

            print(
                "Payment Overview :",
                payment_overview.get("response")
            )

            print(
                "Invoice Records :",
                len(
                    invoice_search.get(
                        "data",
                        []
                    )
                )
            )

            print(
                "Batch Records :",
                len(
                    batch_list.get(
                        "data",
                        []
                    )
                )
            )

            print("=" * 80)

            return {

                "payment_overview":
                    payment_overview,

                "invoice_search":
                    invoice_search,

                "batch_list":
                    batch_list

            }

        except requests.exceptions.RequestException as ex:

            logger.exception(
                "Financial Report API request failed"
            )

            raise Exception(
                f"Financial Report API Error: {str(ex)}"
            )

        except Exception as ex:

            logger.exception(
                "Unexpected Financial Report client error"
            )

            raise Exception(
                f"Financial Report Client Error: {str(ex)}"
            )

        # --------------------------------------------------
    # Invoice View
    # --------------------------------------------------

    def get_invoice_view(
        self,
        login_id: int,
        invoice_id: int,
        authorization: str
    ) -> dict:

        try:

            headers = {
                "Authorization": authorization,
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded"
            }

            session = requests.Session()

            invoice_view = self._post(
                session=session,
                url=self.INVOICE_VIEW_URL,
                headers=headers,
                payload={
                    "login_id": login_id,
                    "id": invoice_id
                }
            )

            print("=" * 80)
            print("INVOICE VIEW")
            print("=" * 80)

            print(
                "Invoice Response :",
                invoice_view.get("response")
            )

            print("=" * 80)

            return invoice_view

        except requests.exceptions.RequestException as ex:

            logger.exception(
                "Invoice View API request failed"
            )

            raise Exception(
                f"Invoice View API Error: {str(ex)}"
            )

        except Exception as ex:

            logger.exception(
                "Unexpected Invoice View client error"
            )

            raise Exception(
                f"Invoice View Client Error: {str(ex)}"
            )