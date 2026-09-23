"""Read-only audio/video format fields, parsed from IFA and IFV."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import OnkyoExtrasConfigEntry
from .const import (
    IFA_INPUT_CHANNELS,
    IFA_INPUT_FORMAT,
    IFA_INPUT_PORT,
    IFA_LISTENING_MODE,
    IFA_OUTPUT_CHANNELS,
    IFA_SAMPLE_RATE,
    IFV_INPUT_COLOR_DEPTH,
    IFV_INPUT_COLOR_FORMAT,
    IFV_INPUT_PORT,
    IFV_INPUT_RESOLUTION,
    IFV_OUTPUT_COLOR_DEPTH,
    IFV_OUTPUT_COLOR_FORMAT,
    IFV_OUTPUT_PORT,
    IFV_OUTPUT_RESOLUTION,
)
from .entity import OnkyoExtrasEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: OnkyoExtrasConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    data = entry.runtime_data
    client, unique_id, model = data.client, data.unique_id, data.model
    entities = [
        OnkyoExtrasFieldSensor(client, unique_id, model, "IFA", "audio_input_port", "Audio input port", IFA_INPUT_PORT, "mdi:audio-input-rca"),
        OnkyoExtrasFieldSensor(client, unique_id, model, "IFA", "audio_input_format", "Audio input format", IFA_INPUT_FORMAT, "mdi:surround-sound"),
        OnkyoExtrasFieldSensor(client, unique_id, model, "IFA", "audio_sample_rate", "Audio sample rate", IFA_SAMPLE_RATE, "mdi:sine-wave"),
        OnkyoExtrasFieldSensor(client, unique_id, model, "IFA", "audio_input_channels", "Audio input channels", IFA_INPUT_CHANNELS, "mdi:surround-sound"),
        OnkyoExtrasFieldSensor(client, unique_id, model, "IFA", "listening_mode", "Listening mode", IFA_LISTENING_MODE, "mdi:speaker-multiple"),
        OnkyoExtrasFieldSensor(client, unique_id, model, "IFA", "audio_output_channels", "Audio output channels", IFA_OUTPUT_CHANNELS, "mdi:surround-sound"),
        OnkyoExtrasFieldSensor(client, unique_id, model, "IFV", "video_input_port", "Video input port", IFV_INPUT_PORT, "mdi:hdmi-port"),
        OnkyoExtrasFieldSensor(client, unique_id, model, "IFV", "video_input_resolution", "Video input resolution", IFV_INPUT_RESOLUTION, "mdi:video-input-hdmi"),
        OnkyoExtrasFieldSensor(client, unique_id, model, "IFV", "video_input_color_format", "Video input color format", IFV_INPUT_COLOR_FORMAT, "mdi:palette"),
        OnkyoExtrasFieldSensor(client, unique_id, model, "IFV", "video_input_color_depth", "Video input color depth", IFV_INPUT_COLOR_DEPTH, "mdi:palette"),
        OnkyoExtrasFieldSensor(client, unique_id, model, "IFV", "video_output_port", "Video output port", IFV_OUTPUT_PORT, "mdi:hdmi-port"),
        OnkyoExtrasFieldSensor(client, unique_id, model, "IFV", "video_output_resolution", "Video output resolution", IFV_OUTPUT_RESOLUTION, "mdi:television"),
        OnkyoExtrasFieldSensor(client, unique_id, model, "IFV", "video_output_color_format", "Video output color format", IFV_OUTPUT_COLOR_FORMAT, "mdi:palette"),
        OnkyoExtrasFieldSensor(client, unique_id, model, "IFV", "video_output_color_depth", "Video output color depth", IFV_OUTPUT_COLOR_DEPTH, "mdi:palette"),
    ]
    async_add_entities(entities)


class OnkyoExtrasFieldSensor(OnkyoExtrasEntity, SensorEntity):
    """One comma-separated field of an IFA or IFV reply."""

    def __init__(
        self,
        client,
        entry_unique_id: str,
        model: str,
        cmd: str,
        key: str,
        name: str,
        field_index: int,
        icon: str,
    ) -> None:
        super().__init__(client, entry_unique_id, model, cmd, key)
        self._attr_name = name
        self._attr_icon = icon
        self._field_index = field_index

    @property
    def native_value(self) -> str | None:
        value = self._client.values.get(self._cmd)
        if not value or value == "N/A":
            return None
        fields = value.split(",")
        if self._field_index >= len(fields):
            return None
        field = fields[self._field_index].strip()
        return field or None
