from services.reports.report_client import (
    ReportClient
)


class VisitorManagementReportService:

    def get_report(
        self,
        property_id: str,
        period: str,
        authorization: str
    ):

        return (
            ReportClient()
            .get_report(
                property_id=property_id,
                period=period,
                authorization=authorization
            )
        )