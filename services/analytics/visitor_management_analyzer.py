import logging

logger = logging.getLogger(__name__)


class VisitorManagementAnalyzer:

    def analyze(
        self,
        report_data: dict
    ) -> dict:

        try:

            property_data = (
                report_data["data"][0]
            )

            visitor_data = (
                property_data.get(
                    "visitor_management",
                    {}
                )
            )

            total_visitors = (
                visitor_data.get(
                    "total",
                    0
                )
            )

            purposes = (
                visitor_data.get(
                    "by_purpose",
                    []
                )
            )

            purposes = sorted(
                purposes,
                key=lambda x: x.get(
                    "count",
                    0
                ),
                reverse=True
            )

            processed_purposes = []

            for purpose in purposes:

                count = purpose.get(
                    "count",
                    0
                )

                percentage = (
                    round(
                        (
                            count /
                            total_visitors
                        ) * 100,
                        2
                    )
                    if total_visitors > 0
                    else 0
                )

                processed_purposes.append(
                    {
                        "purpose": purpose.get(
                            "purpose",
                            "Unknown"
                        ),
                        "count": count,
                        "percentage": percentage
                    }
                )

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

                "total_visitors":
                    total_visitors,

                "purposes":
                    processed_purposes,

                "trend":
                    visitor_data.get(
                        "monthly_trend",
                        []
                    )
            }

        except Exception as ex:

            logger.exception(
                "Error while analyzing visitor management"
            )

            raise Exception(
                f"Visitor management analysis failed: {str(ex)}"
            )