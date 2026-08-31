from services.reports.feedback_client import (
    FeedbackClient
)


class FeedbackReportService:

    def get_report(
        self,
        login_id: int,
        property_id: int,
        authorization: str
    ) -> dict:

        try:

            return (
                FeedbackClient()
                .get_report(
                    login_id=login_id,
                    property_id=property_id,
                    authorization=authorization
                )
            )

        except Exception as ex:

            raise Exception(
                f"Failed to fetch feedback report: {str(ex)}"
            )