import logging

logger = logging.getLogger(__name__)


class FacilityBookingAnalyzer:

    def analyze(
        self,
        report_data: dict
    ) -> dict:
        """
        Analyze facility booking data and prepare
        analytics for AI summary generation.
        """

        try:

            property_data = report_data["data"][0]

            facility_data = property_data.get(
                "facility_bookings",
                {}
            )

            total_bookings = facility_data.get(
                "total",
                0
            )

            facilities = facility_data.get(
                "by_facility",
                []
            )

            monthly_trend = facility_data.get(
                "monthly_trend",
                []
            )

            # ------------------------------------------
            # Sort Facilities
            # ------------------------------------------

            facilities = sorted(
                facilities,
                key=lambda x: x.get(
                    "bookings",
                    0
                ),
                reverse=True
            )

            # ------------------------------------------
            # Popular Facilities
            # ------------------------------------------

            top_facilities = []

            for facility in facilities[:5]:

                top_facilities.append(
                    {
                        "facility":
                            facility.get(
                                "facility",
                                "Unknown"
                            ),

                        "bookings":
                            facility.get(
                                "bookings",
                                0
                            )
                    }
                )

            # ------------------------------------------
            # Unused Facilities
            # ------------------------------------------

            unused_facilities = []

            for facility in facilities:

                bookings = facility.get(
                    "bookings",
                    0
                )

                if bookings == 0:

                    unused_facilities.append(
                        facility.get(
                            "facility",
                            "Unknown"
                        )
                    )

            # ------------------------------------------
            # Low Usage Facilities
            # ------------------------------------------

            low_usage_facilities = []

            for facility in facilities:

                bookings = facility.get(
                    "bookings",
                    0
                )

                if (
                    bookings > 0
                    and bookings <= 5
                ):

                    low_usage_facilities.append(
                        {
                            "facility":
                                facility.get(
                                    "facility",
                                    "Unknown"
                                ),

                            "bookings":
                                bookings
                        }
                    )

            # ------------------------------------------
            # Test Facilities
            # ------------------------------------------

            test_facilities = []

            test_keywords = [
                "test",
                "testing",
                "ios",
                "android",
                "dummy"
            ]

            for facility in facilities:

                facility_name = (
                    facility.get(
                        "facility",
                        ""
                    )
                )

                lower_name = (
                    facility_name.lower()
                )

                if any(
                    keyword in lower_name
                    for keyword in test_keywords
                ):

                    test_facilities.append(
                        facility_name
                    )

            # ------------------------------------------
            # Trend Analysis
            # ------------------------------------------

            trend_status = (
                "stable"
            )

            if len(
                monthly_trend
            ) >= 2:

                first_value = (
                    monthly_trend[0].get(
                        "count",
                        0
                    )
                )

                last_value = (
                    monthly_trend[-1].get(
                        "count",
                        0
                    )
                )

                if last_value > first_value:

                    trend_status = (
                        "increasing"
                    )

                elif last_value < first_value:

                    trend_status = (
                        "decreasing"
                    )

            # ------------------------------------------
            # Utilization Status
            # ------------------------------------------

            total_facilities = len(
                facilities
            )

            active_facilities = len(
                [
                    f
                    for f in facilities
                    if f.get(
                        "bookings",
                        0
                    ) > 0
                ]
            )

            utilization_percentage = (
                round(
                    (
                        active_facilities
                        / total_facilities
                    ) * 100,
                    2
                )
                if total_facilities > 0
                else 0
            )

            if utilization_percentage >= 70:

                utilization_status = (
                    "High"
                )

            elif utilization_percentage >= 40:

                utilization_status = (
                    "Moderate"
                )

            else:

                utilization_status = (
                    "Low"
                )

            # ------------------------------------------
            # Final Analytics
            # ------------------------------------------

            return {

                "property_name":
                    property_data.get(
                        "name",
                        ""
                    ),

                "report_period":
                    property_data.get(
                        "report_period",
                        ""
                    ),

                "total_bookings":
                    total_bookings,

                "total_facilities":
                    total_facilities,

                "active_facilities":
                    active_facilities,

                "utilization_percentage":
                    utilization_percentage,

                "utilization_status":
                    utilization_status,

                "top_facilities":
                    top_facilities,

                "unused_facilities_count":
                    len(
                        unused_facilities
                    ),

                "unused_facilities":
                    unused_facilities,

                "low_usage_facilities":
                    low_usage_facilities,

                "test_facilities_count":
                    len(
                        test_facilities
                    ),

                "test_facilities":
                    test_facilities,

                "trend_status":
                    trend_status,

                "monthly_trend":
                    monthly_trend
            }

        except Exception as ex:

            logger.exception(
                "Error while analyzing facility booking data"
            )

            raise Exception(
                f"Facility booking analysis failed: {str(ex)}"
            )