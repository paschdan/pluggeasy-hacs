"""DataUpdateCoordinator that polls the Pluggeasy ventilation unit."""

# Copyright 2024 Pluggeasy contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from modbus_connection import ModbusError
from pluggeasy_modbus import Pluggeasy

from .const import DOMAIN, LOGGER, SCAN_INTERVAL

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from modbus_connection.pymodbus import ModbusConnection

    from .data import PluggeasyConfigEntry


class PluggeasyCoordinator(DataUpdateCoordinator[Pluggeasy]):
    """Refreshes every sub-system on a schedule."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: PluggeasyConfigEntry,
        device: Pluggeasy,
        connection: ModbusConnection,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=SCAN_INTERVAL,
        )
        self.device = device
        self.connection = connection

    async def _async_update_data(self) -> Pluggeasy:
        """Fetch data from the ventilation unit."""
        # Don't start a Modbus read while Home Assistant is shutting down: the
        # in-flight request would be cancelled and surface as a spurious
        # "Request cancelled outside library" error. Return the last data instead.
        if self.hass.is_stopping:
            return self.device
        try:
            # connect() is a no-op when already connected and rebuilds the client
            # after a dropped link, so the integration self-heals after a network
            # blip instead of staying dead until a manual reload.
            await self.connection.connect()
            await self.device.async_update()
        except ModbusError as err:
            msg = f"Error communicating with Pluggeasy: {err}"
            raise UpdateFailed(msg) from err
        return self.device
