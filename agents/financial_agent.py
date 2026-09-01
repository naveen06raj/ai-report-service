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

        property_id = state.get(
            "property_id"
        )

        authorization = state.get(
            "authorization"
        )

        question = state.get(
            "question"
        )

        # ----------------------------------
        # Validation
        # ----------------------------------

        if not login_id:

            raise Exception(
                "login_id is required."
            )

        if not property_id:

            raise Exception(
                "property_id is required."
            )

        if not authorization:

            raise Exception(
                "Authorization token is required."
            )

        if not question:

            raise Exception(
                "Question is required."
            )

        # ----------------------------------
        # Simple Greeting
        # ----------------------------------

        greeting = question.strip().lower()

        if greeting in [
            "hi",
            "hello",
            "hey",
            "hi there",
            "hello there"
        ]:

            state["answer"] = (
                "Hi! How can I help you with Financial Reports?"
            )

            return state

        # ----------------------------------
        # Financial Report
        # ----------------------------------

        report_data = (
            FinancialReportService()
            .get_report(
                login_id=login_id,
                property_id=property_id,
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

            # ----------------------------------
            # Get Invoice Details
            # ----------------------------------

            if invoice_id:

                invoice_view = (
                    FinancialReportService()
                    .get_invoice_view(
                        login_id=login_id,
                        property_id=property_id,
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

        # ----------------------------------
        # Parse Response
        # ----------------------------------

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