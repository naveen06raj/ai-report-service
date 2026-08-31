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

from services.reports.key_collection_report import (
    KeyCollectionReportService
)

from services.analytics.key_collection_analyzer import (
    KeyCollectionAnalyzer
)

from services.management_report.key_collection_management_report_service import (
    KeyCollectionManagementReportService
)


# --------------------------------------------------
# Router
# --------------------------------------------------

router = APIRouter(
    prefix="/management-report",
    tags=["AI Management Report"]
)


# ==================================================
# Helper Function
# ==================================================

def get_ids(request: dict):

    login_id = request.get(
        "login_id"
    )

    property_id = request.get(
        "property_id"
    )

    if not login_id:
        raise HTTPException(
            status_code=400,
            detail="login_id is required"
        )

    if not property_id:
        raise HTTPException(
            status_code=400,
            detail="property_id is required"
        )

    try:

        login_id = int(login_id)
        property_id = int(property_id)

    except (TypeError, ValueError):

        raise HTTPException(
            status_code=400,
            detail="login_id and property_id must be integers"
        )

    return login_id, property_id


# ==================================================
# Resident Feedback
# ==================================================

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

        login_id, property_id = get_ids(
            request
        )

        # -----------------------------------------
        # Feedback APIs
        # -----------------------------------------

        report_data = (
            FeedbackReportService()
            .get_report(
                login_id=login_id,
                property_id=property_id,
                authorization=authorization
            )
        )

        print("=" * 80)
        print("FEEDBACK REPORT RECEIVED")
        print("=" * 80)

        # -----------------------------------------
        # Analytics
        # -----------------------------------------

        analytics = (
            ResidentFeedbackAnalyzer()
            .analyze(
                report_data
            )
        )

        print("=" * 80)
        print("FEEDBACK ANALYTICS CREATED")
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
        print("FEEDBACK MANAGEMENT REPORT GENERATED")
        print("=" * 80)

        return {

            "status": True,

            "login_id": login_id,

            "property_id": property_id,

            "report": report

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

        login_id, property_id = get_ids(
            request
        )

        # -----------------------------------------
        # Facility Booking APIs
        # -----------------------------------------

        report_data = (
            FacilityBookingReportService()
            .get_report(
                login_id=login_id,
                property_id=property_id,
                authorization=authorization
            )
        )

        print("=" * 80)
        print("FACILITY REPORT RECEIVED")
        print("=" * 80)

        # -----------------------------------------
        # Analytics
        # -----------------------------------------

        analytics = (
            FacilityBookingAnalyzer()
            .analyze(
                report_data
            )
        )

        print("=" * 80)
        print("FACILITY ANALYTICS CREATED")
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
        print("FACILITY MANAGEMENT REPORT GENERATED")
        print("=" * 80)

        return {

            "status": True,

            "login_id": login_id,

            "property_id": property_id,

            "report": report

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

        login_id, property_id = get_ids(
            request
        )

        # -----------------------------------------
        # Visitor Management APIs
        # -----------------------------------------

        report_data = (
            VisitorReportService()
            .get_report(
                login_id=login_id,
                property_id=property_id,
                authorization=authorization
            )
        )

        print("=" * 80)
        print("VISITOR REPORT RECEIVED")
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
        print("VISITOR ANALYTICS CREATED")
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
        print("VISITOR MANAGEMENT REPORT GENERATED")
        print("=" * 80)

        return {

            "status": True,

            "login_id": login_id,

            "property_id": property_id,

            "report": report

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
# Financial Overview
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

        login_id, property_id = get_ids(
            request
        )

        print("=" * 80)
        print("FINANCIAL MANAGEMENT REPORT STARTED")
        print("=" * 80)

        print(
            "LOGIN ID:",
            login_id
        )

        print(
            "PROPERTY ID:",
            property_id
        )

        # -----------------------------------------
        # Financial APIs
        # -----------------------------------------

        report_data = (
            FinancialReportService()
            .get_report(
                login_id=login_id,
                property_id=property_id,
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

            "property_id": property_id,

            "report": report

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
# Key Collection
# ==================================================

@router.post("/key-collection")
async def key_collection_management_report(
    request: dict,
    authorization: str = Header(None)
):

    try:

        if not authorization:

            raise HTTPException(
                status_code=401,
                detail="Authorization header missing"
            )

        login_id, property_id = get_ids(
            request
        )

        print("=" * 80)
        print("KEY COLLECTION MANAGEMENT REPORT STARTED")
        print("=" * 80)

        print(
            "LOGIN ID:",
            login_id
        )

        print(
            "PROPERTY ID:",
            property_id
        )

        # -----------------------------------------
        # Key Collection API
        # -----------------------------------------

        report_data = (
            KeyCollectionReportService()
            .get_report(
                login_id=login_id,
                property_id=property_id,
                authorization=authorization
            )
        )

        print("=" * 80)
        print("KEY COLLECTION REPORT RECEIVED")
        print("=" * 80)

        # -----------------------------------------
        # Analytics
        # -----------------------------------------

        analytics = (
            KeyCollectionAnalyzer()
            .analyze(
                report_data
            )
        )

        print("=" * 80)
        print("KEY COLLECTION ANALYTICS CREATED")
        print("=" * 80)

        # -----------------------------------------
        # AI Management Report
        # -----------------------------------------

        report = (
            KeyCollectionManagementReportService()
            .generate(
                analytics
            )
        )

        print("=" * 80)
        print("KEY COLLECTION MANAGEMENT REPORT GENERATED")
        print("=" * 80)

        return {

            "status": True,

            "login_id": login_id,

            "property_id": property_id,

            "report": report

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