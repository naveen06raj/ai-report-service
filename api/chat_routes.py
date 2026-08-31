from fastapi import (
    APIRouter,
    HTTPException,
    Header
)

from graph.report_graph import (
    run_report_graph
)

router = APIRouter(
    prefix="/chat",
    tags=["AI Chat"]
)


@router.post("/ask")
async def ask_ai(
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
        # Get Request Values
        # ----------------------------------

        login_id = request.get(
            "login_id"
        )

        property_id = request.get(
            "property_id"
        )

        current_module = request.get(
            "module"
        )

        question = request.get(
            "question"
        )

        # ----------------------------------
        # Validation
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

        if not current_module:

            raise HTTPException(
                status_code=400,
                detail="module is required"
            )

        if not question:

            raise HTTPException(
                status_code=400,
                detail="question is required"
            )

        # ----------------------------------
        # Convert IDs to Integer
        # ----------------------------------

        login_id = int(
            login_id
        )

        property_id = int(
            property_id
        )

        # ----------------------------------
        # Debug
        # ----------------------------------

        print("=" * 80)
        print("CHAT REQUEST")
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
            "MODULE:",
            current_module
        )

        print(
            "QUESTION:",
            question
        )

        print("=" * 80)

        # ----------------------------------
        # Run AI Graph
        # ----------------------------------

        response = run_report_graph(
            login_id=login_id,
            property_id=property_id,
            question=question,
            current_module=current_module,
            authorization=authorization
        )

        # ----------------------------------
        # Response
        # ----------------------------------

        return {

            "status": True,

            "login_id": login_id,

            "property_id": property_id,

            "module": current_module,

            "question": question,

            "answer": response

        }

    except HTTPException:

        raise

    except ValueError:

        raise HTTPException(
            status_code=400,
            detail="login_id and property_id must be integers"
        )

    except Exception as ex:

        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )