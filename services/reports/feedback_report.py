from services.reports.feedback_client import (
    FeedbackClient
)


class FeedbackReportService:

    def get_report(
        self,
        login_id: int,
        authorization: str
    ):

        return (
            FeedbackClient()
            .get_report(
                login_id=login_id,
                authorization=authorization
            )
        )