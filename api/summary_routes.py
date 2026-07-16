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


router = APIRouter(
    prefix="/summary",
    tags=["AI Summary"]
)


@router.post("/resident-feedback")
async def resident_feedback_summary(
    request: dict,
    authorization: str = Header(None)
):

    try:

        print("=" * 80)
        print("FEEDBACK SUMMARY API STARTED")
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

        print(
            "CALLING FEEDBACK APIS..."
        )

        report_data = (
            FeedbackReportService()
            .get_report(
                login_id=login_id,
                authorization=authorization
            )
        )

        print(
            "REPORT RECEIVED"
        )

        analytics = (
            ResidentFeedbackAnalyzer()
            .analyze(
                report_data
            )
        )

        print(
            "ANALYTICS CREATED"
        )

        import json

        print("=" * 80)
        print("ANALYTICS")
        print("=" * 80)
        print(json.dumps(analytics, indent=4))
        print("=" * 80)

        prompt = (
            PromptBuilder()
            .build_feedback_summary_prompt(
                analytics
            )
        )

        print(
            "PROMPT CREATED"
        )

        print("=" * 80)
        print("PROMPT")
        print("=" * 80)
        print(prompt)
        print("=" * 80)

        gemini_response = generate(
            prompt
        )

        print(
            "GEMINI RESPONSE RECEIVED"
        )

        print("=" * 80)
        print("RAW GEMINI RESPONSE")
        print("=" * 80)
        print(gemini_response)
        print("=" * 80)

        summary = (
            LLMResponseParser()
            .parse_json(
                gemini_response
            )
        )

        print(
            "SUMMARY PARSED"
        )

        return {

            "status": True,

            "login_id": login_id,

            "summary": summary

        }

    except HTTPException:
        raise

    except Exception as ex:

        print("=" * 80)
        print("GENERAL ERROR")
        print(traceback.format_exc())
        print("=" * 80)

        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )


# --------------------------------------------------
# Facility Booking Summary
# --------------------------------------------------

# --------------------------------------------------
# Facility Booking Summary
# --------------------------------------------------

@router.post("/facility-booking")
async def facility_booking_summary(
    request: dict,
    authorization: str = Header(None)
):

    try:

        print("=" * 80)
        print("FACILITY SUMMARY API STARTED")
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

        print(
            "CALLING FACILITY BOOKING APIS..."
        )

        report_data = (
            FacilityBookingReportService()
            .get_report(
                login_id=login_id,
                authorization=authorization
            )
        )

        print(
            "REPORT RECEIVED"
        )

        analytics = (
            FacilityBookingAnalyzer()
            .analyze(
                report_data
            )
        )

        print(
            "FACILITY ANALYTICS CREATED"
        )

        import json

        print("=" * 80)
        print("FACILITY ANALYTICS")
        print("=" * 80)
        print(
            json.dumps(
                analytics,
                indent=4
            )
        )
        print("=" * 80)

        prompt = (
            PromptBuilder()
            .build_facility_summary_prompt(
                analytics
            )
        )

        print(
            "PROMPT CREATED"
        )

        print("=" * 80)
        print("PROMPT")
        print("=" * 80)
        print(prompt)
        print("=" * 80)

        gemini_response = generate(
            prompt
        )

        print(
            "GEMINI RESPONSE RECEIVED"
        )

        print("=" * 80)
        print("RAW GEMINI RESPONSE")
        print("=" * 80)
        print(gemini_response)
        print("=" * 80)

        summary = (
            LLMResponseParser()
            .parse_json(
                gemini_response
            )
        )

        print(
            "SUMMARY PARSED"
        )

        return {

            "status": True,

            "login_id": login_id,

            "summary": summary

        }

    except HTTPException:
        raise

    except Exception as ex:

        print("=" * 80)
        print("GENERAL ERROR")
        print(traceback.format_exc())
        print("=" * 80)

        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )

# --------------------------------------------------
# Visitor Management Summary
# --------------------------------------------------

@router.post("/visitor-management")
async def visitor_management_summary(
    request: dict,
    authorization: str = Header(None)
):

    try:

        print("=" * 80)
        print("VISITOR SUMMARY API STARTED")
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
        # Call Visitor APIs
        # ----------------------------------

        print(
            "CALLING VISITOR APIS..."
        )

        report_data = (
            VisitorManagementReportService()
            .get_report(
                login_id=login_id,
                authorization=authorization
            )
        )

        print(
            "REPORT RECEIVED"
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

        print(
            "VISITOR ANALYTICS CREATED"
        )

        import json

        print("=" * 80)
        print("VISITOR ANALYTICS")
        print("=" * 80)
        print(
            json.dumps(
                analytics,
                indent=4
            )
        )
        print("=" * 80)

        # ----------------------------------
        # Prompt
        # ----------------------------------

        prompt = (
            PromptBuilder()
            .build_visitor_summary_prompt(
                analytics
            )
        )

        print("=" * 80)
        print("PROMPT")
        print("=" * 80)
        print(prompt)
        print("=" * 80)

        # ----------------------------------
        # Gemini
        # ----------------------------------

        gemini_response = generate(
            prompt
        )

        print("=" * 80)
        print("RAW GEMINI RESPONSE")
        print("=" * 80)
        print(gemini_response)
        print("=" * 80)

        summary = (
            LLMResponseParser()
            .parse_json(
                gemini_response
            )
        )

        print(
            "SUMMARY PARSED"
        )

        return {

            "status": True,

            "login_id": login_id,

            "summary": summary

        }

    except HTTPException:
        raise

    except Exception as ex:

        print("=" * 80)
        print("GENERAL ERROR")
        print(traceback.format_exc())
        print("=" * 80)

        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )

# --------------------------------------------------
# Financial Summary
# --------------------------------------------------

@router.post("/financial-overview")
async def financial_summary(
    request: dict,
    authorization: str = Header(None)
):

    try:

        print("=" * 80)
        print("FINANCIAL SUMMARY API STARTED")
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
        # Call Financial APIs
        # ----------------------------------

        print(
            "CALLING FINANCIAL APIS..."
        )

        report_data = (
            FinancialReportService()
            .get_report(
                login_id=login_id,
                authorization=authorization
            )
        )

        print(
            "REPORT RECEIVED"
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

        print(
            "FINANCIAL ANALYTICS CREATED"
        )

        import json

        print("=" * 80)
        print("FINANCIAL ANALYTICS")
        print("=" * 80)
        print(
            json.dumps(
                analytics,
                indent=4
            )
        )
        print("=" * 80)

        # ----------------------------------
        # Prompt
        # ----------------------------------

        prompt = (
            PromptBuilder()
            .build_financial_summary_prompt(
                analytics
            )
        )

        print("=" * 80)
        print("PROMPT")
        print("=" * 80)
        print(prompt)
        print("=" * 80)

        # ----------------------------------
        # Gemini
        # ----------------------------------

        gemini_response = generate(
            prompt
        )

        print("=" * 80)
        print("RAW GEMINI RESPONSE")
        print("=" * 80)
        print(gemini_response)
        print("=" * 80)

        summary = (
            LLMResponseParser()
            .parse_json(
                gemini_response
            )
        )

        print(
            "SUMMARY PARSED"
        )

        return {

            "status": True,

            "login_id": login_id,

            "summary": summary

        }

    except HTTPException:
        raise

    except Exception as ex:

        print("=" * 80)
        print("GENERAL ERROR")
        print(traceback.format_exc())
        print("=" * 80)

        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )