import logging
from collections import Counter, defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)


class FinancialAnalyzer:

    # ============================================================
    # Backend Status Mapping
    # ============================================================

    PAYMENT_STATUS_MAP = {
        1: "Payment Pending",
        2: "Partially Paid",
        3: "Paid",
        4: "Pending verification",
    }

    BALANCE_TYPE_MAP = {
        1: "Balance need to pay",
        2: "Excess paid",
    }

    # payment_breakup reference types
    REFERENCE_TYPE_MAP = {
        1: "Maintenance Fund",
        2: "Sinking Fund",
        4: "Tax",
        5: "Other",
    }

    # ============================================================
    # Safe Conversion
    # ============================================================

    @staticmethod
    def to_float(value):
        try:
            if value is None or value == "":
                return 0.0

            return float(value)

        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def to_int(value):
        try:
            if value is None or value == "":
                return 0

            return int(value)

        except (TypeError, ValueError):
            return 0

    # ============================================================
    # Date Parsing
    # ============================================================

    @staticmethod
    def parse_date(value):

        if not value:
            return None

        formats = [
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y",
            "%d/%m/%y",
        ]

        for date_format in formats:
            try:
                return datetime.strptime(
                    str(value),
                    date_format
                )

            except ValueError:
                continue

        return None

    # ============================================================
    # Extract Invoice List
    #
    # IMPORTANT:
    # Invoice filtering is NOT done here.
    #
    # Backend API is responsible for returning the
    # correct invoice records for the requested period.
    # ============================================================

    @staticmethod
    def extract_invoices(report_data):

        if not isinstance(report_data, dict):
            return []

        invoices_data = report_data.get(
            "invoices",
            {}
        )

        # Expected FinancialReportClient format:
        #
        # {
        #     "invoices": {
        #         "response": 1,
        #         "data": {
        #             "filters": {...},
        #             "invoices": [...]
        #         }
        #     }
        # }

        if isinstance(invoices_data, dict):

            data = invoices_data.get(
                "data",
                {}
            )

            if isinstance(data, dict):

                invoice_list = data.get(
                    "invoices",
                    []
                )

                if isinstance(invoice_list, list):
                    return invoice_list

            invoice_list = invoices_data.get(
                "invoices",
                []
            )

            if isinstance(invoice_list, list):
                return invoice_list

            if isinstance(data, list):
                return data

        if isinstance(invoices_data, list):
            return invoices_data

        return []

    # ============================================================
    # Payment Amount
    #
    # Only actual received amount fields are used.
    #
    # manager_received is intentionally excluded.
    # ============================================================

    def get_payment_amount(self, payment):

        if not isinstance(payment, dict):
            return 0.0

        amount_fields = [
            "cash_amount_received",
            "axs_amount_received",
            "bt_amount_received",
            "online_amount_received",
            "credit_amount",
            "add_amt_received",
        ]

        total = 0.0

        for field in amount_fields:

            total += self.to_float(
                payment.get(field)
            )

        return total

    # ============================================================
    # Payment Date
    #
    # Uses common payment_received_date first.
    # Falls back to channel-specific dates.
    # ============================================================

    def get_payment_date(self, payment):

        if not isinstance(payment, dict):
            return None

        payment_date = self.parse_date(
            payment.get("payment_received_date")
        )

        if payment_date:
            return payment_date

        date_fields = (
            "cash_received_date",
            "axs_received_date",
            "bt_received_date",
            "add_amt_date",
        )

        for date_field in date_fields:

            payment_date = self.parse_date(
                payment.get(date_field)
            )

            if payment_date:
                return payment_date

        return None

    # ============================================================
    # Check Payment Date Range
    #
    # IMPORTANT:
    # This is ONLY for payment_history.
    #
    # Invoice filtering is handled by the backend API.
    # ============================================================

    def is_payment_in_range(
        self,
        payment_date,
        start_date=None,
        end_date=None
    ):

        if not payment_date:
            return False

        if start_date and payment_date < start_date:
            return False

        if end_date and payment_date > end_date:
            return False

        return True

    # ============================================================
    # Payment History Amount Within Date Range
    #
    # This does NOT filter invoices.
    #
    # It only prevents old payment_history entries from
    # being counted in the current reporting period.
    # ============================================================

    def get_payment_history_amount_in_range(
        self,
        payment_history,
        start_date=None,
        end_date=None
    ):

        if not isinstance(payment_history, list):
            return 0.0

        total = 0.0

        for payment in payment_history:

            if not isinstance(payment, dict):
                continue

            payment_amount = self.get_payment_amount(
                payment
            )

            if payment_amount <= 0:
                continue

            payment_date = self.get_payment_date(
                payment
            )

            if not self.is_payment_in_range(
                payment_date,
                start_date,
                end_date
            ):
                continue

            total += payment_amount

        return total

    # ============================================================
    # Analyze
    # ============================================================

    def analyze(
        self,
        report_data: dict,
        start_date: str | None = None,
        end_date: str | None = None
    ) -> dict:

        try:

            # ----------------------------------------------------
            # IMPORTANT
            #
            # Do NOT filter invoice records here.
            #
            # The backend API has already filtered the invoices
            # according to the requested start_date/end_date.
            #
            # These dates are used ONLY when calculating
            # payment_history collections.
            # ----------------------------------------------------

            report_start_date = self.parse_date(
                start_date
            )

            report_end_date = self.parse_date(
                end_date
            )

            invoices = self.extract_invoices(
                report_data
            )

            logger.info(
                "Financial Analyzer received %s invoice records",
                len(invoices)
            )

            # ====================================================
            # Counters
            # ====================================================

            total_invoices = len(invoices)

            status_counter = Counter()

            balance_type_counter = Counter()

            batch_counter = Counter()

            monthly_invoice_counter = Counter()

            monthly_levy_counter = defaultdict(float)

            monthly_collected_counter = defaultdict(float)

            # ====================================================
            # Amount Totals
            # ====================================================

            total_invoice_amount = 0.0

            total_payable_amount = 0.0

            total_balance_amount = 0.0

            total_excess_paid = 0.0

            total_amount_due = 0.0

            total_collected_amount = 0.0

            # ====================================================
            # Fund Totals
            # ====================================================

            maintenance_fund = 0.0

            sinking_fund = 0.0

            tax_amount = 0.0

            other_breakup_amount = 0.0

            # ====================================================
            # Invoice Analysis
            # ====================================================

            for invoice in invoices:

                if not isinstance(invoice, dict):
                    continue

                # ------------------------------------------------
                # Payment Status
                # ------------------------------------------------

                status_number = self.to_int(
                    invoice.get("status")
                )

                status_name = self.PAYMENT_STATUS_MAP.get(
                    status_number,
                    str(invoice.get("status"))
                    if invoice.get("status") not in (None, "")
                    else "Unknown"
                )

                status_counter[
                    status_name
                ] += 1

                # ------------------------------------------------
                # Balance Type
                # ------------------------------------------------

                balance_type_number = self.to_int(
                    invoice.get("balance_type")
                )

                balance_type_name = self.BALANCE_TYPE_MAP.get(
                    balance_type_number,
                    str(invoice.get("balance_type"))
                    if invoice.get("balance_type") not in (None, "")
                    else "Unknown"
                )

                balance_type_counter[
                    balance_type_name
                ] += 1

                # ------------------------------------------------
                # Invoice Amounts
                # ------------------------------------------------

                invoice_amount = self.to_float(
                    invoice.get("invoice_amount")
                )

                payable_amount = self.to_float(
                    invoice.get("payable_amount")
                )

                balance_amount = self.to_float(
                    invoice.get("balance_amount")
                )

                total_invoice_amount += invoice_amount

                total_payable_amount += payable_amount

                # Keep the complete balance amount separately.
                total_balance_amount += balance_amount

                # ------------------------------------------------
                # Balance Business Meaning
                #
                # balance_type = 2 -> Excess paid
                # balance_type = 1 -> Balance need to pay
                # ------------------------------------------------

                if balance_type_number == 2:

                    total_excess_paid += balance_amount

                elif balance_type_number == 1:

                    total_amount_due += balance_amount

                # ------------------------------------------------
                # Payment History
                #
                # IMPORTANT:
                #
                # The invoice itself is already filtered by
                # the backend API.
                #
                # Only payment_history is checked against
                # the requested reporting period.
                # ------------------------------------------------

                payment_history = invoice.get(
                    "payment_history",
                    []
                )

                invoice_collected = (
                    self.get_payment_history_amount_in_range(
                        payment_history,
                        report_start_date,
                        report_end_date
                    )
                )

                total_collected_amount += invoice_collected

                # ------------------------------------------------
                # Batch
                # ------------------------------------------------

                batch_file_no = invoice.get(
                    "batch_file_no"
                )

                if batch_file_no:

                    batch_counter[
                        str(batch_file_no)
                    ] += 1

                # ------------------------------------------------
                # Monthly Invoice / Levy
                #
                # Invoice amount belongs to invoice month.
                #
                # Backend already decides which invoices belong
                # to the requested reporting period.
                # ------------------------------------------------

                invoice_date = self.parse_date(
                    invoice.get("invoice_date")
                )

                if invoice_date:

                    invoice_month = invoice_date.strftime(
                        "%Y-%m"
                    )

                    monthly_invoice_counter[
                        invoice_month
                    ] += 1

                    monthly_levy_counter[
                        invoice_month
                    ] += invoice_amount

                # ------------------------------------------------
                # Monthly Actual Collection
                #
                # Collection belongs to payment month.
                #
                # Only payments within requested period count.
                # ------------------------------------------------

                if isinstance(payment_history, list):

                    for payment in payment_history:

                        if not isinstance(payment, dict):
                            continue

                        payment_amount = self.get_payment_amount(
                            payment
                        )

                        if payment_amount <= 0:
                            continue

                        payment_date = self.get_payment_date(
                            payment
                        )

                        if not self.is_payment_in_range(
                            payment_date,
                            report_start_date,
                            report_end_date
                        ):
                            continue

                        payment_month = payment_date.strftime(
                            "%Y-%m"
                        )

                        monthly_collected_counter[
                            payment_month
                        ] += payment_amount

                # ------------------------------------------------
                # Payment Breakup
                # ------------------------------------------------

                payment_breakup = invoice.get(
                    "payment_breakup",
                    []
                )

                if not isinstance(
                    payment_breakup,
                    list
                ):
                    continue

                for breakup in payment_breakup:

                    if not isinstance(
                        breakup,
                        dict
                    ):
                        continue

                    reference_type = self.to_int(
                        breakup.get(
                            "reference_type"
                        )
                    )

                    amount = self.to_float(
                        breakup.get(
                            "total_amount"
                        )
                    )

                    if reference_type == 1:

                        maintenance_fund += amount

                    elif reference_type == 2:

                        sinking_fund += amount

                    elif reference_type == 4:

                        tax_amount += amount

                    else:

                        other_breakup_amount += amount

            # ====================================================
            # Payment Status Counts
            # ====================================================

            paid_invoices = status_counter.get(
                "Paid",
                0
            )

            pending_invoices = status_counter.get(
                "Payment Pending",
                0
            )

            partial_payment_invoices = status_counter.get(
                "Partially Paid",
                0
            )

            pending_verification_invoices = status_counter.get(
                "Pending verification",
                0
            )

            # ====================================================
            # Status Summary
            # ====================================================

            status_summary = {}

            for status, count in status_counter.items():

                percentage = 0.0

                if total_invoices > 0:

                    percentage = round(
                        (
                            count
                            / total_invoices
                        ) * 100,
                        2
                    )

                status_summary[status] = {
                    "count": count,
                    "percentage": percentage,
                }

            # ====================================================
            # Collection Rate
            #
            # Actual Collected /
            # Total Payable * 100
            # ====================================================

            if total_payable_amount > 0:

                collection_rate = round(
                    (
                        total_collected_amount
                        / total_payable_amount
                    ) * 100,
                    2
                )

            else:

                collection_rate = 0.0

            # ====================================================
            # Balance Summary
            #
            # Total balance is NOT the same as amount due.
            #
            # total_balance_amount
            #     = excess_paid + amount_due
            #
            # outstanding_amount
            #     = amount_due only
            # ====================================================

            total_balance_amount = round(
                total_balance_amount,
                2
            )

            total_excess_paid = round(
                total_excess_paid,
                2
            )

            total_amount_due = round(
                total_amount_due,
                2
            )

            # ====================================================
            # Monthly Trend
            # ====================================================

            monthly_trend = []

            all_months = sorted(
                set(monthly_invoice_counter.keys())
                | set(monthly_levy_counter.keys())
                | set(monthly_collected_counter.keys())
            )

            for month in all_months:

                date_value = datetime.strptime(
                    month,
                    "%Y-%m"
                )

                levy_amount = round(
                    monthly_levy_counter[
                        month
                    ],
                    2
                )

                collected_amount = round(
                    monthly_collected_counter[
                        month
                    ],
                    2
                )

                if levy_amount > 0:

                    monthly_collection_rate = round(
                        (
                            collected_amount
                            / levy_amount
                        ) * 100,
                        2
                    )

                else:

                    monthly_collection_rate = 0.0

                monthly_trend.append(
                    {
                        "month": date_value.strftime(
                            "%b %Y"
                        ),
                        "invoice_count":
                            monthly_invoice_counter[
                                month
                            ],
                        "levy_budget":
                            levy_amount,
                        "collected":
                            collected_amount,
                        "collection_rate":
                            monthly_collection_rate,
                    }
                )

            # ====================================================
            # Batch Analysis
            # ====================================================

            total_batches = len(
                batch_counter
            )

            batch_summary = []

            for batch, count in batch_counter.most_common():

                batch_summary.append(
                    {
                        "batch_file_no": batch,
                        "invoice_count": count,
                    }
                )

            top_batch = {}

            if batch_summary:

                top_batch = batch_summary[0]

            # ====================================================
            # Balance Type Summary
            #
            # Percentages are based on INVOICES,
            # not accounts.
            # ====================================================

            balance_summary = {}

            for balance_type, count in (
                balance_type_counter.items()
            ):

                percentage = 0.0

                if total_invoices > 0:

                    percentage = round(
                        (
                            count
                            / total_invoices
                        ) * 100,
                        2
                    )

                balance_summary[
                    balance_type
                ] = {
                    "count": count,
                    "percentage": percentage,
                }

            # ====================================================
            # Fund Totals
            # ====================================================

            total_fund_amount = round(
                maintenance_fund
                + sinking_fund
                + tax_amount
                + other_breakup_amount,
                2
            )

            # ====================================================
            # Final Analytics
            # ====================================================

            return {

                # ------------------------------------------------
                # Main Finance Summary Metrics
                # ------------------------------------------------

                "collection_rate":
                    collection_rate,

                "levy_collected":
                    round(
                        total_collected_amount,
                        2
                    ),

                # Actual amount that still needs to be paid
                "outstanding":
                    total_amount_due,

                "sinking_fund":
                    round(
                        sinking_fund,
                        2
                    ),

                "maintenance_fund":
                    round(
                        maintenance_fund,
                        2
                    ),

                "tax_amount":
                    round(
                        tax_amount,
                        2
                    ),

                "other_breakup_amount":
                    round(
                        other_breakup_amount,
                        2
                    ),

                "total_fund_amount":
                    total_fund_amount,

                # ------------------------------------------------
                # Levy / Collection Charts
                # ------------------------------------------------

                "levy_budget_vs_collected":
                    monthly_trend,

                "collection_rate_trend":
                    [
                        {
                            "month":
                                item["month"],
                            "collection_rate":
                                item[
                                    "collection_rate"
                                ],
                        }
                        for item in monthly_trend
                    ],

                # ------------------------------------------------
                # Invoice Counts
                # ------------------------------------------------

                "total_invoices":
                    total_invoices,

                "paid_invoices":
                    paid_invoices,

                "pending_invoices":
                    pending_invoices,

                "partial_payment_invoices":
                    partial_payment_invoices,

                "pending_verification_invoices":
                    pending_verification_invoices,

                "status_summary":
                    status_summary,

                # ------------------------------------------------
                # Amounts
                # ------------------------------------------------

                "total_invoice_amount":
                    round(
                        total_invoice_amount,
                        2
                    ),

                "total_payable_amount":
                    round(
                        total_payable_amount,
                        2
                    ),

                "total_collected_amount":
                    round(
                        total_collected_amount,
                        2
                    ),

                # Actual amount that needs payment
                "outstanding_amount":
                    total_amount_due,

                # Complete balance from all invoices
                "total_balance_amount":
                    total_balance_amount,

                # Excess paid amount
                "excess_paid_amount":
                    total_excess_paid,

                # Amount that actually needs to be paid
                "amount_due":
                    total_amount_due,

                # ------------------------------------------------
                # Balance
                # ------------------------------------------------

                "balance_type_summary":
                    balance_summary,

                # ------------------------------------------------
                # Funds
                # ------------------------------------------------

                "management_fund":
                    round(
                        maintenance_fund,
                        2
                    ),

                "maintenance_fund":
                    round(
                        maintenance_fund,
                        2
                    ),

                "sinking_fund":
                    round(
                        sinking_fund,
                        2
                    ),

                # ------------------------------------------------
                # Monthly
                # ------------------------------------------------

                "monthly_trend":
                    monthly_trend,

                # ------------------------------------------------
                # Batch
                # ------------------------------------------------

                "total_batches":
                    total_batches,

                "generated_invoices":
                    total_invoices,

                "batch_summary":
                    batch_summary,

                "top_batch":
                    top_batch,
            }

        except Exception as ex:

            logger.exception(
                "Financial analysis failed"
            )

            raise Exception(
                f"Failed to analyze financial data: {str(ex)}"
            )