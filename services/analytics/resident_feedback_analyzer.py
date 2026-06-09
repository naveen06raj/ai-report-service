import logging

logger = logging.getLogger(__name__)


class ResidentFeedbackAnalyzer:

    def analyze(self, report_data: dict) -> dict:
        """
        Analyze resident feedback data and prepare
        analytics for AI summary generation.
        """

        try:

            property_data = report_data["data"][0]

            feedback = property_data.get(
                "feedback",
                {}
            )

            total_feedback = feedback.get(
                "total",
                0
            )

            categories = feedback.get(
                "by_category",
                []
            )

            categories = sorted(
                categories,
                key=lambda x: x.get(
                    "count",
                    0
                ),
                reverse=True
            )

            processed_categories = []

            for category in categories:

                count = category.get(
                    "count",
                    0
                )

                percentage = (
                    round(
                        (count / total_feedback) * 100,
                        2
                    )
                    if total_feedback > 0
                    else 0
                )

                processed_categories.append(
                    {
                        "category": category.get(
                            "category",
                            "Unknown"
                        ),
                        "count": count,
                        "percentage": percentage,
                        "severity": category.get(
                            "severity",
                            "normal"
                        )
                    }
                )

            return {
                "property_name": property_data.get(
                    "name",
                    ""
                ),
                "report_period": property_data.get(
                    "report_period",
                    ""
                ),
                "total_feedback": total_feedback,
                "categories": processed_categories,
                "trend": feedback.get(
                    "monthly_trend",
                    []
                )
            }

        except Exception as ex:

            logger.exception(
                "Error while analyzing resident feedback"
            )

            raise Exception(
                f"Resident feedback analysis failed: {str(ex)}"
            )