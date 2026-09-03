from collections import Counter
from datetime import datetime


class KeyCollectionAnalyzer:

    STATUS_MAP = {
        0: "New",
        1: "Cancelled",
        2: "Pending",
        3: "Collected"
    }

    @staticmethod
    def analyze(
        report_data: dict
    ) -> dict:

        # ==================================================
        # Validate Report Data
        # ==================================================

        if not isinstance(
            report_data,
            dict
        ):
            raise ValueError(
                "Expected report_data to be a dictionary"
            )

        # --------------------------------------------------
        # Get Records
        # --------------------------------------------------

        records = report_data.get(
            "data",
            []
        )

        if not isinstance(
            records,
            list
        ):
            raise ValueError(
                "Expected 'data' to be a list"
            )

        # ==================================================
        # Counters
        # ==================================================

        total_submissions = len(
            records
        )

        status_counter = Counter()

        unit_counter = Counter()

        resident_counter = Counter()

        appointment_dates = Counter()

        appointment_times = Counter()

        # ==================================================
        # Date Tracking
        # ==================================================

        earliest_submission = None

        latest_submission = None

        # ==================================================
        # Process Records
        # ==================================================

        for item in records:

            # --------------------------------------------------
            # Safety Check
            # --------------------------------------------------

            if not isinstance(
                item,
                dict
            ):
                continue

            # ==================================================
            # Submission Information
            # ==================================================

            submission = item.get(
                "submission_info"
            )

            if not isinstance(
                submission,
                dict
            ):
                submission = {}

            # ==================================================
            # Unit Information
            # ==================================================

            unit = item.get(
                "unit_info"
            )

            if not isinstance(
                unit,
                dict
            ):
                unit = {}

            # ==================================================
            # User Information
            # ==================================================

            user = item.get(
                "user_info"
            )

            if not isinstance(
                user,
                dict
            ):
                user = {}

            # --------------------------------------------------
            # Some API records may have user information inside
            # submission_info.getname.
            # --------------------------------------------------

            if not user:

                fallback_user = submission.get(
                    "getname"
                )

                if isinstance(
                    fallback_user,
                    dict
                ):
                    user = fallback_user

            # ==================================================
            # Status
            # ==================================================

            status_value = submission.get(
                "status"
            )

            # Convert string status to integer if required
            try:

                if status_value is not None:
                    status_value = int(
                        status_value
                    )

            except (
                TypeError,
                ValueError
            ):

                pass

            status = (
                KeyCollectionAnalyzer.STATUS_MAP.get(
                    status_value,
                    "Unknown"
                )
            )

            status_counter[
                status
            ] += 1

            # ==================================================
            # Unit
            # ==================================================

            unit_no = unit.get(
                "unit"
            )

            if unit_no:

                unit_counter[
                    str(unit_no)
                ] += 1

            # ==================================================
            # Resident
            # ==================================================

            resident = user.get(
                "name"
            )

            if resident:

                resident_counter[
                    str(resident)
                ] += 1

            # ==================================================
            # Appointment Date
            # ==================================================

            appt_date = submission.get(
                "appt_date"
            )

            if appt_date:

                appointment_dates[
                    str(appt_date)
                ] += 1

            # ==================================================
            # Appointment Time
            # ==================================================

            appt_time = submission.get(
                "appt_time"
            )

            if appt_time:

                appointment_times[
                    str(appt_time)
                ] += 1

            # ==================================================
            # Created Date
            # ==================================================

            created_at = submission.get(
                "created_at"
            )

            if created_at:

                try:

                    dt = datetime.strptime(
                        str(created_at),
                        "%Y-%m-%d %H:%M:%S"
                    )

                    if (
                        earliest_submission is None
                        or dt < earliest_submission
                    ):

                        earliest_submission = dt

                    if (
                        latest_submission is None
                        or dt > latest_submission
                    ):

                        latest_submission = dt

                except (
                    ValueError,
                    TypeError
                ):

                    # Ignore invalid date
                    pass

        # ==================================================
        # Completion Rate
        # ==================================================

        collected_count = status_counter.get(
            "Collected",
            0
        )

        completion_rate = (

            round(
                (
                    collected_count
                    / total_submissions
                ) * 100,
                2
            )

            if total_submissions > 0

            else 0
        )

        # ==================================================
        # Most Busy Date
        # ==================================================

        most_busy_date = ""

        if appointment_dates:

            most_busy_date = (
                appointment_dates
                .most_common(1)[0][0]
            )

        # ==================================================
        # Most Busy Time
        # ==================================================

        most_busy_time = ""

        if appointment_times:

            most_busy_time = (
                appointment_times
                .most_common(1)[0][0]
            )

        # ==================================================
        # Final Analytics
        # ==================================================

        analytics = {

            "total_submissions":
                total_submissions,

            "completion_rate":
                completion_rate,

            "status_summary":
                dict(
                    status_counter
                ),

            "unique_units":
                len(
                    unit_counter
                ),

            "top_units":
                unit_counter.most_common(
                    5
                ),

            "unique_residents":
                len(
                    resident_counter
                ),

            "top_residents":
                resident_counter.most_common(
                    5
                ),

            "appointments_by_date":
                dict(
                    appointment_dates
                ),

            "appointments_by_time":
                dict(
                    appointment_times
                ),

            "most_busy_date":
                most_busy_date,

            "most_busy_time":
                most_busy_time,

            "earliest_submission":
                (
                    earliest_submission.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    if earliest_submission
                    else ""
                ),

            "latest_submission":
                (
                    latest_submission.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    if latest_submission
                    else ""
                )
        }

        # ==================================================
        # Debug
        # ==================================================

        print("=" * 80)
        print("KEY COLLECTION ANALYTICS")
        print("=" * 80)

        print(
            "Total Submissions:",
            analytics[
                "total_submissions"
            ]
        )

        print(
            "Completion Rate:",
            analytics[
                "completion_rate"
            ]
        )

        print(
            "Status Summary:",
            analytics[
                "status_summary"
            ]
        )

        print(
            "Unique Units:",
            analytics[
                "unique_units"
            ]
        )

        print(
            "Unique Residents:",
            analytics[
                "unique_residents"
            ]
        )

        print(
            "Most Busy Date:",
            analytics[
                "most_busy_date"
            ]
        )

        print(
            "Most Busy Time:",
            analytics[
                "most_busy_time"
            ]
        )

        print(
            "Earliest Submission:",
            analytics[
                "earliest_submission"
            ]
        )

        print(
            "Latest Submission:",
            analytics[
                "latest_submission"
            ]
        )

        print("=" * 80)

        return analytics