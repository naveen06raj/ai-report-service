from fastapi import (
    APIRouter,
    HTTPException,
    Header
)

from services.reports.monthly_report import (
    MonthlyReportService
)

router = APIRouter(
    prefix="/monthly-report",
    tags=["Monthly Report"]
)


@router.post("")
async def monthly_report(
    request: dict,
    authorization: str = Header(None)
):

    try:

        # ----------------------------------
        # Authorization
        # ----------------------------------

        if not authorization:

            raise HTTPException(
                status_code=401,
                detail="Authorization header missing"
            )

        # ----------------------------------
        # Request Parameters
        # ----------------------------------

        property_id = request.get(
            "property_id"
        )

        month = request.get(
            "month"
        )

        # ----------------------------------
        # Validation
        # ----------------------------------

        if not property_id:

            raise HTTPException(
                status_code=400,
                detail="property_id is required"
            )

        if not month:

            raise HTTPException(
                status_code=400,
                detail="month is required"
            )

        # ----------------------------------
        # Validate Month Format
        # ----------------------------------

        if len(month) != 7 or month[4] != "-":

            raise HTTPException(
                status_code=400,
                detail="month must be in YYYY-MM format"
            )

        # ----------------------------------
        # Generate Monthly Report
        # ----------------------------------

        report = (
            MonthlyReportService()
            .generate(
                property_id=int(property_id),
                month=month,
                authorization=authorization
            )
        )

        # ----------------------------------
        # Response
        # ----------------------------------

        return {

            "status": True,

            "message": "Monthly report generated successfully",

            "property_id": int(property_id),

            "month": month,

            "data": report

        }

    except HTTPException:
        raise

    except Exception as ex:

        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )