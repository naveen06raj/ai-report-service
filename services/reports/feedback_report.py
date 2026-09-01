from services.reports.feedback_client import (
    FeedbackClient
)


class FeedbackReportService:

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
                FeedbackClient()
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
                f"Failed to fetch feedback report: {str(ex)}"
            )