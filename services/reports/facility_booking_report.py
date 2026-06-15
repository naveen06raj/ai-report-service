from services.reports.report_client import (
    ReportClient
)


class FacilityBookingReportService:

    def get_report(
        self,
        property_id: str,
        period: str,
        authorization: str
    ):

        try:

            report = (
                ReportClient()
                .get_report(
                    property_id=property_id,
                    period=period,
                    authorization=authorization
                )
            )

            return report

        except Exception as ex:

            raise Exception(
                f"Failed to fetch facility booking report: {str(ex)}"
            )