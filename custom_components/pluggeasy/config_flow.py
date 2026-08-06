"""Config flow for the Pluggeasy integration."""

# Copyright 2024 Pluggeasy contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)
from modbus_connection import ModbusError
from modbus_connection.tmodbus import ModbusConnection

from ._params import build_params
from .const import (
    CONF_BAUDRATE,
    CONF_BYTESIZE,
    CONF_CONNECTION_TYPE,
    CONF_DEVICE,
    CONF_FRAMER,
    CONF_HOST,
    CONF_PARITY,
    CONF_PORT,
    CONF_STOPBITS,
    CONF_UNIT_ID,
    DEFAULT_BAUDRATE,
    DEFAULT_BYTESIZE,
    DEFAULT_PARITY,
    DEFAULT_PORT,
    DEFAULT_SERIAL_FRAMER,
    DEFAULT_STOPBITS,
    DEFAULT_TCP_FRAMER,
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
        user_input: dict[str, Any] | None = None,  # noqa: ARG002
    ) -> config_entries.ConfigFlowResult:
        """Show transport-type menu."""
        return self.async_show_menu(
            step_id="user",
            menu_options=["tcp", "serial"],
        )

    async def async_step_tcp(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle TCP connection setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            data = dict(user_input)
            data[CONF_CONNECTION_TYPE] = "tcp"

            try:
                await self._async_probe(data)
            except (ModbusError, OSError) as err:
                LOGGER.error(
                    "Cannot connect to Pluggeasy at %s:%s unit %s: %s",
                    data.get(CONF_HOST),
                    data.get(CONF_PORT),
                    data.get(CONF_UNIT_ID),
                    err,
                )
                errors["base"] = "cannot_connect"
            else:
                host = data[CONF_HOST]
                unit = int(data[CONF_UNIT_ID])
                unique_id = f"tcp_{host}_{unit}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Pluggeasy {host}",
                    data=data,
                )

        return self.async_show_form(
            step_id="tcp",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST,
                        default=(user_input or {}).get(CONF_HOST, vol.UNDEFINED),
                    ): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.TEXT),
                    ),
                    vol.Required(
                        CONF_PORT,
                        default=(user_input or {}).get(CONF_PORT, DEFAULT_PORT),
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=1,
                            max=65535,
                            mode=NumberSelectorMode.BOX,
                        ),
                    ),
                    vol.Required(
                        CONF_FRAMER,
                        default=(user_input or {}).get(CONF_FRAMER, DEFAULT_TCP_FRAMER),
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=["socket", "rtu", "ascii"],
                            mode=SelectSelectorMode.LIST,
                        ),
                    ),
                    vol.Required(
                        CONF_UNIT_ID,
                        default=(user_input or {}).get(CONF_UNIT_ID, DEFAULT_UNIT_ID),
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=1,
                            max=247,
                            mode=NumberSelectorMode.BOX,
                        ),
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_serial(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle Serial connection setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            data = dict(user_input)
            data[CONF_CONNECTION_TYPE] = "serial"

            try:
                await self._async_probe(data)
            except (ModbusError, OSError) as err:
                LOGGER.error(
                    "Cannot connect to Pluggeasy on %s unit %s: %s",
                    data.get(CONF_DEVICE),
                    data.get(CONF_UNIT_ID),
                    err,
                )
                errors["base"] = "cannot_connect"
            else:
                device = data[CONF_DEVICE]
                unit = int(data[CONF_UNIT_ID])
                unique_id = f"serial_{device}_{unit}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Pluggeasy {device}",
                    data=data,
                )

        return self.async_show_form(
            step_id="serial",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_DEVICE,
                        default=(user_input or {}).get(CONF_DEVICE, vol.UNDEFINED),
                    ): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.TEXT),
                    ),
                    vol.Required(
                        CONF_BAUDRATE,
                        default=(user_input or {}).get(CONF_BAUDRATE, DEFAULT_BAUDRATE),
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(value="4800", label="4800"),
                                SelectOptionDict(value="9600", label="9600"),
                                SelectOptionDict(value="19200", label="19200"),
                                SelectOptionDict(value="38400", label="38400"),
                            ],
                            mode=SelectSelectorMode.LIST,
                        ),
                    ),
                    vol.Required(
                        CONF_PARITY,
                        default=(user_input or {}).get(CONF_PARITY, DEFAULT_PARITY),
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(value="N", label="None (N)"),
                                SelectOptionDict(value="E", label="Even (E)"),
                                SelectOptionDict(value="O", label="Odd (O)"),
                            ],
                            mode=SelectSelectorMode.LIST,
                        ),
                    ),
                    vol.Required(
                        CONF_BYTESIZE,
                        default=(user_input or {}).get(CONF_BYTESIZE, DEFAULT_BYTESIZE),
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(value="7", label="7"),
                                SelectOptionDict(value="8", label="8"),
                            ],
                            mode=SelectSelectorMode.LIST,
                        ),
                    ),
                    vol.Required(
                        CONF_STOPBITS,
                        default=(user_input or {}).get(CONF_STOPBITS, DEFAULT_STOPBITS),
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(value="1", label="1"),
                                SelectOptionDict(value="2", label="2"),
                            ],
                            mode=SelectSelectorMode.LIST,
                        ),
                    ),
                    vol.Required(
                        CONF_FRAMER,
                        default=(user_input or {}).get(
                            CONF_FRAMER, DEFAULT_SERIAL_FRAMER
                        ),
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=["rtu", "ascii"],
                            mode=SelectSelectorMode.LIST,
                        ),
                    ),
                    vol.Required(
                        CONF_UNIT_ID,
                        default=(user_input or {}).get(CONF_UNIT_ID, DEFAULT_UNIT_ID),
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=1,
                            max=247,
                            mode=NumberSelectorMode.BOX,
                        ),
                    ),
                }
            ),
            errors=errors,
        )

    async def _async_probe(self, data: dict[str, Any]) -> None:
        """Open a temporary connection and do one update to verify reachability."""
        connection = ModbusConnection(
            build_params(data),
            message_spacing=0.03,
        )
        try:
            unit = connection.for_unit(int(data[CONF_UNIT_ID]))
            device = Pluggeasy(unit)
            await device.async_update()
        finally:
            # ModbusConnection.close() is a coroutine and MUST be awaited;
            # a bare call leaves the coroutine un-awaited and the socket dangling,
            # which previously surfaced as a spurious "cannot_connect".
            await connection.close()
