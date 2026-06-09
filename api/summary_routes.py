import traceback
from fastapi import (
    APIRouter,
    HTTPException,
    Header
)

import requests

from services.analytics.resident_feedback_analyzer import (
    ResidentFeedbackAnalyzer
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

BACKEND_REPORT_URL = (
    "https://aereanew.panzerplayground.com/api/reports/properties"
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
        print("SUMMARY API STARTED")
        print("=" * 80)

        if not authorization:

            raise HTTPException(
                status_code=401,
                detail="Authorization header missing"
            )

        property_id = request.get("property")
        period = request.get("period")

        print("PROPERTY:", property_id)
        print("PERIOD:", period)
        print("URL:", BACKEND_REPORT_URL)

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

        print("CALLING REPORT API...")

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

        print(
            "API STATUS:",
            backend_response.status_code
        )

        backend_response.raise_for_status()

        report_data = backend_response.json()

        print("REPORT RECEIVED")

        analytics = (
            ResidentFeedbackAnalyzer()
            .analyze(report_data)
        )

        print("ANALYTICS CREATED")

        prompt = (
            PromptBuilder()
            .build_feedback_summary_prompt(
                analytics
            )
        )

        print("PROMPT CREATED")

        gemini_response = generate(
            prompt
        )

        print("GEMINI RESPONSE RECEIVED")

        summary = (
            LLMResponseParser()
            .parse_json(
                gemini_response
            )
        )

        print("SUMMARY PARSED")

        return {
            "status": True,
            "property": property_id,
            "period": period,
            "summary": summary
        }

    except HTTPException:
        raise

    except requests.exceptions.RequestException as ex:

        print("REQUEST ERROR:")
        print(str(ex))

        raise HTTPException(
            status_code=500,
            detail=f"Backend API Error: {str(ex)}"
        )

    except Exception as ex:

        print("=" * 80)
        print("GENERAL ERROR")
        print(traceback.format_exc())
        print("=" * 80)

        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )