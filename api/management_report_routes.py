from fastapi import (
    APIRouter,
    HTTPException,
    Header
)

import requests
from services.reports.feedback_report import (
    FeedbackReportService
)

from services.analytics.resident_feedback_analyzer import (
    ResidentFeedbackAnalyzer
)

from services.management_report.feedback_management_report_service import (
    FeedbackManagementReportService
)

from services.analytics.facility_booking_analyzer import (
    FacilityBookingAnalyzer
)

from services.management_report.facility_management_report_service import (
    FacilityManagementReportService
)

from services.reports.facility_booking_report import (
    FacilityBookingReportService
)

from services.reports.visitor_management_report import (
    VisitorManagementReportService as VisitorReportService
)

from services.analytics.visitor_management_analyzer import (
    VisitorManagementAnalyzer
)

from services.management_report.visitor_management_report_service import (
    VisitorManagementReportService
)

from services.reports.financial_report import (
    FinancialReportService
)

from services.analytics.financial_overview_analyzer import (
    FinancialAnalyzer
)

from services.management_report.financial_management_report_service import (
    FinancialManagementReportService
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
    prefix="/management-report",
    tags=["AI Management Report"]
)


@router.post("/resident-feedback")
async def resident_feedback_management_report(
    request: dict,
    authorization: str = Header(None)
):

    try:

        if not authorization:

            raise HTTPException(
                status_code=401,
                detail="Authorization header missing"
            )

        login_id = request.get(
            "login_id"
        )

        if not login_id:

            raise HTTPException(
                status_code=400,
                detail="login_id is required"
            )

        # -----------------------------------------
        # Call Feedback APIs
        # -----------------------------------------

        report_data = (
            FeedbackReportService()
            .get_report(
                login_id=login_id,
                authorization=authorization
            )
        )

        print("=" * 80)
        print("REPORT RECEIVED")
        print("=" * 80)

        # -----------------------------------------
        # Analytics Layer
        # -----------------------------------------

        analytics = (
            ResidentFeedbackAnalyzer()
            .analyze(
                report_data
            )
        )

        print("=" * 80)
        print("ANALYTICS CREATED")
        print("=" * 80)

        # -----------------------------------------
        # Management Report
        # -----------------------------------------

        report = (
            FeedbackManagementReportService()
            .generate(
                analytics
            )
        )

        print("=" * 80)
        print("MANAGEMENT REPORT GENERATED")
        print("=" * 80)

        return {

            "status": True,

            "login_id": login_id,

            "report": report

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

@router.post("/facility-booking")
async def facility_booking_management_report(
    request: dict,
    authorization: str = Header(None)
):

    try:

        if not authorization:

            raise HTTPException(
                status_code=401,
                detail="Authorization header missing"
            )

        login_id = request.get(
            "login_id"
        )

        if not login_id:

            raise HTTPException(
                status_code=400,
                detail="login_id is required"
            )

        # -----------------------------------------
        # Call Facility Booking APIs
        # -----------------------------------------

        report_data = (
            FacilityBookingReportService()
            .get_report(
                login_id=login_id,
                authorization=authorization
            )
        )

        print("=" * 80)
        print("REPORT RECEIVED")
        print("=" * 80)

        # -----------------------------------------
        # Analytics Layer
        # -----------------------------------------

        analytics = (
            FacilityBookingAnalyzer()
            .analyze(
                report_data
            )
        )

        print("=" * 80)
        print("ANALYTICS CREATED")
        print("=" * 80)

        # -----------------------------------------
        # Management Report
        # -----------------------------------------

        report = (
            FacilityManagementReportService()
            .generate(
                analytics
            )
        )

        print("=" * 80)
        print("MANAGEMENT REPORT GENERATED")
        print("=" * 80)

        return {

            "status": True,

            "login_id": login_id,

            "report": report

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

@router.post("/visitor-management")
async def visitor_management_report(
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

        # -----------------------------------------
        # Call Visitor Management APIs
        # -----------------------------------------

        report_data = (
            VisitorReportService()
            .get_report(
                login_id=login_id,
                authorization=authorization
            )
        )

        print("=" * 80)
        print("REPORT RECEIVED")
        print("=" * 80)

        # -----------------------------------------
        # Analytics
        # -----------------------------------------

        analytics = (
            VisitorManagementAnalyzer()
            .analyze(
                report_data
            )
        )

        print("=" * 80)
        print("ANALYTICS CREATED")
        print("=" * 80)

        # -----------------------------------------
        # AI Management Report
        # -----------------------------------------

        report = (
            VisitorManagementReportService()
            .generate(
                analytics
            )
        )

        print("=" * 80)
        print("MANAGEMENT REPORT GENERATED")
        print("=" * 80)

        return {

            "status": True,

            "login_id": login_id,

            "report": report

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
# Financial Overview Management Report
# ==================================================

@router.post("/financial-overview")
async def financial_management_report(
    request: dict,
    authorization: str = Header(None)
):

    try:

        if not authorization:

            raise HTTPException(
                status_code=401,
                detail="Authorization header missing"
            )

        login_id = request.get(
            "login_id"
        )

        if not login_id:

            raise HTTPException(
                status_code=400,
                detail="login_id is required"
            )

        # -----------------------------------------
        # Financial APIs
        # -----------------------------------------

        report_data = (
            FinancialReportService()
            .get_report(
                login_id=login_id,
                authorization=authorization
            )
        )

        print("=" * 80)
        print("FINANCIAL REPORT RECEIVED")
        print("=" * 80)

        # -----------------------------------------
        # Analytics
        # -----------------------------------------

        analytics = (
            FinancialAnalyzer()
            .analyze(
                report_data
            )
        )

        print("=" * 80)
        print("FINANCIAL ANALYTICS CREATED")
        print("=" * 80)

        # -----------------------------------------
        # AI Management Report
        # -----------------------------------------

        report = (
            FinancialManagementReportService()
            .generate(
                analytics
            )
        )

        print("=" * 80)
        print("FINANCIAL MANAGEMENT REPORT GENERATED")
        print("=" * 80)

        return {

            "status": True,

            "login_id": login_id,

            "report": report

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