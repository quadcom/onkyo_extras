"""HDR indicator, from field 9 of an IFV reply."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import OnkyoExtrasConfigEntry
from .const import IFV_INPUT_HDR
from .entity import OnkyoExtrasEntity

_NOT_HDR = {"", "sdr", "off", "-"}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: OnkyoExtrasConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    data = entry.runtime_data
    async_add_entities(
        [OnkyoExtrasHdrBinarySensor(data.client, data.unique_id, data.model)]
    )


class OnkyoExtrasHdrBinarySensor(OnkyoExtrasEntity, BinarySensorEntity):
    """On when the current video input carries an HDR format."""

    _attr_name = "HDR input"
    _attr_icon = "mdi:hdr"

    def __init__(self, client, entry_unique_id: str, model: str) -> None:
        super().__init__(client, entry_unique_id, model, "IFV", "hdr")

    def _hdr_field(self) -> str:
        value = self._client.values.get("IFV")
        if not value or value == "N/A":
            return ""
        fields = value.split(",")
        if IFV_INPUT_HDR >= len(fields):
            return ""
        return fields[IFV_INPUT_HDR].strip()

    @property
    def is_on(self) -> bool | None:
        value = self._client.values.get("IFV")
        if not value or value == "N/A":
            return None
        return self._hdr_field().lower() not in _NOT_HDR

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        return {"hdr_format": self._hdr_field()}
