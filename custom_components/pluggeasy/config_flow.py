"""Config flow for the Pluggeasy integration."""

# Copyright 2024 Pluggeasy contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from modbus_connection import ModbusError
from modbus_connection.tmodbus import ModbusConnection, ModbusTcpParams

from .const import (
    CONF_HOST,
    CONF_PORT,
    CONF_UNIT_ID,
    DEFAULT_PORT,
    DEFAULT_UNIT_ID,
    DOMAIN,
    LOGGER,
)
from .vendor.pluggeasy_modbus import Pluggeasy


class PluggeasyFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Pluggeasy."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host: str = user_input[CONF_HOST]
            port: int = int(user_input[CONF_PORT])
            unit_id: int = int(user_input[CONF_UNIT_ID])

            try:
                await self._async_probe(host, port, unit_id)
            except ModbusError as err:
                LOGGER.error(
                    "Cannot connect to Pluggeasy at %s:%s unit %s: %s",
                    host,
                    port,
                    unit_id,
                    err,
                )
                errors["base"] = "cannot_connect"
            else:
                unique_id = f"{host}_{unit_id}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Pluggeasy {host}",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST,
                        default=(user_input or {}).get(CONF_HOST, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Required(
                        CONF_PORT,
                        default=(user_input or {}).get(CONF_PORT, DEFAULT_PORT),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=65535,
                            mode=selector.NumberSelectorMode.BOX,
                        ),
                    ),
                    vol.Required(
                        CONF_UNIT_ID,
                        default=(user_input or {}).get(CONF_UNIT_ID, DEFAULT_UNIT_ID),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=247,
                            mode=selector.NumberSelectorMode.BOX,
                        ),
                    ),
                }
            ),
            errors=errors,
        )

    async def _async_probe(self, host: str, port: int, unit_id: int) -> None:
        """Open a temporary connection and do one update to verify reachability."""
        connection = ModbusConnection(
            # RTU-over-TCP gateway — framer fixed to "rtu" (see __init__.py).
            ModbusTcpParams(host=host, port=port, framer="rtu"),
            message_spacing=0.03,
        )
        try:
            unit = connection.for_unit(unit_id)
            device = Pluggeasy(unit)
            await device.async_update()
        finally:
            connection.close()
