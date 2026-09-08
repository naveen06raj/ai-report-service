import logging
import requests

logger = logging.getLogger(__name__)


class FinancialReportClient:

    # ============================================================
    # Main Financial API
    # Used by:
    # 1. Financial Overview AI Report
    # 2. Financial Chatbot
    # ============================================================

    INVOICES_URL = (
        "https://newaws.panzerplayground.com/api/ai/invoices"
    )

    # ============================================================
    # Chatbot APIs
    # ============================================================

    INVOICE_VIEW_URL = (
        "https://newaws.panzerplayground.com/api/ai/invoiceview"
    )

    INVOICE_SEARCH_URL = (
        "https://newaws.panzerplayground.com/api/ai/report_search"
    )

    # ============================================================
    # Common POST method
    # ============================================================

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

    # ============================================================
    # Get Invoices
    #
    # Main API for Financial AI
    #
    # Dates are optional because:
    # - Financial Report can use dates
    # - Financial Chatbot may not need dates
    # ============================================================

    def get_invoices(
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

            session = requests.Session()

            payload = {
                "login_id": login_id,
                "property_id": property_id
            }

            # Add date filters only when provided.
            if start_date:
                payload["start_date"] = start_date

            if end_date:
                payload["end_date"] = end_date

            logger.info(
                "Calling Financial Invoices API"
            )

            logger.info(
                "Financial Invoices Payload: %s",
                payload
            )

            result = self._post(
                session=session,
                url=self.INVOICES_URL,
                headers=headers,
                payload=payload
            )

            invoices = (
                result
                .get("data", {})
                .get("invoices", [])
            )

            logger.info(
                "Financial invoice records received: %s",
                len(invoices)
            )

            return result

        except requests.exceptions.RequestException as ex:

            logger.exception(
                "Financial Invoices API request failed"
            )

            raise Exception(
                f"Financial Invoices API Error: {str(ex)}"
            )

        except Exception as ex:

            logger.exception(
                "Unexpected Financial Invoices client error"
            )

            raise Exception(
                f"Financial Invoices Client Error: {str(ex)}"
            )

    # ============================================================
    # Financial Report
    #
    # Uses ONLY /api/ai/invoices as the main data source.
    # ============================================================

    def get_report(
        self,
        login_id: int,
        property_id: int,
        authorization: str,
        start_date: str = None,
        end_date: str = None
    ) -> dict:

        try:

            invoices = self.get_invoices(
                login_id=login_id,
                property_id=property_id,
                authorization=authorization,
                start_date=start_date,
                end_date=end_date
            )

            invoice_records = (
                invoices
                .get("data", {})
                .get("invoices", [])
            )

            logger.info(
                "Financial report data contains %s invoices",
                len(invoice_records)
            )

            return {
                "invoices": invoices
            }

        except Exception as ex:

            logger.exception(
                "Financial Report client error"
            )

            raise Exception(
                f"Financial Report Client Error: {str(ex)}"
            )

    # ============================================================
    # Invoice View
    #
    # Used by Financial Chatbot when the user asks about
    # one specific invoice.
    # ============================================================

    def get_invoice_view(
        self,
        login_id: int,
        property_id: int,
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

            payload = {
                "login_id": login_id,
                "property_id": property_id,
                "id": invoice_id
            }

            logger.info(
                "Calling Invoice View API"
            )

            logger.info(
                "Invoice View Payload: %s",
                payload
            )

            result = self._post(
                session=session,
                url=self.INVOICE_VIEW_URL,
                headers=headers,
                payload=payload
            )

            return result

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

    # ============================================================
    # Invoice Search
    #
    # Used by Financial Chatbot when the user wants to search
    # or filter invoices.
    # ============================================================

    def search_invoices(
        self,
        login_id: int,
        property_id: int,
        authorization: str,
        batch_file_no: str = "",
        invoice_no: str = "",
        building: str = "",
        unit: str = "",
        fromdate: str = "",
        todate: str = "",
        status: str = ""
    ) -> dict:

        try:

            headers = {
                "Authorization": authorization,
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded"
            }

            session = requests.Session()

            payload = {
                "login_id": login_id,
                "property_id": property_id,
                "batch_file_no": batch_file_no,
                "invoice_no": invoice_no,
                "building": building,
                "unit": unit,
                "fromdate": fromdate,
                "todate": todate,
                "status": status
            }

            logger.info(
                "Calling Invoice Search API"
            )

            logger.info(
                "Invoice Search Payload: %s",
                payload
            )

            result = self._post(
                session=session,
                url=self.INVOICE_SEARCH_URL,
                headers=headers,
                payload=payload
            )

            return result

        except requests.exceptions.RequestException as ex:

            logger.exception(
                "Invoice Search API request failed"
            )

            raise Exception(
                f"Invoice Search API Error: {str(ex)}"
            )

        except Exception as ex:

            logger.exception(
                "Unexpected Invoice Search client error"
            )

            raise Exception(
                f"Invoice Search Client Error: {str(ex)}"
            )