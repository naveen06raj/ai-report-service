from typing import TypedDict


class ReportState(
    TypedDict,
    total=False
):

    property_id: str

    period: str

    question: str

    current_module: str

    authorization: str

    detected_module: str

    answer: str