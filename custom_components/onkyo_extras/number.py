"""Level and tone controls: subwoofer, center, bass, treble."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import UnitOfSoundPressure
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import OnkyoExtrasConfigEntry
from .codec import decode_half_db, decode_tone, encode_half_db, encode_tone_value
from .entity import OnkyoExtrasEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: OnkyoExtrasConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    data = entry.runtime_data
    async_add_entities(
        [
            OnkyoExtrasLevelNumber(
                data.client, data.unique_id, data.model, "SWL", "swl",
                "Subwoofer level", -15.0, 12.0, "mdi:speaker",
            ),
            OnkyoExtrasLevelNumber(
                data.client, data.unique_id, data.model, "CTL", "ctl",
                "Center level", -12.0, 12.0, "mdi:account-voice",
            ),
            OnkyoExtrasToneNumber(
                data.client, data.unique_id, data.model, "bass", "Bass",
            ),
            OnkyoExtrasToneNumber(
                data.client, data.unique_id, data.model, "treble", "Treble",
            ),
        ]
    )


class OnkyoExtrasLevelNumber(OnkyoExtrasEntity, NumberEntity):
    """SWL/CTL: signed half-dB-step level, encoded as 2-digit hex."""

    _attr_mode = NumberMode.SLIDER
    _attr_native_step = 0.5
    _attr_native_unit_of_measurement = UnitOfSoundPressure.DECIBEL

    def __init__(
        self,
        client,
        entry_unique_id: str,
        model: str,
        cmd: str,
        key: str,
        name: str,
        min_value: float,
        max_value: float,
        icon: str,
    ) -> None:
        super().__init__(client, entry_unique_id, model, cmd, key)
        self._attr_name = name
        self._attr_icon = icon
        self._attr_native_min_value = min_value
        self._attr_native_max_value = max_value

    @property
    def native_value(self) -> float | None:
        value = self._client.values.get(self._cmd)
        if not value or value == "N/A":
            return None
        try:
            return decode_half_db(value)
        except (ValueError, IndexError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        await self._client.send(self._cmd + encode_half_db(value))


class OnkyoExtrasToneNumber(OnkyoExtrasEntity, NumberEntity):
    """Bass or treble part of TFR: -10..10 dB in 2 dB steps."""

    _attr_native_min_value = -10
    _attr_native_max_value = 10
    _attr_native_step = 2
    _attr_native_unit_of_measurement = UnitOfSoundPressure.DECIBEL
    _attr_icon = "mdi:equalizer"

    def __init__(self, client, entry_unique_id: str, model: str, part: str, name: str) -> None:
        super().__init__(client, entry_unique_id, model, "TFR", part)
        self._part = part
        self._attr_name = name

    @property
    def native_value(self) -> float | None:
        value = self._client.values.get("TFR")
        if not value or value == "N/A":
            return None
        try:
            bass, treble = decode_tone(value)
        except (ValueError, IndexError):
            return None
        return bass if self._part == "bass" else treble

    async def async_set_native_value(self, value: float) -> None:
        letter = "B" if self._part == "bass" else "T"
        await self._client.send("TFR" + letter + encode_tone_value(int(value)))
