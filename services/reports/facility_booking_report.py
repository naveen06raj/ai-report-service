from services.reports.facility_booking_client import (
    FacilityBookingClient
)


class FacilityBookingReportService:

    def get_report(
        self,
        login_id: int,
        authorization: str
    ) -> dict:

        try:

            return (
                FacilityBookingClient()
                .get_report(
                    login_id=login_id,
                    authorization=authorization
                )
            )

        except Exception as ex:

            raise Exception(
                f"Failed to fetch facility booking report: {str(ex)}"
            )