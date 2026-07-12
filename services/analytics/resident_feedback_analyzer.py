import logging

from collections import Counter
from datetime import datetime

logger = logging.getLogger(__name__)


class ResidentFeedbackAnalyzer:

    def analyze(
        self,
        report_data: dict
    ) -> dict:

        try:

            feedback_list = (
                report_data
                .get(
                    "feedback_list",
                    {}
                )
                .get(
                    "data",
                    []
                )
            )

            print("=" * 80)
            print(
                "TOTAL FEEDBACK RECORDS:",
                len(feedback_list)
            )
            print("=" * 80)

            total_feedback = len(
                feedback_list
            )

            status_counter = Counter()

            category_counter = Counter()

            monthly_counter = Counter()

            # ----------------------------------
            # Process Feedback
            # ----------------------------------

            for item in feedback_list:

                submission = (
                    item.get(
                        "submissions"
                    )
                    or {}
                )

                option = (
                    item.get(
                        "option"
                    )
                    or {}
                )

                # --------------------------
                # Status
                # --------------------------

                status = submission.get(
                    "status",
                    0
                )

                if status == 0:

                    status_counter[
                        "Open"
                    ] += 1

                elif status == 1:

                    status_counter[
                        "Resolved"
                    ] += 1

                else:

                    status_counter[
                        "Closed"
                    ] += 1

                # --------------------------
                # Category
                # --------------------------

                category = (
                    option.get(
                        "feedback_option"
                    )
                    or "Unknown"
                )

                category_counter[
                    category
                ] += 1

                # --------------------------
                # Monthly Trend
                # --------------------------

                created_at = submission.get(
                    "created_at"
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
            # Category Breakdown
            # ----------------------------------

            categories = []

            for category, count in sorted(

                category_counter.items(),

                key=lambda x: x[1],

                reverse=True

            ):

                categories.append(

                    {

                        "category":
                            category,

                        "count":
                            count,

                        "percentage":
                            round(
                                (
                                    count
                                    / total_feedback
                                ) * 100,
                                2
                            )
                            if total_feedback > 0
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
            # Final Analytics
            # ----------------------------------

            return {

                "total_feedback":
                    total_feedback,

                "status_summary":
                    dict(
                        status_counter
                    ),

                "feedback_categories":
                    categories,

                "monthly_trend":
                    trend

            }

        except Exception as ex:

            logger.exception(
                "Error while analyzing resident feedback"
            )

            raise Exception(
                f"Resident feedback analysis failed: {str(ex)}"
            )