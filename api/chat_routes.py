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

        if not authorization:

            raise HTTPException(
                status_code=401,
                detail="Authorization header missing"
            )

        login_id = request.get(
            "login_id"
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
        # Run AI Graph
        # ----------------------------------

        response = run_report_graph(
            login_id=login_id,
            question=question,
            current_module=current_module,
            authorization=authorization
        )

        return {

            "status": True,

            "login_id": login_id,

            "module": current_module,

            "question": question,

            "answer": response

        }

    except HTTPException:
        raise

    except Exception as ex:

        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )