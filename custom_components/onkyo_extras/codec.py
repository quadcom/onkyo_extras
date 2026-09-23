"""Pure eISCP packet framing and value codecs. No Home Assistant imports."""
from __future__ import annotations

import re
import struct

ISCP_MAGIC = b"ISCP"
HEADER_SIZE = 16


def build_packet(message: str) -> bytes:
    """Build one eISCP packet carrying a message like "SWLQSTN"."""
    data = ("!1" + message + "\r").encode("utf-8")
    header = ISCP_MAGIC + struct.pack(">IIB3x", HEADER_SIZE, len(data), 1)
    return header + data


def parse_packets(buffer: bytes) -> tuple[list[str], bytes]:
    """Pull every complete message out of buffer, return (messages, leftover)."""
    messages: list[str] = []
    while True:
        idx = buffer.find(ISCP_MAGIC)
        if idx < 0:
            # keep a short tail in case it holds the start of "ISCP"
            if len(buffer) > len(ISCP_MAGIC) - 1:
                buffer = buffer[-(len(ISCP_MAGIC) - 1):]
            break
        if idx > 0:
            buffer = buffer[idx:]
        if len(buffer) < HEADER_SIZE:
            break
        header_size, data_size = struct.unpack(">II", buffer[4:12])
        total = header_size + data_size
        if len(buffer) < total:
            break
        data = buffer[header_size:total]
        buffer = buffer[total:]
        text = data.decode("utf-8", errors="ignore")
        if text.startswith("!1"):
            text = text[2:]
        text = text.rstrip("\x1a\r\n")
        if text:
            messages.append(text)
    return messages, buffer


def decode_half_db(value: str) -> float:
    """Decode a signed-hex count of 0.5 dB steps, e.g. "-06" -> -3.0."""
    if value in ("00", "+00"):
        return 0.0
    sign = -1 if value[0] == "-" else 1
    steps = int(value[1:], 16)
    return sign * steps * 0.5


def encode_half_db(value: float) -> str:
    """Encode a dB value as a signed-hex count of 0.5 dB steps."""
    steps = round(value / 0.5)
    if steps == 0:
        return "00"
    sign = "+" if steps > 0 else "-"
    return f"{sign}{abs(steps):02X}"


def decode_tone_value(value: str) -> int:
    """Decode one bass/treble field: "00" or a sign plus one hex digit of dB."""
    if value == "00":
        return 0
    sign = -1 if value[0] == "-" else 1
    return sign * int(value[1], 16)


def encode_tone_value(value: int) -> str:
    """Encode one bass/treble dB value as "00" or sign plus one hex digit."""
    if value == 0:
        return "00"
    sign = "+" if value > 0 else "-"
    return f"{sign}{abs(value):X}"


def decode_tone(value: str) -> tuple[int, int]:
    """Decode a TFR reply like "B+2T-A" into (bass, treble) dB values."""
    bass_raw = value[1:3]
    treble_raw = value[4:6]
    return decode_tone_value(bass_raw), decode_tone_value(treble_raw)


def parse_selectors(xml: str) -> list[tuple[str, str, int]]:
    """Pull (id, name, zone mask) out of an NRI reply's <selectorlist>."""
    selectors: list[tuple[str, str, int]] = []
    for tag in re.findall(r"<selector\b[^>]*/>", xml):
        attrs = dict(re.findall(r'(\w+)="([^"]*)"', tag))
        if attrs.get("value", "0") == "0":
            continue
        selector_id = attrs.get("id", "").upper()
        name = attrs.get("name", "")
        zone = int(attrs.get("zone", "0") or "0", 16)
        selectors.append((selector_id, name, zone))
    return selectors


def parse_zones(xml: str) -> dict[int, int]:
    """Pull {zone id: volmax} out of an NRI reply's <zonelist>, present zones only."""
    zones: dict[int, int] = {}
    for tag in re.findall(r"<zone\b[^>]*/>", xml):
        attrs = dict(re.findall(r'(\w+)="([^"]*)"', tag))
        if attrs.get("value") != "1":
            continue
        zone_id = int(attrs.get("id", "0") or "0")
        volmax = int(attrs.get("volmax", "100") or "100")
        zones[zone_id] = volmax
    if not zones:
        zones[1] = 100
    return zones


def decode_volume(value: str, volmax: int) -> float:
    """Decode a 2-digit hex raw step count into a 0..1 HA volume level."""
    raw = int(value, 16)
    return raw / (volmax * 2)


def encode_volume(level: float, volmax: int, max_percent: float) -> str:
    """Encode a 0..1 level as 2-digit hex raw steps, capped to max_percent."""
    capped = min(level, max_percent / 100)
    raw = round(capped * volmax * 2)
    return f"{raw:02X}"


def parse_nri(xml: str) -> tuple[str | None, str | None]:
    """Pull model and unique id out of an NRI reply's XML, by regex."""
    model_match = re.search(r"<model>([^<]+)</model>", xml)
    model = model_match.group(1) if model_match else None
    serial_match = re.search(r"<deviceserial>([^<]+)</deviceserial>", xml)
    if serial_match:
        unique_id = serial_match.group(1)
    else:
        id_match = re.search(r'<device\s+id="([^"]+)"', xml)
        unique_id = id_match.group(1) if id_match else None
    return model, unique_id
