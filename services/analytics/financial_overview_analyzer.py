class FinancialAnalyzer:

    @staticmethod
    def to_float(value):

        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def to_int(value):

        try:
            return int(value or 0)
        except (TypeError, ValueError):
            return 0

    def analyze(
        self,
        report_data: dict
    ) -> dict:

        payment = (
            report_data.get(
                "payment_overview",
                {}
            ).get(
                "data",
                {}
            )
        )

        invoice_search = (
            report_data.get(
                "invoice_search",
                {}
            ).get(
                "data",
                []
            )
        )

        batch_list = (
            report_data.get(
                "batch_list",
                {}
            ).get(
                "data",
                []
            )
        )

        # --------------------------------------------------
        # Payment Overview
        # --------------------------------------------------

        total_invoices = self.to_int(
            payment.get("total_invoices")
        )

        paid_invoices = self.to_int(
            payment.get("paid_invoices")
        )

        pending_invoices = self.to_int(
            payment.get("pending_payment_invoices")
        )

        partial_payment_invoices = self.to_int(
            payment.get("partial_payment_invoices")
        )

        monthly_fee_collected = self.to_float(
            payment.get("monthly_fee_collected")
        )

        management_fund = self.to_float(
            payment.get("tot_mf_amounts")
        )

        sinking_fund = self.to_float(
            payment.get("tot_sf_amounts")
        )

        tax_amount = self.to_float(
            payment.get("tot_tax_amounts")
        )

        interest_amount = self.to_float(
            payment.get("tot_int_amounts")
        )

        total_collection = (
            management_fund
            + sinking_fund
            + tax_amount
            + interest_amount
        )

        # --------------------------------------------------
        # Invoice Search Analysis
        # --------------------------------------------------

        overdue_invoices = 0

        overdue_amount = 0.0

        unpaid_invoices = 0

        for invoice in invoice_search:

            status = str(
                invoice.get(
                    "payment_status",
                    ""
                )
            ).lower()

            overdue_days = str(
                invoice.get(
                    "overdue_days",
                    ""
                )
            ).strip()

            balance = self.to_float(
                invoice.get(
                    "balance",
                    0
                )
            )

            if overdue_days:

                overdue_invoices += 1
                overdue_amount += balance

            if (
                "pending" in status
                or "unpaid" in status
                or "over due" in status
            ):
                unpaid_invoices += 1

        # --------------------------------------------------
        # Batch Analysis
        # --------------------------------------------------

        total_batches = len(
            batch_list
        )

        generated_invoices = sum(
            self.to_int(
                batch.get(
                    "count"
                )
            )
            for batch in batch_list
        )

        # --------------------------------------------------
        # Collection Rate
        # --------------------------------------------------

        if total_invoices > 0:

            collection_rate = round(
                (
                    paid_invoices
                    / total_invoices
                ) * 100,
                2
            )

        else:

            collection_rate = 0

        # --------------------------------------------------
        # Analytics Output
        # --------------------------------------------------

        return {

            "total_invoices": total_invoices,

            "paid_invoices": paid_invoices,

            "pending_invoices": pending_invoices,

            "partial_payment_invoices": partial_payment_invoices,

            "collection_rate": collection_rate,

            "monthly_fee_collected": monthly_fee_collected,

            "management_fund": management_fund,

            "sinking_fund": sinking_fund,

            "tax_amount": tax_amount,

            "interest_amount": interest_amount,

            "total_collection": round(
                total_collection,
                2
            ),

            "overdue_invoices": overdue_invoices,

            "overdue_amount": round(
                overdue_amount,
                2
            ),

            "unpaid_invoices": unpaid_invoices,

            "total_batches": total_batches,

            "generated_invoices": generated_invoices,

            "management_fund_trend":
                payment.get(
                    "mf_y_axis",
                    ""
                ),

            "sinking_fund_trend":
                payment.get(
                    "sf_y_axis",
                    ""
                )

        }