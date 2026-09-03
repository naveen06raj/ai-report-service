import logging

from collections import Counter
from datetime import datetime

logger = logging.getLogger(__name__)


class VisitorManagementAnalyzer:

    # Backend booking_type mapping
    # 1 = Pre-Registered
    # 2 = Walk-In
    REGISTRATION_TYPE_MAP = {
        1: "Pre-Registered",
        2: "Walk-In"
    }

    def analyze(
        self,
        report_data: dict
    ) -> dict:

        try:

            # ----------------------------------
            # Get Visitor Summary
            # ----------------------------------

            visitor_summary = (
                report_data.get(
                    "visitor_summary",
                    {}
                )
            )

            # Handle possible backend response shapes
            if isinstance(visitor_summary, dict):

                visitor_list = (
                    visitor_summary.get(
                        "data",
                        []
                    )
                )

            else:

                visitor_list = []

            if not isinstance(
                visitor_list,
                list
            ):

                visitor_list = []

            # ----------------------------------
            # Total Visitors
            # ----------------------------------

            total_visitors = len(
                visitor_list
            )

            # ----------------------------------
            # Counters
            # ----------------------------------

            status_counter = Counter()

            purpose_counter = Counter()

            monthly_counter = Counter()

            registration_counter = Counter()

            # ----------------------------------
            # Process Visitors
            # ----------------------------------

            for visitor in visitor_list:

                if not isinstance(
                    visitor,
                    dict
                ):
                    continue

                # ------------------------------
                # Status
                # ------------------------------

                status = (
                    visitor.get(
                        "status"
                    )
                    or "Unknown"
                )

                status_counter[
                    str(status)
                ] += 1

                # ------------------------------
                # Visiting Purpose
                #
                # Backend field:
                # "purpose"
                # ------------------------------

                purpose = (
                    visitor.get(
                        "purpose"
                    )
                    or "Unknown"
                )

                purpose_counter[
                    str(purpose)
                ] += 1

                # ------------------------------
                # Registration Type
                #
                # Backend field:
                # "booking_type"
                #
                # 1 = Pre-Registered
                # 2 = Walk-In
                # ------------------------------

                booking_type = (
                    visitor.get(
                        "booking_type"
                    )
                )

                registration = (
                    self.REGISTRATION_TYPE_MAP.get(
                        booking_type,
                        "Unknown"
                    )
                )

                registration_counter[
                    registration
                ] += 1

                # ------------------------------
                # Monthly Trend
                #
                # Backend field:
                # "date_of_visit"
                #
                # Format:
                # DD/MM/YY
                # ------------------------------

                date_of_visit = (
                    visitor.get(
                        "date_of_visit"
                    )
                )

                if date_of_visit:

                    try:

                        visit_date = (
                            datetime.strptime(
                                date_of_visit,
                                "%d/%m/%y"
                            )
                        )

                        month_key = (
                            visit_date.strftime(
                                "%Y-%m"
                            )
                        )

                        monthly_counter[
                            month_key
                        ] += 1

                    except ValueError:

                        logger.warning(
                            "Unable to parse visitor date: %s",
                            date_of_visit
                        )

            # ----------------------------------
            # Purpose Breakdown
            # ----------------------------------

            purposes = []

            for purpose, count in sorted(

                purpose_counter.items(),

                key=lambda x: (
                    -x[1],
                    x[0]
                )

            ):

                percentage = (
                    round(
                        (
                            count
                            / total_visitors
                        ) * 100,
                        2
                    )
                    if total_visitors > 0
                    else 0
                )

                purposes.append(
                    {
                        "purpose": purpose,
                        "count": count,
                        "percentage": percentage
                    }
                )

            # ----------------------------------
            # Registration Breakdown
            # ----------------------------------

            registration_summary = {}

            for registration, count in (
                registration_counter.items()
            ):

                percentage = (
                    round(
                        (
                            count
                            / total_visitors
                        ) * 100,
                        2
                    )
                    if total_visitors > 0
                    else 0
                )

                registration_summary[
                    registration
                ] = {
                    "count": count,
                    "percentage": percentage
                }

            # ----------------------------------
            # Monthly Trend
            # ----------------------------------

            trend = []

            for month_key in sorted(
                monthly_counter.keys()
            ):

                try:

                    month_date = (
                        datetime.strptime(
                            month_key,
                            "%Y-%m"
                        )
                    )

                    month_label = (
                        month_date.strftime(
                            "%b %Y"
                        )
                    )

                except ValueError:

                    month_label = month_key

                trend.append(
                    {
                        "month": month_label,
                        "count": monthly_counter[
                            month_key
                        ]
                    }
                )

            # ----------------------------------
            # Trend Status
            # ----------------------------------
            #
            # Do not call the trend "Stable"
            # when there is no trend data.
            #
            # Compare first and last available
            # monthly values when data exists.
            # ----------------------------------

            trend_status = "Unavailable"

            if len(trend) >= 2:

                first_count = (
                    trend[0]["count"]
                )

                last_count = (
                    trend[-1]["count"]
                )

                if last_count > first_count:

                    trend_status = (
                        "Increasing"
                    )

                elif last_count < first_count:

                    trend_status = (
                        "Decreasing"
                    )

                else:

                    trend_status = (
                        "Stable"
                    )

            elif len(trend) == 1:

                trend_status = (
                    "Insufficient Data"
                )

            # ----------------------------------
            # Top Purpose
            # ----------------------------------

            top_purpose = {}

            if purposes:

                top_purpose = purposes[0]

            # ----------------------------------
            # Peak Month
            # ----------------------------------

            peak_month = {}

            if trend:

                peak_item = max(
                    trend,
                    key=lambda x: x["count"]
                )

                peak_month = {
                    "month": peak_item["month"],
                    "count": peak_item["count"]
                }

            # ----------------------------------
            # Registration Type Highlights
            # ----------------------------------

            pre_registered_count = (
                registration_counter.get(
                    "Pre-Registered",
                    0
                )
            )

            walk_in_count = (
                registration_counter.get(
                    "Walk-In",
                    0
                )
            )

            # ----------------------------------
            # Final Analytics
            # ----------------------------------

            return {

                "total_visitors":
                    total_visitors,

                "status_summary":
                    dict(
                        status_counter
                    ),

                "registration_summary":
                    registration_summary,

                "registration_counts": {
                    "Pre-Registered":
                        pre_registered_count,

                    "Walk-In":
                        walk_in_count
                },

                "top_purpose":
                    top_purpose,

                "visitor_purposes":
                    purposes,

                "monthly_trend":
                    trend,

                "trend_status":
                    trend_status,

                "peak_month":
                    peak_month

            }

        except Exception as ex:

            logger.exception(
                "Error while analyzing visitor management"
            )

            raise Exception(
                f"Visitor management analysis failed: {str(ex)}"
            )