from services.reports.financial_report_client import (
    FinancialReportClient
)


class FinancialReportService:

    def get_report(
        self,
        login_id: int,
        authorization: str
    ) -> dict:

        try:

            return (
                FinancialReportClient()
                .get_report(
                    login_id=login_id,
                    authorization=authorization
                )
            )

        except Exception as ex:

            raise Exception(
                f"Failed to fetch financial report: {str(ex)}"
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

            return (
                FinancialReportClient()
                .get_invoice_view(
                    login_id=login_id,
                    invoice_id=invoice_id,
                    authorization=authorization
                )
            )

        except Exception as ex:

            raise Exception(
                f"Failed to fetch invoice view: {str(ex)}"
            )