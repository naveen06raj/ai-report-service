from services.reports.visitor_management_client import (
    VisitorManagementClient
)


class VisitorManagementReportService:

    def get_report(
        self,
        login_id: int,
        property_id: int,
        start_date: str,
        end_date: str,
        authorization: str
    ) -> dict:

        try:

            return (
                VisitorManagementClient()
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
                f"Failed to fetch visitor management report: {str(ex)}"
            )