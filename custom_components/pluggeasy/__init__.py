"""Set up the Pluggeasy integration (own-connection model)."""

# Copyright 2024 Pluggeasy contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import Platform
from modbus_connection.tmodbus import ModbusConnection

from ._params import build_params
from .const import CONF_UNIT_ID
from .coordinator import PluggeasyCoordinator
from .data import PluggeasyData
from .vendor.pluggeasy_modbus import Pluggeasy

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from .data import PluggeasyConfigEntry

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.FAN,
    Platform.SENSOR,
    Platform.SWITCH,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PluggeasyConfigEntry,
) -> bool:
    """Set up Pluggeasy from a config entry."""
    connection = ModbusConnection(build_params(entry.data), message_spacing=0.03)
    entry.async_on_unload(connection.close)

    unit = connection.for_unit(int(entry.data[CONF_UNIT_ID]))
    device = Pluggeasy(unit)

    coordinator = PluggeasyCoordinator(hass, entry, device)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = PluggeasyData(coordinator=coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
