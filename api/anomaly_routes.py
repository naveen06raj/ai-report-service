from fastapi import (
    APIRouter,
    HTTPException,
    Header
)

from services.reports.feedback_report import (
    FeedbackReportService
)

from services.analytics.resident_feedback_analyzer import (
    ResidentFeedbackAnalyzer
)

from services.anomaly.feedback_anomaly_service import (
    FeedbackAnomalyService
)

from services.reports.facility_booking_report import (
    FacilityBookingReportService
)

from services.analytics.facility_booking_analyzer import (
    FacilityBookingAnalyzer
)

from services.anomaly.facility_anomaly_service import (
    FacilityAnomalyService
)

from services.reports.visitor_management_report import (
    VisitorManagementReportService
)

from services.analytics.visitor_management_analyzer import (
    VisitorManagementAnalyzer
)

from services.anomaly.visitor_management_anomaly_service import (
    VisitorManagementAnomalyService
)

from services.reports.financial_report import (
    FinancialReportService
)

from services.analytics.financial_overview_analyzer import (
    FinancialAnalyzer
)

from services.anomaly.financial_anomaly_service import (
    FinancialAnomalyService
)

router = APIRouter(
    prefix="/anomaly",
    tags=["AI Anomaly Detection"]
)


# ==================================================
# Resident Feedback
# ==================================================

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

        login_id = request.get("login_id")

        if not login_id:
            raise HTTPException(
                status_code=400,
                detail="login_id is required"
            )

        report_data = (
            FeedbackReportService()
            .get_report(
                login_id=login_id,
                authorization=authorization
            )
        )

        analytics = (
            ResidentFeedbackAnalyzer()
            .analyze(
                report_data
            )
        )

        anomalies = (
            FeedbackAnomalyService()
            .detect(
                analytics
            )
        )

        return {

            "status": True,

            "login_id": login_id,

            "anomalies": anomalies

        }

    except HTTPException:
        raise

    except Exception as ex:

        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )


# ==================================================
# Facility Booking
# ==================================================

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

        login_id = request.get("login_id")

        if not login_id:
            raise HTTPException(
                status_code=400,
                detail="login_id is required"
            )

        report_data = (
            FacilityBookingReportService()
            .get_report(
                login_id=login_id,
                authorization=authorization
            )
        )

        analytics = (
            FacilityBookingAnalyzer()
            .analyze(
                report_data
            )
        )

        anomalies = (
            FacilityAnomalyService()
            .detect(
                analytics
            )
        )

        return {

            "status": True,

            "login_id": login_id,

            "anomalies": anomalies

        }

    except HTTPException:
        raise

    except Exception as ex:

        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )


# ==================================================
# Visitor Management
# ==================================================

@router.post("/visitor-management")
async def visitor_management_anomaly(
    request: dict,
    authorization: str = Header(None)
):

    try:

        if not authorization:
            raise HTTPException(
                status_code=401,
                detail="Authorization header missing"
            )

        login_id = request.get("login_id")

        if not login_id:
            raise HTTPException(
                status_code=400,
                detail="login_id is required"
            )

        # ----------------------------------
        # Visitor APIs
        # ----------------------------------

        report_data = (
            VisitorManagementReportService()
            .get_report(
                login_id=login_id,
                authorization=authorization
            )
        )

        print("=" * 80)
        print("REPORT RECEIVED")
        print("=" * 80)

        # ----------------------------------
        # Analytics
        # ----------------------------------

        analytics = (
            VisitorManagementAnalyzer()
            .analyze(
                report_data
            )
        )

        print("=" * 80)
        print("ANALYTICS CREATED")
        print("=" * 80)

        # ----------------------------------
        # AI Anomaly Detection
        # ----------------------------------

        anomalies = (
            VisitorManagementAnomalyService()
            .detect(
                analytics
            )
        )

        print("=" * 80)
        print("ANOMALIES GENERATED")
        print("=" * 80)

        return {

            "status": True,

            "login_id": login_id,

            "anomalies": anomalies

        }

    except HTTPException:
        raise

    except Exception as ex:

        print("=" * 80)
        print("GENERAL ERROR")
        print("=" * 80)

        import traceback
        traceback.print_exc()

        print("=" * 80)

        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )

# ==================================================
# Financial Overview
# ==================================================

@router.post("/financial-overview")
async def financial_overview_anomaly(
    request: dict,
    authorization: str = Header(None)
):

    try:

        print("=" * 80)
        print("FINANCIAL ANOMALY API STARTED")
        print("=" * 80)

        if not authorization:

            raise HTTPException(
                status_code=401,
                detail="Authorization header missing"
            )

        login_id = request.get(
            "login_id"
        )

        print(
            "LOGIN ID:",
            login_id
        )

        if not login_id:

            raise HTTPException(
                status_code=400,
                detail="login_id is required"
            )

        # ----------------------------------
        # Financial APIs
        # ----------------------------------

        report_data = (
            FinancialReportService()
            .get_report(
                login_id=login_id,
                authorization=authorization
            )
        )

        print("=" * 80)
        print("REPORT RECEIVED")
        print("=" * 80)

        # ----------------------------------
        # Analytics
        # ----------------------------------

        analytics = (
            FinancialAnalyzer()
            .analyze(
                report_data
            )
        )

        print("=" * 80)
        print("ANALYTICS CREATED")
        print("=" * 80)

        import json

        print(
            json.dumps(
                analytics,
                indent=4
            )
        )

        # ----------------------------------
        # AI Anomaly Detection
        # ----------------------------------

        anomalies = (
            FinancialAnomalyService()
            .detect(
                analytics
            )
        )

        print("=" * 80)
        print("ANOMALIES GENERATED")
        print("=" * 80)

        return {

            "status": True,

            "login_id": login_id,

            "anomalies": anomalies

        }

    except HTTPException:
        raise

    except Exception as ex:

        print("=" * 80)
        print("GENERAL ERROR")
        print("=" * 80)

        import traceback
        traceback.print_exc()

        print("=" * 80)

        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )