"""Onkyo Extras: extra controls for an Onkyo/Integra receiver over eISCP."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .codec import parse_nri, parse_selectors, parse_zones
from .const import DEFAULT_PORT, PLATFORMS, TRACKED_COMMANDS, ZONE_COMMANDS
from .eiscp import EiscpClient


@dataclass
class OnkyoExtrasData:
    """Runtime data for one config entry."""

    client: EiscpClient
    unique_id: str
    model: str
    selectors: list[tuple[str, str, int]]
    zones: dict[int, int]


type OnkyoExtrasConfigEntry = ConfigEntry[OnkyoExtrasData]


async def async_setup_entry(hass: HomeAssistant, entry: OnkyoExtrasConfigEntry) -> bool:
    """Connect to the receiver and set up its platforms."""
    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)
    client = EiscpClient(host, port)

    try:
        await client.connect()
    except OSError as err:
        raise ConfigEntryNotReady(f"Cannot connect to {host}:{port}") from err

    nri = await client.request("NRIQSTN", "NRI", timeout=3.0)
    model = None
    unique_id = None
    selectors: list[tuple[str, str, int]] = []
    zones: dict[int, int] = {1: 100}
    if nri:
        model, unique_id = parse_nri(nri)
        selectors = parse_selectors(nri)
        zones = parse_zones(nri)
    if not unique_id:
        unique_id = entry.unique_id or host
    if not model:
        model = "Onkyo receiver"

    zone_commands = {cmd for cmds in ZONE_COMMANDS.values() for cmd in cmds.values()}
    query_cmds = [cmd for cmd in TRACKED_COMMANDS if cmd not in zone_commands]
    for zone_id in sorted(zones):
        if zone_id in ZONE_COMMANDS:
            query_cmds.extend(ZONE_COMMANDS[zone_id].values())
    for cmd in query_cmds:
        await client.query(cmd)

    entry.runtime_data = OnkyoExtrasData(
        client=client, unique_id=unique_id, model=model, selectors=selectors, zones=zones
    )
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_update_listener(hass: HomeAssistant, entry: OnkyoExtrasConfigEntry) -> None:
    """Reload the entry when its options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: OnkyoExtrasConfigEntry) -> bool:
    """Unload platforms and close the connection."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        await entry.runtime_data.client.close()
    return unload_ok
