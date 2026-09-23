"""Shared base entity for Onkyo Extras."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo, Entity

from .const import CONNECTION_EVENT, DOMAIN
from .eiscp import EiscpClient


class OnkyoExtrasEntity(Entity):
    """Common device info, availability and listener wiring."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        client: EiscpClient,
        entry_unique_id: str,
        model: str,
        cmd: str | None,
        key: str,
        cmds: tuple[str, ...] | None = None,
        power_cmd: str | None = None,
    ) -> None:
        self._client = client
        self._cmd = cmd
        self._cmds = cmds
        self._power_cmd = power_cmd if power_cmd is not None else cmd
        self._attr_unique_id = f"{entry_unique_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_unique_id)},
            name=model,
            manufacturer="Onkyo",
            model=model,
        )
        self._remove_listener = None

    async def async_added_to_hass(self) -> None:
        watched = self._cmds if self._cmds is not None else (self._cmd,)

        def listener(cmd: str, value: str) -> None:
            if cmd == CONNECTION_EVENT or cmd in watched:
                self.async_write_ha_state()

        self._remove_listener = self._client.add_listener(listener)

    async def async_will_remove_from_hass(self) -> None:
        if self._remove_listener:
            self._remove_listener()
            self._remove_listener = None

    @property
    def available(self) -> bool:
        if not self._client.connected:
            return False
        if self._cmds is not None:
            value = self._client.values.get(self._power_cmd)
            return value is not None and value != "N/A"
        if self._cmd is None:
            return True
        value = self._client.values.get(self._cmd)
        return value is not None and value != "N/A"
