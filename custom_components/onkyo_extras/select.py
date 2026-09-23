"""Enumerated settings: display dimmer, dialog enhancement, late night."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import OnkyoExtrasConfigEntry
from .const import DIALOG_ENHANCEMENT_OPTIONS, DIMMER_OPTIONS, LATE_NIGHT_OPTIONS
from .entity import OnkyoExtrasEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: OnkyoExtrasConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    data = entry.runtime_data
    async_add_entities(
        [
            OnkyoExtrasSelect(
                data.client, data.unique_id, data.model, "DIM", "dim",
                "Display dimmer", DIMMER_OPTIONS, "mdi:brightness-6",
            ),
            OnkyoExtrasSelect(
                data.client, data.unique_id, data.model, "DGF", "dgf",
                "Dialog enhancement", DIALOG_ENHANCEMENT_OPTIONS, "mdi:message-text",
            ),
            OnkyoExtrasSelect(
                data.client, data.unique_id, data.model, "LTN", "ltn",
                "Late night", LATE_NIGHT_OPTIONS, "mdi:weather-night",
            ),
        ]
    )


class OnkyoExtrasSelect(OnkyoExtrasEntity, SelectEntity):
    """A tracked cmd whose raw value maps to a small set of named options."""

    def __init__(
        self,
        client,
        entry_unique_id: str,
        model: str,
        cmd: str,
        key: str,
        name: str,
        options: dict[str, str],
        icon: str,
    ) -> None:
        super().__init__(client, entry_unique_id, model, cmd, key)
        self._attr_name = name
        self._attr_icon = icon
        self._options_map = options
        self._reverse_map = {label: raw for raw, label in options.items()}
        self._attr_options = list(options.values())

    @property
    def current_option(self) -> str | None:
        value = self._client.values.get(self._cmd)
        if value is None or value == "N/A":
            return None
        return self._options_map.get(value)

    async def async_select_option(self, option: str) -> None:
        raw = self._reverse_map[option]
        await self._client.send(self._cmd + raw)
