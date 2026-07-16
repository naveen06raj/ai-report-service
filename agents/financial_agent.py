import re

from graph.state import (
    ReportState
)

from services.reports.financial_report import (
    FinancialReportService
)

from services.llm.prompt_builder import (
    PromptBuilder
)

from services.llm.gemini_client import (
    generate
)

from services.llm.llm_response_parser import (
    LLMResponseParser
)


def financial_node(
    state: ReportState
):

    try:

        login_id = state.get(
            "login_id"
        )

        authorization = state.get(
            "authorization"
        )

        question = state.get(
            "question"
        )

        # ----------------------------------
        # Financial Report
        # ----------------------------------

        report_data = (
            FinancialReportService()
            .get_report(
                login_id=login_id,
                authorization=authorization
            )
        )

        # ----------------------------------
        # Check whether the user is asking
        # about a specific invoice
        # ----------------------------------

        invoice_match = re.search(
            r"[A-Za-z0-9\-]+",
            question
        )

        if invoice_match:

            invoice_no = invoice_match.group()

            invoice_list = report_data.get(
                "invoice_search",
                {}
            ).get(
                "data",
                []
            )

            invoice_id = None

            for invoice in invoice_list:

                if (
                    str(
                        invoice.get(
                            "invoice_no",
                            ""
                        )
                    ).lower()
                    ==
                    invoice_no.lower()
                ):

                    invoice_id = invoice.get(
                        "id"
                    )

                    break

            if invoice_id:

                invoice_view = (
                    FinancialReportService()
                    .get_invoice_view(
                        login_id=login_id,
                        invoice_id=invoice_id,
                        authorization=authorization
                    )
                )

                report_data[
                    "invoice_view"
                ] = invoice_view

        # ----------------------------------
        # Build Prompt
        # ----------------------------------

        prompt = (
            PromptBuilder()
            .build_financial_chat_prompt(
                report_data,
                question
            )
        )

        # ----------------------------------
        # Gemini
        # ----------------------------------

        response = generate(
            prompt
        )

        answer = (
            LLMResponseParser()
            .parse_json(
                response
            )
        )

        state["answer"] = answer.get(
            "answer",
            ""
        )

        return state

    except Exception as ex:

        state["answer"] = (
            f"Financial Agent Error: {str(ex)}"
        )

        return state