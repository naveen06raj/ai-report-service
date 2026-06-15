from fastapi import (
    APIRouter,
    HTTPException,
    Header
)

import requests

from services.analytics.resident_feedback_analyzer import (
    ResidentFeedbackAnalyzer
)

from services.anomaly.feedback_anomaly_service import (
    FeedbackAnomalyService
)

from services.analytics.facility_booking_analyzer import (
    FacilityBookingAnalyzer
)

from services.anomaly.facility_anomaly_service import (
    FacilityAnomalyService
)

# --------------------------------------------------
# Backend Report API
# --------------------------------------------------

BACKEND_REPORT_URL = (
    "https://aereanew.panzerplayground.com/api/reports/properties"
)

# --------------------------------------------------
# Router
# --------------------------------------------------

router = APIRouter(
    prefix="/anomaly",
    tags=["AI Anomaly Detection"]
)


@router.post("/resident-feedback")
async def resident_feedback_anomaly(
    request: dict,
    authorization: str = Header(None)
):

    try:

        if not authorization:

            raise HTTPException(
                status_code=401,
                detail="Authorization header missing"
            )

        property_id = request.get(
            "property"
        )

        period = request.get(
            "period"
        )

        if not property_id:

            raise HTTPException(
                status_code=400,
                detail="property is required"
            )

        if not period:

            raise HTTPException(
                status_code=400,
                detail="period is required"
            )

        # --------------------------------------------------
        # Call Report API
        # --------------------------------------------------

        backend_response = requests.post(
            BACKEND_REPORT_URL,
            headers={
                "Authorization": authorization,
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            json={
                "property": property_id,
                "period": period
            },
            timeout=60
        )

        backend_response.raise_for_status()

        report_data = (
            backend_response.json()
        )

        # --------------------------------------------------
        # Analytics
        # --------------------------------------------------

        analytics = (
            ResidentFeedbackAnalyzer()
            .analyze(
                report_data
            )
        )

        # --------------------------------------------------
        # AI Anomaly Detection
        # --------------------------------------------------

        anomalies = (
            FeedbackAnomalyService()
            .detect(
                analytics
            )
        )

        return anomalies

    except HTTPException:
        raise

    except requests.exceptions.RequestException as ex:

        raise HTTPException(
            status_code=500,
            detail=f"Backend API Error: {str(ex)}"
        )

    except Exception as ex:

        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )


@router.post("/facility-booking")
async def facility_booking_anomaly(
    request: dict,
    authorization: str = Header(None)
):

    try:

        if not authorization:

            raise HTTPException(
                status_code=401,
                detail="Authorization header missing"
            )

        property_id = request.get(
            "property"
        )

        period = request.get(
            "period"
        )

        if not property_id:

            raise HTTPException(
                status_code=400,
                detail="property is required"
            )

        if not period:

            raise HTTPException(
                status_code=400,
                detail="period is required"
            )

        # --------------------------------------------------
        # Call Report API
        # --------------------------------------------------

        backend_response = requests.post(
            BACKEND_REPORT_URL,
            headers={
                "Authorization": authorization,
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            json={
                "property": property_id,
                "period": period
            },
            timeout=60
        )

        backend_response.raise_for_status()

        report_data = (
            backend_response.json()
        )

        # --------------------------------------------------
        # Analytics
        # --------------------------------------------------

        analytics = (
            FacilityBookingAnalyzer()
            .analyze(
                report_data
            )
        )

        # --------------------------------------------------
        # AI Anomaly Detection
        # --------------------------------------------------

        anomalies = (
            FacilityAnomalyService()
            .detect(
                analytics
            )
        )

        return anomalies

    except HTTPException:
        raise

    except requests.exceptions.RequestException as ex:

        raise HTTPException(
            status_code=500,
            detail=f"Backend API Error: {str(ex)}"
        )

    except Exception as ex:

        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )