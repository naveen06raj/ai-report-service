import logging

logger = logging.getLogger(__name__)


class ThresholdAnalyzer:

    STATIC_ANALYTICS = {

        "loginRate": {
            "current_value": 82,
            "trend": "Stable",
            "recommended_range": "75-90",
            "industry_standard": 80
        },

        "feedbackScore": {
            "current_value": 74,
            "trend": "Declining",
            "recommended_range": "75-85",
            "industry_standard": 80
        },

        "bookingRate": {
            "current_value": 42,
            "trend": "Increasing",
            "recommended_range": "25-40",
            "industry_standard": 30
        },

        "financialCollectionRate": {
            "current_value": 89,
            "trend": "Stable",
            "recommended_range": "85-95",
            "industry_standard": 85
        },

        "activeUsers": {
            "current_value": 118,
            "trend": "Increasing",
            "recommended_range": "100-150",
            "industry_standard": 120
        },

        "visitorCount": {
            "current_value": 165,
            "trend": "Stable",
            "recommended_range": "150-200",
            "industry_standard": 150
        },

        "keyCollectionCount": {
            "current_value": 92,
            "trend": "Stable",
            "recommended_range": "80-100",
            "industry_standard": 90
        }

    }

    def analyze(
        self,
        threshold_response: dict
    ) -> dict:

        threshold_list = threshold_response.get(
            "data",
            []
        )

        analytics = []

        for item in threshold_list:

            config_key = item.get("config_key")

            static_data = self.STATIC_ANALYTICS.get(
                config_key,
                {}
            )

            analytics.append({

                "config_key": config_key,

                "label": item.get("label"),

                "condition": item.get("condition"),

                "current_threshold": item.get("value"),

                "unit": item.get("unit"),

                "status": item.get("status"),

                "minimum": item.get("min"),

                "maximum": item.get("max"),

                "current_value": static_data.get(
                    "current_value"
                ),

                "trend": static_data.get(
                    "trend"
                ),

                "recommended_range": static_data.get(
                    "recommended_range"
                ),

                "industry_standard": static_data.get(
                    "industry_standard"
                )

            })

        return {

            "thresholds": analytics

        }