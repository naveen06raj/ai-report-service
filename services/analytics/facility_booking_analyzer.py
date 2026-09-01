from collections import Counter
from datetime import datetime


class FacilityBookingAnalyzer:

    def analyze(
        self,
        report_data: dict
    ) -> dict:

        # ----------------------------------
        # Validate Report Data
        # ----------------------------------

        if not isinstance(
            report_data,
            dict
        ):
            raise ValueError(
                "Expected report_data to be a dictionary"
            )

        # ----------------------------------
        # Get Booking Data
        # ----------------------------------

        # Direct API response
        #
        # {
        #     "response": 1,
        #     "message": "Success",
        #     "data": [...]
        # }

        if "data" in report_data:

            records = report_data.get(
                "data",
                []
            )

        # Wrapped response
        #
        # {
        #     "facility_bookings": {
        #         "data": [...]
        #     }
        # }

        elif "facility_bookings" in report_data:

            facility_bookings_response = (
                report_data.get(
                    "facility_bookings",
                    {}
                )
            )

            records = (
                facility_bookings_response.get(
                    "data",
                    []
                )
            )

        else:

            records = []

        if not isinstance(
            records,
            list
        ):
            raise ValueError(
                "Expected facility booking 'data' to be a list"
            )

        # ----------------------------------
        # Counters
        # ----------------------------------

        total_bookings = len(
            records
        )

        status_counter = Counter()

        facility_counter = Counter()

        monthly_bookings = Counter()

        total_revenue = 0.0

        paid_bookings = 0

        free_bookings = 0

        # ----------------------------------
        # Status Mapping
        # ----------------------------------

        status_mapping = {

            1: "Cancelled",

            2: "Confirmed",

            3: "New"

        }

        # ----------------------------------
        # Process Bookings
        # ----------------------------------

        for booking in records:

            if not isinstance(
                booking,
                dict
            ):
                continue

            # ----------------------------------
            # Submission Data
            # ----------------------------------

            submission = booking.get(
                "submissions",
                {}
            )

            if not isinstance(
                submission,
                dict
            ):
                submission = {}

            # ----------------------------------
            # Facility Type
            # ----------------------------------

            facility_data = booking.get(
                "type",
                {}
            )

            if not isinstance(
                facility_data,
                dict
            ):
                facility_data = {}

            facility = (
                facility_data.get(
                    "facility_type"
                )
                or "Unknown"
            )

            facility_counter[
                str(facility)
            ] += 1

            # ----------------------------------
            # Booking Status
            # ----------------------------------

            status = submission.get(
                "status"
            )

            try:

                status = int(
                    status
                )

            except (
                TypeError,
                ValueError
            ):

                status = None

            status_name = status_mapping.get(
                status,
                "Unknown"
            )

            status_counter[
                status_name
            ] += 1

            # ----------------------------------
            # Booking Date
            # ----------------------------------

            booking_date = submission.get(
                "booking_date"
            )

            if booking_date:

                try:

                    date_obj = datetime.strptime(
                        booking_date,
                        "%Y-%m-%d"
                    )

                    month = date_obj.strftime(
                        "%Y-%m"
                    )

                    monthly_bookings[
                        month
                    ] += 1

                except ValueError:

                    pass

            # ----------------------------------
            # Revenue
            # ----------------------------------

            booking_fee = (
                submission.get(
                    "booking_fee"
                )
                or 0
            )

            deposit_fee = (
                submission.get(
                    "deposit_fee"
                )
                or 0
            )

            try:

                booking_fee = float(
                    booking_fee
                )

            except (
                TypeError,
                ValueError
            ):

                booking_fee = 0.0

            try:

                deposit_fee = float(
                    deposit_fee
                )

            except (
                TypeError,
                ValueError
            ):

                deposit_fee = 0.0

            amount = (
                booking_fee +
                deposit_fee
            )

            total_revenue += amount

            # ----------------------------------
            # Paid / Free
            # ----------------------------------

            if amount > 0:

                paid_bookings += 1

            else:

                free_bookings += 1

        # ----------------------------------
        # Facility Distribution
        # ----------------------------------

        facility_bookings = []

        for (
            facility,
            count
        ) in facility_counter.most_common():

            percentage = (
                round(
                    (
                        count /
                        total_bookings
                    ) * 100,
                    2
                )
                if total_bookings
                else 0
            )

            facility_bookings.append({

                "facility":
                    facility,

                "count":
                    count,

                "percentage":
                    percentage

            })

        # ----------------------------------
        # Top Facility
        # ----------------------------------

        if facility_counter:

            (
                top_facility_name,
                top_count
            ) = (
                facility_counter.most_common(1)[0]
            )

            top_facility = {

                "facility":
                    top_facility_name,

                "count":
                    top_count,

                "percentage":
                    round(
                        (
                            top_count /
                            total_bookings
                        ) * 100,
                        2
                    )

            }

        else:

            top_facility = {

                "facility":
                    "",

                "count":
                    0,

                "percentage":
                    0

            }

        # ----------------------------------
        # Monthly Trend
        # ----------------------------------

        monthly_trend = []

        for (
            month,
            count
        ) in sorted(
            monthly_bookings.items()
        ):

            monthly_trend.append({

                "month":
                    month,

                "count":
                    count

            })

        # ----------------------------------
        # Final Analytics
        # ----------------------------------

        return {

            "total_bookings":
                total_bookings,

            "status_summary":
                dict(
                    status_counter
                ),

            "top_facility":
                top_facility,

            "facility_bookings":
                facility_bookings,

            "monthly_trend":
                monthly_trend,

            "revenue": {

                "total_revenue":
                    round(
                        total_revenue,
                        2
                    ),

                "paid_bookings":
                    paid_bookings,

                "free_bookings":
                    free_bookings

            }

        }