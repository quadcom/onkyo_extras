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
    Platform.MEDIA_PLAYER,
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
    "MVL",
    "AMT",
    "SLI",
    "LMD",
    "ZPW",
    "ZVL",
    "ZMT",
    "SLZ",
    "PW3",
    "VL3",
    "MT3",
    "SL3",
]

# Per-zone command prefixes for power, volume, mute and source select.
ZONE_COMMANDS = {
    1: {"power": "PWR", "volume": "MVL", "mute": "AMT", "source": "SLI"},
    2: {"power": "ZPW", "volume": "ZVL", "mute": "ZMT", "source": "SLZ"},
    3: {"power": "PW3", "volume": "VL3", "mute": "MT3", "source": "SL3"},
}

CONF_MAX_VOLUME = "max_volume"
CONF_SOUND_MODES = "sound_modes"

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

# LMD listening mode codes, uppercase, to display name.
LISTENING_MODES = {
    "00": "Stereo",
    "01": "Direct",
    "02": "Surround",
    "03": "Film",
    "04": "THX",
    "05": "Action",
    "06": "Musical",
    "07": "Mono Movie",
    "08": "Orchestra",
    "09": "Unplugged",
    "0A": "Studio-Mix",
    "0B": "TV Logic",
    "0C": "All Ch Stereo",
    "0D": "Theater-Dimensional",
    "0E": "Enhanced",
    "0F": "Mono",
    "11": "Pure Audio",
    "12": "Multiplex",
    "13": "Full Mono",
    "14": "Dolby Virtual",
    "15": "DTS Surround Sensation",
    "16": "Audyssey DSX",
    "17": "DTS Virtual:X",
    "40": "Straight Decode",
    "41": "Dolby EX/DTS ES",
    "42": "THX Cinema",
    "43": "THX Surround EX",
    "44": "THX Music",
    "45": "THX Games",
    "50": "THX U2/S2 Cinema",
    "51": "THX Music Mode",
    "52": "THX Games Mode",
    "80": "Dolby Atmos/Dolby Surround",
    "81": "PLII Music",
    "82": "DTS:X/Neural:X",
    "83": "Neo:6 Music",
    "84": "PLII THX Cinema",
    "85": "Neural:X THX Cinema",
    "86": "PLII Game",
    "87": "Neural Surround",
    "88": "Neural THX",
    "89": "PLII THX Games",
    "8A": "Neo:6 THX Games",
    "8B": "PLII THX Music",
    "8C": "Neo:6 THX Music",
    "FF": "Auto Surround",
}

DEFAULT_SOUND_MODES = ["00", "01", "11", "0C", "40", "42", "80", "82", "85", "FF"]

RECONNECT_DELAYS = [1, 2, 5, 10, 30]
POLL_INTERVAL_SECONDS = 300
WRITE_SPACING_SECONDS = 0.05
CONNECTION_EVENT = "__connection__"
CONNECT_TIMEOUT_SECONDS = 5
