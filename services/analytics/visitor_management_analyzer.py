import logging

from collections import Counter
from datetime import datetime

logger = logging.getLogger(__name__)


class VisitorManagementAnalyzer:

    def analyze(
        self,
        report_data: dict
    ) -> dict:

        try:

            visitor_summary = (
                report_data
                .get(
                    "visitor_summary",
                    {}
                )
            )

            visitor_list = (
                visitor_summary
                .get(
                    "data",
                    []
                )
            )

            total_visitors = len(
                visitor_list
            )

            status_counter = Counter()

            purpose_counter = Counter()

            monthly_counter = Counter()

            registration_counter = Counter()

            # ----------------------------------
            # Process Visitors
            # ----------------------------------

            for visitor in visitor_list:

                # --------------------------
                # Status
                # --------------------------

                status = (
                    visitor.get(
                        "status"
                    )
                    or "Unknown"
                )

                status_counter[
                    status
                ] += 1

                # --------------------------
                # Visiting Purpose
                # --------------------------

                purpose = (
                    visitor.get(
                        "visiting_purpose"
                    )
                    or "Unknown"
                )

                purpose_counter[
                    purpose
                ] += 1

                # --------------------------
                # Registration Type
                # --------------------------

                registration = (
                    visitor.get(
                        "registration_type"
                    )
                    or "Unknown"
                )

                registration_counter[
                    registration
                ] += 1

                # --------------------------
                # Monthly Trend
                # --------------------------

                created_at = (
                    visitor.get(
                        "created_at"
                    )
                )

                if created_at:

                    try:

                        month = (
                            datetime.strptime(
                                created_at,
                                "%Y-%m-%d %H:%M:%S"
                            )
                            .strftime(
                                "%b %Y"
                            )
                        )

                        monthly_counter[
                            month
                        ] += 1

                    except Exception:

                        pass

            # ----------------------------------
            # Purpose Breakdown
            # ----------------------------------

            purposes = []

            for purpose, count in sorted(

                purpose_counter.items(),

                key=lambda x: x[1],

                reverse=True

            ):

                purposes.append(

                    {

                        "purpose":
                            purpose,

                        "count":
                            count,

                        "percentage":
                            round(
                                (
                                    count
                                    / total_visitors
                                ) * 100,
                                2
                            )
                            if total_visitors > 0
                            else 0

                    }

                )

            # ----------------------------------
            # Monthly Trend
            # ----------------------------------

            trend = []

            for month in sorted(
                monthly_counter
            ):

                trend.append(

                    {

                        "month":
                            month,

                        "count":
                            monthly_counter[
                                month
                            ]

                    }

                )

            # ----------------------------------
            # Trend Status
            # ----------------------------------

            trend_status = (
                "Stable"
            )

            if len(trend) >= 2:

                if trend[-1]["count"] > trend[0]["count"]:

                    trend_status = (
                        "Increasing"
                    )

                elif trend[-1]["count"] < trend[0]["count"]:

                    trend_status = (
                        "Decreasing"
                    )

            # ----------------------------------
            # Top Purpose
            # ----------------------------------

            top_purpose = {}

            if purposes:

                top_purpose = purposes[0]

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
                    dict(
                        registration_counter
                    ),

                "top_purpose":
                    top_purpose,

                "visitor_purposes":
                    purposes,

                "monthly_trend":
                    trend,

                "trend_status":
                    trend_status

            }

        except Exception as ex:

            logger.exception(
                "Error while analyzing visitor management"
            )

            raise Exception(
                f"Visitor management analysis failed: {str(ex)}"
            )