import logging
import requests

logger = logging.getLogger(__name__)


class FacilityBookingClient:

    TIMEOUT = 60

    FACILITY_OPTIONS_URL = (
        "https://newaws.panzerplayground.com/api/ai/facilityoptions"
    )

    FACILITY_LIST_URL = (
        "https://newaws.panzerplayground.com/api/ai/facilitylist"
    )

    def _post(
        self,
        url: str,
        login_id: int,
        property_id: int,
        start_date: str,
        end_date: str,
        authorization: str
    ) -> dict:

        headers = {
            "Authorization": authorization,
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        payload = {
            "login_id": login_id,
            "property_id": property_id,
            "start_date": start_date,
            "end_date": end_date
        }

        print("=" * 80)
        print("FACILITY API REQUEST")
        print("=" * 80)
        print("URL:", url)
        print("LOGIN ID:", login_id)
        print("PROPERTY ID:", property_id)
        print("START DATE:", start_date)
        print("END DATE:", end_date)
        print("PAYLOAD:", payload)
        print("=" * 80)

        response = requests.post(
            url,
            headers=headers,
            data=payload,
            timeout=self.TIMEOUT
        )

        print("=" * 80)
        print("FACILITY API RESPONSE")
        print("=" * 80)
        print("STATUS:", response.status_code)
        print("BODY:", response.text)
        print("=" * 80)

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
        property_id: int,
        start_date: str,
        end_date: str,
        authorization: str
    ) -> dict:

        try:

            # ----------------------------------
            # Facility Options
            # ----------------------------------

            facility_options = self._post(
                url=self.FACILITY_OPTIONS_URL,
                login_id=login_id,
                property_id=property_id,
                start_date=start_date,
                end_date=end_date,
                authorization=authorization
            )

            # ----------------------------------
            # Facility Booking List
            # ----------------------------------

            facility_bookings = self._post(
                url=self.FACILITY_LIST_URL,
                login_id=login_id,
                property_id=property_id,
                start_date=start_date,
                end_date=end_date,
                authorization=authorization
            )

            # ----------------------------------
            # Logging
            # ----------------------------------

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