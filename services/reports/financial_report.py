from services.reports.financial_report_client import (
    FinancialReportClient
)


class FinancialReportService:

    def get_report(
        self,
        login_id: int,
        property_id: int,
        authorization: str,
        start_date: str = None,
        end_date: str = None
    ) -> dict:

        try:

            return (
                FinancialReportClient()
                .get_report(
                    login_id=login_id,
                    property_id=property_id,
                    start_date=start_date,
                    end_date=end_date,
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
        property_id: int,
        invoice_id: int,
        authorization: str
    ) -> dict:

        try:

            return (
                FinancialReportClient()
                .get_invoice_view(
                    login_id=login_id,
                    property_id=property_id,
                    invoice_id=invoice_id,
                    authorization=authorization
                )
            )

        except Exception as ex:

            raise Exception(
                f"Failed to fetch invoice view: {str(ex)}"
            )