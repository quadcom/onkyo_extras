"""Media player: one entity per zone the receiver reports as present."""
from __future__ import annotations

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import OnkyoExtrasConfigEntry
from .codec import decode_volume, encode_volume
from .const import (
    CONF_MAX_VOLUME,
    CONF_SOUND_MODES,
    DEFAULT_SOUND_MODES,
    IFA_LISTENING_MODE,
    LISTENING_MODES,
    ZONE_COMMANDS,
)
from .entity import OnkyoExtrasEntity

_ZONE_NAMES = {2: "Zone 2", 3: "Zone 3"}
_ZONE_BITS = {1: 0x01, 2: 0x02, 3: 0x04}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: OnkyoExtrasConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    data = entry.runtime_data
    async_add_entities(
        OnkyoExtrasMediaPlayer(
            data.client, data.unique_id, data.model, zone_id, volmax, data.selectors, entry
        )
        for zone_id, volmax in data.zones.items()
        if zone_id in ZONE_COMMANDS
    )


class OnkyoExtrasMediaPlayer(OnkyoExtrasEntity, MediaPlayerEntity):
    """One receiver zone: power, volume, mute, source and (zone 1) sound mode."""

    _attr_device_class = MediaPlayerDeviceClass.RECEIVER

    def __init__(
        self,
        client,
        entry_unique_id: str,
        model: str,
        zone_id: int,
        volmax: int,
        selectors: list[tuple[str, str, int]],
        entry: OnkyoExtrasConfigEntry,
    ) -> None:
        cmds = ZONE_COMMANDS[zone_id]
        super().__init__(
            client,
            entry_unique_id,
            model,
            None,
            f"zone{zone_id}",
            cmds=tuple(cmds.values()),
            power_cmd=cmds["power"],
        )
        self._zone_id = zone_id
        self._zone_cmds = cmds
        self._volmax = volmax
        self._entry = entry

        bit = _ZONE_BITS[zone_id]
        sources = [(sid, name) for sid, name, zone_mask in selectors if zone_mask & bit]
        self._source_by_id = {sid: name for sid, name in sources}
        self._source_id_by_name = {name: sid for sid, name in sources}
        self._attr_source_list = [name for _, name in sources]

        features = (
            MediaPlayerEntityFeature.TURN_ON
            | MediaPlayerEntityFeature.TURN_OFF
            | MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.VOLUME_STEP
            | MediaPlayerEntityFeature.VOLUME_MUTE
            | MediaPlayerEntityFeature.SELECT_SOURCE
        )
        if zone_id == 1:
            self._attr_name = None
            self._attr_supported_features = features | MediaPlayerEntityFeature.SELECT_SOUND_MODE
            codes = entry.options.get(CONF_SOUND_MODES, DEFAULT_SOUND_MODES)
            self._attr_sound_mode_list = [
                LISTENING_MODES[code] for code in codes if code in LISTENING_MODES
            ]
        else:
            self._attr_name = _ZONE_NAMES[zone_id]
            self._attr_supported_features = features

    def _max_volume(self) -> float:
        return self._entry.options.get(CONF_MAX_VOLUME, 100)

    @property
    def state(self) -> MediaPlayerState | None:
        value = self._client.values.get(self._zone_cmds["power"])
        if value == "01":
            return MediaPlayerState.ON
        if value == "00":
            return MediaPlayerState.OFF
        return None

    @property
    def volume_level(self) -> float | None:
        value = self._client.values.get(self._zone_cmds["volume"])
        if not value or value == "N/A":
            return None
        try:
            return decode_volume(value, self._volmax)
        except ValueError:
            return None

    @property
    def is_volume_muted(self) -> bool | None:
        value = self._client.values.get(self._zone_cmds["mute"])
        if value is None or value == "N/A":
            return None
        return value == "01"

    def _current_source_id(self) -> str | None:
        value = self._client.values.get(self._zone_cmds["source"])
        if not value or value == "N/A":
            return None
        return value.upper()

    @property
    def source(self) -> str | None:
        source_id = self._current_source_id()
        if source_id is None:
            return None
        return self._source_by_id.get(source_id, source_id)

    @property
    def sound_mode(self) -> str | None:
        if self._zone_id != 1:
            return None
        ifa = self._client.values.get("IFA")
        if ifa and ifa != "N/A":
            fields = ifa.split(",")
            if len(fields) > IFA_LISTENING_MODE:
                name = fields[IFA_LISTENING_MODE].strip()
                if name:
                    return name
        code = self._client.values.get("LMD")
        if not code or code == "N/A":
            return None
        return LISTENING_MODES.get(code, code)

    @property
    def extra_state_attributes(self) -> dict[str, str | None] | None:
        if self._zone_id != 1:
            return None
        code = self._client.values.get("LMD")
        return {
            "listening_mode_code": code if code and code != "N/A" else None,
            "source_id": self._current_source_id(),
        }

    async def async_turn_on(self) -> None:
        await self._client.send(self._zone_cmds["power"] + "01")

    async def async_turn_off(self) -> None:
        await self._client.send(self._zone_cmds["power"] + "00")

    async def async_mute_volume(self, mute: bool) -> None:
        await self._client.send(self._zone_cmds["mute"] + ("01" if mute else "00"))

    async def async_set_volume_level(self, volume: float) -> None:
        raw = encode_volume(volume, self._volmax, self._max_volume())
        await self._client.send(self._zone_cmds["volume"] + raw)

    async def async_volume_up(self) -> None:
        step = 1 / (self._volmax * 2)
        current = self.volume_level or 0.0
        cap = self._max_volume() / 100
        if current + step > cap:
            await self.async_set_volume_level(cap)
            return
        await self._client.send(self._zone_cmds["volume"] + "UP")

    async def async_volume_down(self) -> None:
        await self._client.send(self._zone_cmds["volume"] + "DOWN")

    async def async_select_source(self, source: str) -> None:
        source_id = self._source_id_by_name.get(source, source)
        await self._client.send(self._zone_cmds["source"] + source_id)

    async def async_select_sound_mode(self, sound_mode: str) -> None:
        for code, name in LISTENING_MODES.items():
            if name == sound_mode:
                await self._client.send("LMD" + code)
                return
