from typing import TypedDict


class ReportState(
    TypedDict,
    total=False
):

    # ----------------------------------
    # Common Login
    # ----------------------------------

    login_id: int

    authorization: str

    # ----------------------------------
    # Financial
    # ----------------------------------

    invoice_id: int

    # ----------------------------------
    # Property / Period
    # ----------------------------------

    property_id: int

    period: str

    # ----------------------------------
    # Common
    # ----------------------------------

    question: str

    current_module: str

    detected_module: str

    answer: str