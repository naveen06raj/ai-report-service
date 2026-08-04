from services.reports.key_collection_client import (
    KeyCollectionClient
)


class KeyCollectionReportService:

    def get_report(
        self,
        login_id: int,
        authorization: str
    ):

        return (
            KeyCollectionClient()
            .get_report(
                login_id=login_id,
                authorization=authorization
            )
        )