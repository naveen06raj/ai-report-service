import traceback

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

from services.reports.facility_booking_report import (
    FacilityBookingReportService
)

from services.analytics.facility_booking_analyzer import (
    FacilityBookingAnalyzer
)

from services.reports.visitor_management_report import (
    VisitorManagementReportService
)

from services.analytics.visitor_management_analyzer import (
    VisitorManagementAnalyzer
)

from services.llm.prompt_builder import (
    PromptBuilder
)

from services.llm.gemini_client import (
    generate
)

from services.llm.llm_response_parser import (
    LLMResponseParser
)

from services.reports.financial_report import (
    FinancialReportService
)

from services.analytics.financial_overview_analyzer import (
    FinancialAnalyzer
)

from services.reports.key_collection_report import (
    KeyCollectionReportService
)

from services.analytics.key_collection_analyzer import (
    KeyCollectionAnalyzer
)


router = APIRouter(
    prefix="/summary",
    tags=["AI Summary"]
)


# ==================================================
# Helper
# ==================================================

def get_request_parameters(
    request: dict
):

    login_id = request.get(
        "login_id"
    )

    property_id = request.get(
        "property_id"
    )

    start_date = request.get(
        "start_date"
    )

    end_date = request.get(
        "end_date"
    )

    # ----------------------------------
    # Required Fields
    # ----------------------------------

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

    if not start_date:

        raise HTTPException(
            status_code=400,
            detail="start_date is required"
        )

    if not end_date:

        raise HTTPException(
            status_code=400,
            detail="end_date is required"
        )

    # ----------------------------------
    # Convert IDs
    # ----------------------------------

    try:

        login_id = int(
            login_id
        )

        property_id = int(
            property_id
        )

    except (TypeError, ValueError):

        raise HTTPException(
            status_code=400,
            detail="login_id and property_id must be integers"
        )

    # ----------------------------------
    # Validate Date Format
    # ----------------------------------

    if (
        not isinstance(start_date, str)
        or len(start_date) != 10
        or start_date[4] != "-"
        or start_date[7] != "-"
    ):

        raise HTTPException(
            status_code=400,
            detail="start_date must be in YYYY-MM-DD format"
        )

    if (
        not isinstance(end_date, str)
        or len(end_date) != 10
        or end_date[4] != "-"
        or end_date[7] != "-"
    ):

        raise HTTPException(
            status_code=400,
            detail="end_date must be in YYYY-MM-DD format"
        )

    # ----------------------------------
    # Validate Date Range
    # ----------------------------------

    if start_date > end_date:

        raise HTTPException(
            status_code=400,
            detail="start_date cannot be greater than end_date"
        )

    return (
        login_id,
        property_id,
        start_date,
        end_date
    )


# ==================================================
# Resident Feedback Summary
# ==================================================

@router.post("/resident-feedback")
async def resident_feedback_summary(
    request: dict,
    authorization: str = Header(None)
):

    try:

        if not authorization:

            raise HTTPException(
                status_code=401,
                detail="Authorization header missing"
            )

        (
            login_id,
            property_id,
            start_date,
            end_date
        ) = get_request_parameters(
            request
        )

        print("=" * 80)
        print("FEEDBACK SUMMARY API STARTED")
        print("=" * 80)

        print("LOGIN ID:", login_id)
        print("PROPERTY ID:", property_id)
        print("START DATE:", start_date)
        print("END DATE:", end_date)

        # ----------------------------------
        # Report
        # ----------------------------------

        report_data = (
            FeedbackReportService()
            .get_report(
                login_id=login_id,
                property_id=property_id,
                start_date=start_date,
                end_date=end_date,
                authorization=authorization
            )
        )

        # ----------------------------------
        # Analytics
        # ----------------------------------

        analytics = (
            ResidentFeedbackAnalyzer()
            .analyze(
                report_data
            )
        )

        # ----------------------------------
        # Prompt
        # ----------------------------------

        prompt = (
            PromptBuilder()
            .build_feedback_summary_prompt(
                analytics
            )
        )

        # ----------------------------------
        # Gemini
        # ----------------------------------

        gemini_response = generate(
            prompt
        )

        # ----------------------------------
        # Parse
        # ----------------------------------

        summary = (
            LLMResponseParser()
            .parse_json(
                gemini_response
            )
        )

        return {

            "status": True,

            "login_id": login_id,

            "property_id": property_id,

            "start_date": start_date,

            "end_date": end_date,

            "summary": summary

        }

    except HTTPException:

        raise

    except Exception:

        print(
            traceback.format_exc()
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to generate resident feedback summary"
        )


# ==================================================
# Facility Booking Summary
# ==================================================

@router.post("/facility-booking")
async def facility_booking_summary(
    request: dict,
    authorization: str = Header(None)
):

    try:

        if not authorization:

            raise HTTPException(
                status_code=401,
                detail="Authorization header missing"
            )

        (
            login_id,
            property_id,
            start_date,
            end_date
        ) = get_request_parameters(
            request
        )

        print("=" * 80)
        print("FACILITY SUMMARY API STARTED")
        print("=" * 80)

        print("LOGIN ID:", login_id)
        print("PROPERTY ID:", property_id)
        print("START DATE:", start_date)
        print("END DATE:", end_date)

        # ----------------------------------
        # Report
        # ----------------------------------

        report_data = (
            FacilityBookingReportService()
            .get_report(
                login_id=login_id,
                property_id=property_id,
                start_date=start_date,
                end_date=end_date,
                authorization=authorization
            )
        )

        # ----------------------------------
        # Analytics
        # ----------------------------------

        analytics = (
            FacilityBookingAnalyzer()
            .analyze(
                report_data
            )
        )

        # ----------------------------------
        # Prompt
        # ----------------------------------

        prompt = (
            PromptBuilder()
            .build_facility_summary_prompt(
                analytics
            )
        )

        # ----------------------------------
        # Gemini
        # ----------------------------------

        gemini_response = generate(
            prompt
        )

        # ----------------------------------
        # Parse
        # ----------------------------------

        summary = (
            LLMResponseParser()
            .parse_json(
                gemini_response
            )
        )

        return {

            "status": True,

            "login_id": login_id,

            "property_id": property_id,

            "start_date": start_date,

            "end_date": end_date,

            "summary": summary

        }

    except HTTPException:

        raise

    except Exception:

        print(
            traceback.format_exc()
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to generate facility booking summary"
        )


# ==================================================
# Visitor Management Summary
# ==================================================

@router.post("/visitor-management")
async def visitor_management_summary(
    request: dict,
    authorization: str = Header(None)
):

    try:

        if not authorization:

            raise HTTPException(
                status_code=401,
                detail="Authorization header missing"
            )

        (
            login_id,
            property_id,
            start_date,
            end_date
        ) = get_request_parameters(
            request
        )

        print("=" * 80)
        print("VISITOR SUMMARY API STARTED")
        print("=" * 80)

        print("LOGIN ID:", login_id)
        print("PROPERTY ID:", property_id)
        print("START DATE:", start_date)
        print("END DATE:", end_date)

        # ----------------------------------
        # Report
        # ----------------------------------

        report_data = (
            VisitorManagementReportService()
            .get_report(
                login_id=login_id,
                property_id=property_id,
                start_date=start_date,
                end_date=end_date,
                authorization=authorization
            )
        )

        # ----------------------------------
        # Analytics
        # ----------------------------------

        analytics = (
            VisitorManagementAnalyzer()
            .analyze(
                report_data
            )
        )

        # ----------------------------------
        # Prompt
        # ----------------------------------

        prompt = (
            PromptBuilder()
            .build_visitor_summary_prompt(
                analytics
            )
        )

        # ----------------------------------
        # Gemini
        # ----------------------------------

        gemini_response = generate(
            prompt
        )

        # ----------------------------------
        # Parse
        # ----------------------------------

        summary = (
            LLMResponseParser()
            .parse_json(
                gemini_response
            )
        )

        return {

            "status": True,

            "login_id": login_id,

            "property_id": property_id,

            "start_date": start_date,

            "end_date": end_date,

            "summary": summary

        }

    except HTTPException:

        raise

    except Exception:

        print(
            traceback.format_exc()
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to generate visitor management summary"
        )


# ==================================================
# Financial Summary
# ==================================================

@router.post("/financial-overview")
async def financial_summary(
    request: dict,
    authorization: str = Header(None)
):

    try:

        if not authorization:

            raise HTTPException(
                status_code=401,
                detail="Authorization header missing"
            )

        (
            login_id,
            property_id,
            start_date,
            end_date
        ) = get_request_parameters(
            request
        )

        print("=" * 80)
        print("FINANCIAL SUMMARY API STARTED")
        print("=" * 80)

        print("LOGIN ID:", login_id)
        print("PROPERTY ID:", property_id)
        print("START DATE:", start_date)
        print("END DATE:", end_date)

        # ----------------------------------
        # Report
        # ----------------------------------

        report_data = (
            FinancialReportService()
            .get_report(
                login_id=login_id,
                property_id=property_id,
                start_date=start_date,
                end_date=end_date,
                authorization=authorization
            )
        )

        # ----------------------------------
        # Analytics
        # ----------------------------------

        analytics = (
            FinancialAnalyzer()
            .analyze(
                report_data
            )
        )

        # ----------------------------------
        # Prompt
        # ----------------------------------

        prompt = (
            PromptBuilder()
            .build_financial_summary_prompt(
                analytics
            )
        )

        # ----------------------------------
        # Gemini
        # ----------------------------------

        gemini_response = generate(
            prompt
        )

        # ----------------------------------
        # Parse
        # ----------------------------------

        summary = (
            LLMResponseParser()
            .parse_json(
                gemini_response
            )
        )

        return {

            "status": True,

            "login_id": login_id,

            "property_id": property_id,

            "start_date": start_date,

            "end_date": end_date,

            "summary": summary

        }

    except HTTPException:

        raise

    except Exception:

        print(
            traceback.format_exc()
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to generate financial summary"
        )


# ==================================================
# Key Collection Summary
# ==================================================

@router.post("/key-collection")
async def key_collection_summary(
    request: dict,
    authorization: str = Header(None)
):

    try:

        if not authorization:

            raise HTTPException(
                status_code=401,
                detail="Authorization header missing"
            )

        (
            login_id,
            property_id,
            start_date,
            end_date
        ) = get_request_parameters(
            request
        )

        print("=" * 80)
        print("KEY COLLECTION SUMMARY API STARTED")
        print("=" * 80)

        print("LOGIN ID:", login_id)
        print("PROPERTY ID:", property_id)
        print("START DATE:", start_date)
        print("END DATE:", end_date)

        # ----------------------------------
        # Report
        # ----------------------------------

        report_data = (
            KeyCollectionReportService()
            .get_report(
                login_id=login_id,
                property_id=property_id,
                start_date=start_date,
                end_date=end_date,
                authorization=authorization
            )
        )

        # ----------------------------------
        # Analytics
        # ----------------------------------

        analytics = (
            KeyCollectionAnalyzer()
            .analyze(
                report_data
            )
        )

        # ----------------------------------
        # Prompt
        # ----------------------------------

        prompt = (
            PromptBuilder()
            .build_key_collection_summary_prompt(
                analytics
            )
        )

        # ----------------------------------
        # Gemini
        # ----------------------------------

        gemini_response = generate(
            prompt
        )

        # ----------------------------------
        # Parse
        # ----------------------------------

        summary = (
            LLMResponseParser()
            .parse_json(
                gemini_response
            )
        )

        return {

            "status": True,

            "login_id": login_id,

            "property_id": property_id,

            "start_date": start_date,

            "end_date": end_date,

            "summary": summary

        }

    except HTTPException:

        raise

    except Exception:

        print(
            traceback.format_exc()
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to generate key collection summary"
        )