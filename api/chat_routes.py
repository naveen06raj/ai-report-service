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

        property_id = request.get(
            "property"
        )

        period = request.get(
            "period"
        )

        question = request.get(
            "question"
        )

        current_module = request.get(
            "module"
        )

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

        if not question:

            raise HTTPException(
                status_code=400,
                detail="question is required"
            )

        if not current_module:

            raise HTTPException(
                status_code=400,
                detail="module is required"
            )

        response = run_report_graph(
            property_id=property_id,
            period=period,
            question=question,
            current_module=current_module,
            authorization=authorization
        )

        return {
            "status": True,
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