from typing import TypedDict


class ReportState(
    TypedDict,
    total=False
):

    # ----------------------------------
    # Feedback Module
    # ----------------------------------

    login_id: int

    # ----------------------------------
    # Other Modules
    # ----------------------------------

    property_id: str

    period: str

    # ----------------------------------
    # Common
    # ----------------------------------

    question: str

    current_module: str

    authorization: str

    detected_module: str

    answer: str