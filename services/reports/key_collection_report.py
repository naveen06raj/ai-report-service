from services.reports.key_collection_client import (
    KeyCollectionClient
)


class KeyCollectionReportService:

    def get_report(
        self,
        login_id: int,
        property_id: int,
        authorization: str
    ) -> dict:

        try:

            return (
                KeyCollectionClient()
                .get_report(
                    login_id=login_id,
                    property_id=property_id,
                    authorization=authorization
                )
            )

        except Exception as ex:

            raise Exception(
                f"Failed to fetch key collection report: {str(ex)}"
            )