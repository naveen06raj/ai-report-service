
import logging

from services.reports.property_list_client import PropertyListClient

logger = logging.getLogger(__name__)


class PropertyListService:

    def get_property_name(
        self,
        property_id: int,
        authorization: str,
    ) -> str:
        try:
            result = PropertyListClient().get_property_list(
                authorization=authorization
            )

            if result.get("response") != 1:
                raise ValueError(
                    result.get("message", "Property API request failed")
                )

            data = result.get("data") or {}
            properties = data.get("assinged_properties", [])

            for property_data in properties:
                if int(property_data.get("id", -1)) == int(property_id):
                    name = property_data.get("name")

                    if name:
                        return name

                    break

            raise ValueError(
                f"Property ID {property_id} was not found "
                "in the assigned property list"
            )

        except Exception as ex:
            logger.exception("Failed to fetch property name")
            raise Exception(
                f"Failed to fetch property name: {ex}"
            ) from ex