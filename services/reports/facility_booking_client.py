import logging
import requests

logger = logging.getLogger(__name__)


class FacilityBookingClient:

    TIMEOUT = 60

    FACILITY_OPTIONS_URL = (
        "https://aereanew.panzerplayground.com/api/ops/v4/facilityoptions"
    )

    FACILITY_LIST_URL = (
        "https://aereanew.panzerplayground.com/api/ops/v4/facilitylist"
    )

    def _post(
        self,
        url: str,
        login_id: int,
        authorization: str
    ) -> dict:

        headers = {
            "Authorization": authorization,
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        payload = {
            "login_id": login_id
        }

        response = requests.post(
            url,
            headers=headers,
            data=payload,
            timeout=self.TIMEOUT
        )

        response.raise_for_status()

        result = response.json()

        if result.get("response") != 1:

            raise Exception(
                result.get(
                    "message",
                    "Facility API returned an error."
                )
            )

        return result

    def get_report(
        self,
        login_id: int,
        authorization: str
    ) -> dict:

        try:

            # ----------------------------------
            # Facility Options
            # ----------------------------------

            facility_options = self._post(
                self.FACILITY_OPTIONS_URL,
                login_id,
                authorization
            )

            # ----------------------------------
            # Facility Booking List
            # ----------------------------------

            facility_bookings = self._post(
                self.FACILITY_LIST_URL,
                login_id,
                authorization
            )

            logger.info(
                "Facility Report: %s facilities, %s bookings",
                len(
                    facility_options.get(
                        "options",
                        {}
                    )
                ),
                len(
                    facility_bookings.get(
                        "data",
                        []
                    )
                )
            )

            return {

                "facility_options":
                    facility_options,

                "facility_bookings":
                    facility_bookings

            }

        except requests.exceptions.RequestException as ex:

            logger.exception(
                "Facility Booking API request failed"
            )

            raise Exception(
                f"Facility Booking API Error: {str(ex)}"
            )

        except Exception as ex:

            logger.exception(
                "Unexpected facility booking client error"
            )

            raise Exception(
                f"Facility Booking Client Error: {str(ex)}"
            )