"""Constants for the Onkyo Extras integration."""
from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "onkyo_extras"

DEFAULT_PORT = 60128

PLATFORMS = [
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SWITCH,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
]

# Commands we query on connect/reconnect and dispatch to entities.
TRACKED_COMMANDS = [
    "PWR",
    "IFA",
    "IFV",
    "SWL",
    "CTL",
    "TFR",
    "DIM",
    "DGF",
    "LTN",
    "RAS",
    "MOT",
]

DIMMER_OPTIONS = {
    "00": "Bright",
    "01": "Dim",
    "02": "Dark",
}

DIALOG_ENHANCEMENT_OPTIONS = {
    "00": "Off",
    "01": "Level 1",
    "03": "Level 3",
}

LATE_NIGHT_OPTIONS = {
    "00": "Off",
    "01": "Low",
    "02": "High",
    "03": "Auto",
}

# IFA reply fields, comma separated.
IFA_INPUT_PORT = 0
IFA_INPUT_FORMAT = 1
IFA_SAMPLE_RATE = 2
IFA_INPUT_CHANNELS = 3
IFA_LISTENING_MODE = 4
IFA_OUTPUT_CHANNELS = 5

# IFV reply fields, comma separated.
IFV_INPUT_PORT = 0
IFV_INPUT_RESOLUTION = 1
IFV_INPUT_COLOR_FORMAT = 2
IFV_INPUT_COLOR_DEPTH = 3
IFV_OUTPUT_PORT = 4
IFV_OUTPUT_RESOLUTION = 5
IFV_OUTPUT_COLOR_FORMAT = 6
IFV_OUTPUT_COLOR_DEPTH = 7
IFV_PICTURE_MODE = 8
IFV_INPUT_HDR = 9

RECONNECT_DELAYS = [1, 2, 5, 10, 30]
POLL_INTERVAL_SECONDS = 300
WRITE_SPACING_SECONDS = 0.05
CONNECTION_EVENT = "__connection__"
CONNECT_TIMEOUT_SECONDS = 5
