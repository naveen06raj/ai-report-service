from collections import Counter
from datetime import datetime


class KeyCollectionAnalyzer:

    STATUS_MAP = {
        0: "New",
        1: "Cancelled",
        2: "On Schedule",
        3: "Done"
    }

    @staticmethod
    def analyze(report_data: dict) -> dict:

        records = report_data.get("data", [])

        if not isinstance(records, list):
            raise ValueError("Expected 'data' to be a list")

        total_submissions = len(records)

        status_counter = Counter()
        unit_counter = Counter()
        resident_counter = Counter()
        appointment_dates = Counter()
        appointment_times = Counter()

        earliest_submission = None
        latest_submission = None

        for item in records:

            submission = item.get(
                "submission_info",
                {}
            )

            unit = item.get(
                "unit_info",
                {}
            )

            user = item.get(
                "user_info",
                {}
            )

            # ----------------------------------
            # Status
            # ----------------------------------

            status_value = submission.get(
                "status"
            )

            status = KeyCollectionAnalyzer.STATUS_MAP.get(
                status_value,
                "Unknown"
            )

            status_counter[
                status
            ] += 1

            # ----------------------------------
            # Unit
            # ----------------------------------

            unit_no = unit.get(
                "unit"
            )

            if unit_no:

                unit_counter[
                    unit_no
                ] += 1

            # ----------------------------------
            # Resident
            # ----------------------------------

            resident = user.get(
                "name"
            )

            if resident:

                resident_counter[
                    resident
                ] += 1

            # ----------------------------------
            # Appointment Date
            # ----------------------------------

            appt_date = submission.get(
                "appt_date"
            )

            if appt_date:

                appointment_dates[
                    appt_date
                ] += 1

            # ----------------------------------
            # Appointment Time
            # ----------------------------------

            appt_time = submission.get(
                "appt_time"
            )

            if appt_time:

                appointment_times[
                    appt_time
                ] += 1

            # ----------------------------------
            # Created Date
            # ----------------------------------

            created_at = submission.get(
                "created_at"
            )

            if created_at:

                try:

                    dt = datetime.strptime(
                        created_at,
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

                except Exception:
                    pass

        # ----------------------------------
        # Completion Rate
        # ----------------------------------

        done_count = status_counter.get(
            "Done",
            0
        )

        completion_rate = round(
            (
                done_count / total_submissions
            ) * 100,
            2
        ) if total_submissions > 0 else 0

        # ----------------------------------
        # Final Analytics
        # ----------------------------------

        return {

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
                unit_counter.most_common(5),

            "unique_residents":
                len(
                    resident_counter
                ),

            "top_residents":
                resident_counter.most_common(5),

            "appointments_by_date":
                dict(
                    appointment_dates
                ),

            "appointments_by_time":
                dict(
                    appointment_times
                ),

            "most_busy_date":
                appointment_dates.most_common(1)[0][0]
                if appointment_dates
                else "",

            "most_busy_time":
                appointment_times.most_common(1)[0][0]
                if appointment_times
                else "",

            "earliest_submission":
                earliest_submission.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                if earliest_submission
                else "",

            "latest_submission":
                latest_submission.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                if latest_submission
                else ""
        }