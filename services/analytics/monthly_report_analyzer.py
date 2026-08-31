class MonthlyReportAnalyzer:

    @staticmethod
    def analyze(
        report_data: dict
    ) -> dict:

        # ----------------------------------
        # Validate Response
        # ----------------------------------

        if not isinstance(report_data, dict):

            raise ValueError(
                "Monthly report response must be an object."
            )

        # ----------------------------------
        # Get API Data
        # ----------------------------------

        data = report_data.get("data")

        if not isinstance(data, dict):

            raise ValueError(
                "Monthly report API response does not contain valid 'data'."
            )

        # ----------------------------------
        # Final Analytics
        # ----------------------------------

        analytics = {

            "property_id":
                data.get("property_id"),

            "month":
                data.get("month"),

            "active_users":
                int(
                    data.get(
                        "active_users",
                        0
                    ) or 0
                ),

            "total_users":
                int(
                    data.get(
                        "total_users",
                        0
                    ) or 0
                ),

            "login_rate":
                float(
                    data.get(
                        "login_rate",
                        0
                    ) or 0
                ),

            "feedback_score":
                float(
                    data.get(
                        "feedback_score",
                        0
                    ) or 0
                ),

            "booking_rate":
                float(
                    data.get(
                        "booking_rate",
                        0
                    ) or 0
                ),

            "key_collection_count":
                int(
                    data.get(
                        "key_collection_count",
                        0
                    ) or 0
                ),

            "visitor_count":
                int(
                    data.get(
                        "visitor_count",
                        0
                    ) or 0
                ),

            "financial_collection_rate":
                float(
                    data.get(
                        "financial_collection_rate",
                        0
                    ) or 0
                ),

            "status":
                data.get("status")
        }

        # ----------------------------------
        # Debug
        # ----------------------------------

        print("=" * 80)
        print("MONTHLY ANALYZER INPUT")
        print("=" * 80)
        print(data)

        print("=" * 80)
        print("MONTHLY ANALYTICS OUTPUT")
        print("=" * 80)
        print(analytics)
        print("=" * 80)

        return analytics