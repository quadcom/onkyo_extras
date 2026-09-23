"""On-screen menu navigation: send-only OSD keys."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import OnkyoExtrasConfigEntry
from .entity import OnkyoExtrasEntity

_BUTTONS = [
    ("menu", "Menu", "MENU", "mdi:menu"),
    ("up", "Up", "UP", "mdi:arrow-up"),
    ("down", "Down", "DOWN", "mdi:arrow-down"),
    ("left", "Left", "LEFT", "mdi:arrow-left"),
    ("right", "Right", "RIGHT", "mdi:arrow-right"),
    ("enter", "Enter", "ENTER", "mdi:keyboard-return"),
    ("exit", "Exit", "EXIT", "mdi:exit-to-app"),
    ("quick", "Quick menu", "QUICK", "mdi:menu-open"),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: OnkyoExtrasConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    data = entry.runtime_data
    async_add_entities(
        OnkyoExtrasOsdButton(data.client, data.unique_id, data.model, key, name, osd_key, icon)
        for key, name, osd_key, icon in _BUTTONS
    )


class OnkyoExtrasOsdButton(OnkyoExtrasEntity, ButtonEntity):
    """Sends one OSD key. There is nothing to query, so cmd is None."""

    def __init__(
        self, client, entry_unique_id: str, model: str, key: str, name: str, osd_key: str, icon: str
    ) -> None:
        super().__init__(client, entry_unique_id, model, None, key)
        self._attr_name = name
        self._attr_icon = icon
        self._osd_key = osd_key

    async def async_press(self) -> None:
        await self._client.send("OSD" + self._osd_key)
