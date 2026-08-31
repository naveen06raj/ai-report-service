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

        # ----------------------------------
        # Authorization Validation
        # ----------------------------------

        if not authorization:

            raise HTTPException(
                status_code=401,
                detail="Authorization header missing"
            )

        # ----------------------------------
        # Get Request Parameters
        # ----------------------------------

        login_id = request.get(
            "login_id"
        )

        property_id = request.get(
            "property_id"
        )

        # ----------------------------------
        # Validate login_id
        # ----------------------------------

        if not login_id:

            raise HTTPException(
                status_code=400,
                detail="login_id is required"
            )

        # ----------------------------------
        # Validate property_id
        # ----------------------------------

        if not property_id:

            raise HTTPException(
                status_code=400,
                detail="property_id is required"
            )

        # ----------------------------------
        # Convert IDs to Integer
        # ----------------------------------

        try:

            login_id = int(
                login_id
            )

            property_id = int(
                property_id
            )

        except (
            TypeError,
            ValueError
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "login_id and property_id "
                    "must be integers"
                )
            )

        # ----------------------------------
        # Debug
        # ----------------------------------

        print("=" * 80)
        print("KEY COLLECTION WORKFLOW REQUEST")
        print("=" * 80)

        print(
            "LOGIN ID:",
            login_id
        )

        print(
            "PROPERTY ID:",
            property_id
        )

        print(
            "AUTH EXISTS:",
            bool(authorization)
        )

        print("=" * 80)

        # ----------------------------------
        # Get Key Collection Report
        # ----------------------------------

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

        # ----------------------------------
        # Analyze Data
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
        # Generate AI Workflow
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

        # ----------------------------------
        # Response
        # ----------------------------------

        return {

            "status": True,

            "login_id": login_id,

            "property_id": property_id,

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