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

from services.workflow.key_collection_workflow_service import (
    KeyCollectionWorkflowService
)

router = APIRouter(
    prefix="/workflow",
    tags=["AI Workflow"]
)


# ==================================================
# Key Collection Workflow
# ==================================================

@router.post("/key-collection")
async def key_collection_workflow(
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
        # AI Workflow
        # ----------------------------------

        workflow = (
            KeyCollectionWorkflowService()
            .generate(
                analytics
            )
        )

        print("=" * 80)
        print("KEY COLLECTION WORKFLOW GENERATED")
        print("=" * 80)

        return {

            "status": True,

            "login_id": login_id,

            "workflow": workflow

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