import logging

from collections import Counter, defaultdict
from datetime import datetime


logger = logging.getLogger(__name__)


class ResidentFeedbackAnalyzer:

    @staticmethod
    def analyze(
        report_data: dict
    ) -> dict:

        try:

            # ----------------------------------
            # Get Feedback Data
            # ----------------------------------

            feedback_list = (
                report_data
                .get(
                    "feedback_list",
                    {}
                )
                or {}
            ).get(
                "data",
                []
            ) or []

            if not isinstance(
                feedback_list,
                list
            ):
                raise ValueError(
                    "Expected feedback_list data to be a list"
                )

            print("=" * 80)
            print(
                "TOTAL FEEDBACK RECORDS:",
                len(feedback_list)
            )
            print("=" * 80)

            # ----------------------------------
            # Basic Counters
            # ----------------------------------

            total_feedback = len(
                feedback_list
            )

            status_counter = Counter()

            category_counter = Counter()

            category_ratings = defaultdict(list)

            monthly_counter = Counter()

            # Safe, LLM-friendly individual feedback records.
            # Do NOT include raw user/email/account data.
            feedback_records = []

            total_rating = 0.0

            rated_feedback_count = 0

            # ----------------------------------
            # Process Feedback
            # ----------------------------------

            for item in feedback_list:

                if not isinstance(
                    item,
                    dict
                ):
                    continue

                # ----------------------------------
                # Submission
                # ----------------------------------

                submission = (
                    item.get(
                        "submissions"
                    )
                    or {}
                )

                if not isinstance(
                    submission,
                    dict
                ):
                    submission = {}

                # ----------------------------------
                # Option
                # ----------------------------------

                option = (
                    item.get(
                        "option"
                    )
                    or {}
                )

                if not isinstance(
                    option,
                    dict
                ):
                    option = {}

                # ----------------------------------
                # Unit Information
                # ----------------------------------

                unit = (
                    item.get(
                        "unit_info"
                    )
                    or {}
                )

                if not isinstance(
                    unit,
                    dict
                ):
                    unit = {}

                # ----------------------------------
                # Get Option
                # ----------------------------------

                getoption = (
                    submission.get(
                        "getoption"
                    )
                    or {}
                )

                if not isinstance(
                    getoption,
                    dict
                ):
                    getoption = {}

                # ----------------------------------
                # Status
                # ----------------------------------

                status = submission.get(
                    "status"
                )

                if status == 0:

                    status_counter[
                        "Open"
                    ] += 1

                elif status == 1:

                    status_counter[
                        "Resolved"
                    ] += 1

                elif status == 2:

                    status_counter[
                        "Closed"
                    ] += 1

                else:

                    status_counter[
                        "Unknown"
                    ] += 1

                # ----------------------------------
                # Category
                # ----------------------------------

                category = (
                    option.get(
                        "feedback_option"
                    )
                    or getoption.get(
                        "feedback_option"
                    )
                    or "Unknown"
                )

                category = str(
                    category
                ).strip()

                if not category:
                    category = "Unknown"

                category_counter[
                    category
                ] += 1

                # ----------------------------------
                # Rating
                # ----------------------------------

                rating = submission.get(
                    "rating"
                )

                try:

                    if rating is not None:

                        rating = float(
                            rating
                        )

                        # Only accept ratings
                        # within the 1-5 scale
                        if 1 <= rating <= 5:

                            total_rating += rating

                            rated_feedback_count += 1

                            category_ratings[
                                category
                            ].append(
                                rating
                            )

                except (
                    TypeError,
                    ValueError
                ):

                    pass

                # ----------------------------------
                # Monthly Trend
                # ----------------------------------

                created_at = submission.get(
                    "created_at"
                )

                if created_at:

                    try:

                        date_obj = datetime.strptime(
                            str(created_at),
                            "%Y-%m-%d %H:%M:%S"
                        )

                        month_key = date_obj.strftime(
                            "%Y-%m"
                        )

                        monthly_counter[
                            month_key
                        ] += 1

                    except (
                        ValueError,
                        TypeError
                    ):

                        # Try date-only format
                        try:

                            date_obj = datetime.strptime(
                                str(created_at),
                                "%Y-%m-%d"
                            )

                            month_key = date_obj.strftime(
                                "%Y-%m"
                            )

                            monthly_counter[
                                month_key
                            ] += 1

                        except (
                            ValueError,
                            TypeError
                        ):

                            pass

                # ----------------------------------
                # Safe Individual Feedback Record
                # ----------------------------------

                try:
                    rating_value = (
                        float(rating)
                        if submission.get("rating") is not None
                        else None
                    )
                except (TypeError, ValueError):
                    rating_value = None

                feedback_records.append(
                    {
                        "feedback_id":
                            submission.get("id"),

                        "ticket":
                            submission.get("ticket"),

                        "subject":
                            submission.get("subject") or "",

                        "notes":
                            submission.get("notes") or "",

                        "category":
                            category,

                        "status":
                            (
                                "Open"
                                if status == 0
                                else
                                "Resolved"
                                if status == 1
                                else
                                "Closed"
                                if status == 2
                                else
                                "Unknown"
                            ),

                        "unit":
                            unit.get("unit"),

                        "rating":
                            rating_value,

                        "remarks":
                            submission.get("remarks"),

                        "created_at":
                            created_at
                    }
                )

            # ----------------------------------
            # Overall Average Rating
            # ----------------------------------

            if rated_feedback_count > 0:

                average_rating = round(
                    total_rating /
                    rated_feedback_count,
                    2
                )

            else:

                average_rating = 0

            # ----------------------------------
            # Category Breakdown
            # ----------------------------------

            categories = []

            for category, count in sorted(

                category_counter.items(),

                key=lambda x: x[1],

                reverse=True

            ):

                ratings = category_ratings.get(
                    category,
                    []
                )

                if ratings:

                    category_average_rating = round(
                        sum(ratings) /
                        len(ratings),
                        2
                    )

                else:

                    category_average_rating = 0

                percentage = (
                    round(
                        (
                            count /
                            total_feedback
                        ) * 100,
                        2
                    )
                    if total_feedback > 0
                    else 0
                )

                categories.append({

                    "category":
                        category,

                    "count":
                        count,

                    "percentage":
                        percentage,

                    "average_rating":
                        category_average_rating

                })

            # ----------------------------------
            # Best Category
            # ----------------------------------

            best_category = None

            rated_categories = [

                category

                for category in categories

                if category[
                    "average_rating"
                ] > 0

            ]

            if rated_categories:

                best_category = max(

                    rated_categories,

                    key=lambda x:
                    x["average_rating"]

                )

            # ----------------------------------
            # Needs Attention
            # ----------------------------------

            needs_attention = None

            if rated_categories:

                needs_attention = min(

                    rated_categories,

                    key=lambda x:
                    x["average_rating"]

                )

            # ----------------------------------
            # Monthly Trend
            # ----------------------------------

            trend = []

            for month in sorted(
                monthly_counter
            ):

                try:

                    month_label = datetime.strptime(
                        month,
                        "%Y-%m"
                    ).strftime(
                        "%b %Y"
                    )

                except ValueError:

                    month_label = month

                trend.append({

                    "month":
                        month_label,

                    "count":
                        monthly_counter[
                            month
                        ]

                })

            # ----------------------------------
            # Trend Summary
            # ----------------------------------

            trend_summary = None

            if len(trend) >= 2:

                first_month = trend[0]
                last_month = trend[-1]

                first_count = first_month["count"]
                last_count = last_month["count"]

                if last_count > first_count:

                    change = last_count - first_count

                    trend_summary = (
                        f"Feedback volume increased from "
                        f"{first_count} submissions in "
                        f"{first_month['month']} to "
                        f"{last_count} submissions in "
                        f"{last_month['month']}."
                    )

                elif last_count < first_count:

                    change = first_count - last_count

                    trend_summary = (
                        f"Feedback volume decreased from "
                        f"{first_count} submissions in "
                        f"{first_month['month']} to "
                        f"{last_count} submissions in "
                        f"{last_month['month']}."
                    )

                else:

                    trend_summary = (
                        f"Feedback volume remained stable at "
                        f"{last_count} submissions between "
                        f"{first_month['month']} and "
                        f"{last_month['month']}."
                    )

            elif len(trend) == 1:

                trend_summary = (
                    f"{trend[0]['count']} feedback submissions "
                    f"were recorded in {trend[0]['month']}."
                )

            else:

                trend_summary = (
                    "No valid feedback submission dates "
                    "were available for trend analysis."
                )

            # ----------------------------------
            # Final Analytics
            # ----------------------------------

            analytics = {

                "total_feedback":
                    total_feedback,

                "average_rating":
                    average_rating,

                "rating_scale":
                    5,

                "status_summary":
                    dict(
                        status_counter
                    ),

                "feedback_categories":
                    categories,

                "best_category":
                    best_category,

                "needs_attention":
                    needs_attention,

                "monthly_trend":
                    trend,

                "trend_summary":
                    trend_summary,

                # Individual records are included in a safe,
                # compact structure so chat questions such as
                # "list the feedback" can be answered.
                "feedback_records":
                    sorted(
                        feedback_records,
                        key=lambda x:
                        x.get("created_at") or "",
                        reverse=True
                    )

            }

            # ----------------------------------
            # Debug Analytics
            # ----------------------------------

            print("=" * 80)
            print("RESIDENT FEEDBACK ANALYTICS")
            print("=" * 80)

            print(
                analytics
            )

            print(
                "INDIVIDUAL FEEDBACK RECORDS:",
                len(feedback_records)
            )

            print("=" * 80)

            return analytics

        except Exception as ex:

            logger.exception(
                "Error while analyzing resident feedback"
            )

            raise Exception(
                f"Resident feedback analysis failed: {str(ex)}"
            )