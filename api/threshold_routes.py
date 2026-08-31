from fastapi import (
    APIRouter,
    HTTPException,
    Header
)

from pydantic import BaseModel

from services.threshold.threshold_advisor_service import (
    ThresholdAdvisorService
)

from services.threshold.auto_tune_service import (
    AutoTuneService
)

from services.threshold.explain_service import (
    ThresholdExplainService
)


router = APIRouter(
    prefix="/threshold",
    tags=["AI Threshold Advisor"]
)


# ==================================================
# Request Models
# ==================================================

class ThresholdRequest(BaseModel):

    login_id: int

    property_id: int

    period: str = "monthly"


class ThresholdExplainRequest(BaseModel):

    login_id: int

    property_id: int

    period: str = "monthly"

    config_key: str


# ==================================================
# Threshold Advisor
# ==================================================

@router.post("/advisor")
async def threshold_advisor(
    request: ThresholdRequest,
    authorization: str = Header(...)
):

    try:

        service = ThresholdAdvisorService()

        result = service.generate_advisor(
            authorization=authorization,
            login_id=request.login_id,
            property_id=request.property_id,
            period=request.period
        )

        return {

            "status": True,

            "message": "Success",

            "login_id": request.login_id,

            "property_id": request.property_id,

            "period": request.period,

            "data": result

        }

    except Exception as ex:

        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )


# ==================================================
# Auto Tune
# ==================================================

@router.post("/auto-tune")
async def auto_tune(
    request: ThresholdRequest,
    authorization: str = Header(...)
):

    try:

        service = AutoTuneService()

        result = service.generate_auto_tune(
            authorization=authorization,
            login_id=request.login_id,
            property_id=request.property_id,
            period=request.period
        )

        return {

            "status": True,

            "message": "Success",

            "login_id": request.login_id,

            "property_id": request.property_id,

            "period": request.period,

            "data": result

        }

    except Exception as ex:

        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )


# ==================================================
# Threshold Explain
# ==================================================

@router.post("/explain")
async def threshold_explain(
    request: ThresholdExplainRequest,
    authorization: str = Header(...)
):

    try:

        service = ThresholdExplainService()

        result = service.generate(
            authorization=authorization,
            login_id=request.login_id,
            property_id=request.property_id,
            period=request.period,
            config_key=request.config_key
        )

        return {

            "status": True,

            "message": "Success",

            "login_id": request.login_id,

            "property_id": request.property_id,

            "period": request.period,

            "config_key": request.config_key,

            "data": result

        }

    except Exception as ex:

        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )