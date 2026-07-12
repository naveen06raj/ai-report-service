from services.reports.visitor_management_client import (
    VisitorManagementClient
)


class VisitorManagementReportService:

    def get_report(
        self,
        login_id: int,
        authorization: str
    ) -> dict:

        try:

            return (
                VisitorManagementClient()
                .get_report(
                    login_id=login_id,
                    authorization=authorization
                )
            )

        except Exception as ex:

            raise Exception(
                f"Failed to fetch visitor management report: {str(ex)}"
            )