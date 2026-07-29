from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel

from services.threshold.threshold_advisor_service import (
    ThresholdAdvisorService
)
from services.threshold.auto_tune_service import AutoTuneService

from services.threshold.explain_service import (
    ThresholdExplainService
)

router = APIRouter(
    prefix="/threshold",
    tags=["AI Threshold Advisor"]
)


class ThresholdRequest(BaseModel):
    property: str
    period: str = "monthly"

class ThresholdExplainRequest(BaseModel):
    property: str
    period: str = "monthly"
    config_key: str


@router.post("/advisor")
async def threshold_advisor(
    request: ThresholdRequest,
    authorization: str = Header(...)
):

    try:

        service = ThresholdAdvisorService()

        result = service.generate_advisor(
            authorization=authorization,
            property_id=request.property,
            period=request.period
        )

        return {
            "status": True,
            "message": "Success",
            "data": result
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("/auto-tune")
async def auto_tune(
    request: ThresholdRequest,
    authorization: str = Header(...)
):

    try:

        service = AutoTuneService()

        result = service.generate_auto_tune(
            authorization=authorization,
            property_id=request.property,
            period=request.period
        )

        return {
            "status": True,
            "message": "Success",
            "data": result
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("/explain")
async def threshold_explain(
    request: ThresholdExplainRequest,
    authorization: str = Header(...)
):

    try:

        service = ThresholdExplainService()

        result = service.generate(
            authorization=authorization,
            property_id=request.property,
            period=request.period,
            config_key=request.config_key
        )

        return {
            "status": True,
            "message": "Success",
            "data": result
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )