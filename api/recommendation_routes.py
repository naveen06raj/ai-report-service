from fastapi import (
    APIRouter,
    HTTPException,
    Header
)

from services.reports.key_collection_report import (
    KeyCollectionReportService
)

from services.analytics.key_collection_analyzer import (
    KeyCollectionAnalyzer
)

from services.recommendation.key_collection_recommendation_service import (
    KeyCollectionRecommendationService
)

router = APIRouter(
    prefix="/recommendation",
    tags=["AI Recommendation"]
)


# ==================================================
# Key Collection Recommendation
# ==================================================

@router.post("/key-collection")
async def key_collection_recommendation(
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

        # ----------------------------------
        # Get Report
        # ----------------------------------

        report_data = (
            KeyCollectionReportService()
            .get_report(
                login_id=login_id,
                authorization=authorization
            )
        )

        print("=" * 80)
        print("KEY COLLECTION REPORT RECEIVED")
        print("=" * 80)

        # ----------------------------------
        # Analytics
        # ----------------------------------

        analytics = (
            KeyCollectionAnalyzer()
            .analyze(
                report_data
            )
        )

        print("=" * 80)
        print("KEY COLLECTION ANALYTICS CREATED")
        print("=" * 80)

        # ----------------------------------
        # AI Recommendation
        # ----------------------------------

        recommendation = (
            KeyCollectionRecommendationService()
            .generate(
                analytics
            )
        )

        print("=" * 80)
        print("KEY COLLECTION RECOMMENDATION GENERATED")
        print("=" * 80)

        return {

            "status": True,

            "login_id": login_id,

            "recommendation": recommendation

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