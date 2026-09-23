"""Config flow: host and port, validated by connecting and asking NRIQSTN."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT

from .codec import parse_nri
from .const import DEFAULT_PORT, DOMAIN
from .eiscp import EiscpClient

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
    }
)


class OnkyoExtrasConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Onkyo Extras."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]
            client = EiscpClient(host, port)
            try:
                await client.connect()
            except OSError:
                errors["base"] = "cannot_connect"
            else:
                nri = await client.request("NRIQSTN", "NRI", timeout=3.0)
                await client.close()
                model = None
                unique_id = None
                if nri:
                    model, unique_id = parse_nri(nri)
                if not unique_id:
                    unique_id = host
                if not model:
                    model = "Onkyo receiver"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=model,
                    data={CONF_HOST: host, CONF_PORT: port},
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
