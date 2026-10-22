
import json
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class LLMResponseParser:
    """
    Parses LLM responses into plain text, JSON, or a standardized
    structured response that can be rendered by the frontend.
    """

    ALLOWED_CHART_TYPES = {"bar", "line", "pie", "doughnut"}

    # ============================================================
    # Parse JSON Response
    # ============================================================

    def parse_json(self, response_text: str) -> dict:
        """Parse a JSON object, including optional Markdown fences."""

        if not response_text or not str(response_text).strip():
            raise ValueError("Empty response received from LLM")

        cleaned_text = str(response_text).strip()

        if cleaned_text.startswith("```"):
            lines = cleaned_text.splitlines()

            # Remove opening fence, such as ```json.
            if lines:
                lines = lines[1:]

            # Remove closing fence.
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            cleaned_text = "\n".join(lines).strip()

        try:
            parsed = json.loads(cleaned_text)
        except json.JSONDecodeError as ex:
            logger.warning("LLM returned invalid JSON: %s", ex)
            raise ValueError(f"Invalid JSON response: {ex}") from ex

        if not isinstance(parsed, dict):
            raise ValueError("LLM JSON response must be a JSON object")

        return parsed

    # ============================================================
    # Normalization Helpers
    # ============================================================

    @staticmethod
    def _to_text(value: Any) -> str:
        """Convert a value into safe display text."""
        if value is None:
            return ""
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, (int, float, bool)):
            return str(value)
        return str(value).strip()

    @classmethod
    def _normalize_section(cls, section: Any) -> Dict[str, Any] | None:
        if not isinstance(section, dict):
            return None

        title = cls._to_text(section.get("title"))
        items = section.get("items", [])

        if not isinstance(items, list):
            items = []

        normalized_items = [
            cls._to_text(item)
            for item in items
            if item is not None
        ]

        return {
            "title": title,
            "items": normalized_items
        }

    @classmethod
    def _normalize_table(cls, table: Any) -> Dict[str, Any] | None:
        if not isinstance(table, dict):
            return None

        title = cls._to_text(table.get("title"))
        columns = table.get("columns", [])
        rows = table.get("rows", [])

        if not isinstance(columns, list):
            columns = []

        if not isinstance(rows, list):
            rows = []

        normalized_columns = [cls._to_text(column) for column in columns]

        normalized_rows = []

        for row in rows:
            if not isinstance(row, (list, tuple)):
                continue

            normalized_row = [cls._to_text(cell) for cell in row]

            # Keep table rows consistent with the declared columns.
            if normalized_columns:
                normalized_row = normalized_row[:len(normalized_columns)]

                while len(normalized_row) < len(normalized_columns):
                    normalized_row.append("")

            normalized_rows.append(normalized_row)

        return {
            "title": title,
            "columns": normalized_columns,
            "rows": normalized_rows
        }

    @classmethod
    def _normalize_chart(cls, chart: Any) -> Dict[str, Any] | None:
        if not isinstance(chart, dict):
            return None

        chart_type = cls._to_text(chart.get("type") or "bar").lower()

        if chart_type not in cls.ALLOWED_CHART_TYPES:
            logger.warning("Ignoring unsupported chart type: %s", chart_type)
            return None

        title = cls._to_text(chart.get("title"))
        labels = chart.get("labels", [])
        values = chart.get("values", [])

        if not isinstance(labels, list) or not isinstance(values, list):
            return None

        if len(labels) != len(values):
            logger.warning("Ignoring chart with mismatched labels and values")
            return None

        normalized_labels = [cls._to_text(label) for label in labels]
        normalized_values = []

        for value in values:
            # Chart values must be numeric for frontend charting.
            if isinstance(value, bool):
                return None

            try:
                numeric_value = float(value)
            except (TypeError, ValueError):
                return None

            normalized_values.append(numeric_value)

        return {
            "type": chart_type,
            "title": title,
            "labels": normalized_labels,
            "values": normalized_values
        }

    # ============================================================
    # Parse Structured Response
    # ============================================================

    def parse_structured_response(
        self,
        response_text: str,
        fallback_text: str = ""
    ) -> Dict[str, Any]:
        """
        Return a stable frontend schema.

        {
            "type": "answer",
            "format": "structured",
            "content": {
                "text": "...",
                "sections": [],
                "tables": [],
                "charts": []
            },
            "follow_up_questions": []
        }
        """

        try:
            parsed = self.parse_json(response_text)

            content = parsed.get("content", {})

            if not isinstance(content, dict):
                content = {"text": self._to_text(content)}

            text = self._to_text(content.get("text"))

            sections = content.get("sections", [])
            tables = content.get("tables", [])
            charts = content.get("charts", [])
            follow_up_questions = parsed.get("follow_up_questions", [])

            if not isinstance(sections, list):
                sections = []

            if not isinstance(tables, list):
                tables = []

            if not isinstance(charts, list):
                charts = []

            if not isinstance(follow_up_questions, list):
                follow_up_questions = []

            normalized_sections = [
                normalized
                for item in sections
                if (normalized := self._normalize_section(item)) is not None
            ]

            normalized_tables = [
                normalized
                for item in tables
                if (normalized := self._normalize_table(item)) is not None
            ]

            normalized_charts = [
                normalized
                for item in charts
                if (normalized := self._normalize_chart(item)) is not None
            ]

            normalized_follow_ups = []
            for item in follow_up_questions:
                if isinstance(item, str) and item.strip():
                    question = item.strip()
                    if question not in normalized_follow_ups:
                        normalized_follow_ups.append(question)

                if len(normalized_follow_ups) >= 5:
                    break

            return {
                "type": "answer",
                "format": "structured",
                "content": {
                    "text": text,
                    "sections": normalized_sections,
                    "tables": normalized_tables,
                    "charts": normalized_charts
                },
                "follow_up_questions": normalized_follow_ups
            }

        except (ValueError, TypeError, AttributeError):
            logger.warning(
                "Could not parse structured LLM response; using text fallback"
            )

            text = self._to_text(fallback_text or response_text)

            # Do not expose a malformed JSON blob to the frontend.
            if text.startswith("{"):
                text = (
                    "I couldn't format the response correctly. "
                    "Please try your question again."
                )

            return {
                "type": "answer",
                "format": "structured",
                "content": {
                    "text": text,
                    "sections": [],
                    "tables": [],
                    "charts": []
                },
                "follow_up_questions": []
            }

    # ============================================================
    # Parse Plain Text Response
    # ============================================================

    def parse_text(self, response_text: str) -> str:
        """Return plain text for existing agents."""
        if not response_text:
            return ""
        return str(response_text).strip()

    # ============================================================
    # Parse Router Response
    # ============================================================

    def parse_router_response(self, response_text: str) -> str:
        """Validate a plain-text module-routing response."""

        if not response_text:
            return "fallback"

        module = str(response_text).strip().lower()

        allowed_modules = [
            "feedback",
            "facilities",
            "defect",
            "security",
            "fallback"
        ]

        if module not in allowed_modules:
            return "fallback"

        return module