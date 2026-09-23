"""On/off toggles: cinema filter, music optimizer."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import OnkyoExtrasConfigEntry
from .entity import OnkyoExtrasEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: OnkyoExtrasConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    data = entry.runtime_data
    async_add_entities(
        [
            OnkyoExtrasSwitch(
                data.client, data.unique_id, data.model, "RAS", "ras",
                "Cinema filter", "mdi:filter-variant",
            ),
            OnkyoExtrasSwitch(
                data.client, data.unique_id, data.model, "MOT", "mot",
                "Music optimizer", "mdi:music-note",
            ),
        ]
    )


class OnkyoExtrasSwitch(OnkyoExtrasEntity, SwitchEntity):
    """A tracked cmd whose value is "00" (off) or "01" (on)."""

    def __init__(
        self, client, entry_unique_id: str, model: str, cmd: str, key: str, name: str, icon: str
    ) -> None:
        super().__init__(client, entry_unique_id, model, cmd, key)
        self._attr_name = name
        self._attr_icon = icon

    @property
    def is_on(self) -> bool | None:
        value = self._client.values.get(self._cmd)
        if value is None or value == "N/A":
            return None
        return value == "01"

    async def async_turn_on(self, **kwargs) -> None:
        await self._client.send(self._cmd + "01")

    async def async_turn_off(self, **kwargs) -> None:
        await self._client.send(self._cmd + "00")
