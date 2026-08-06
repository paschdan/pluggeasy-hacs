"""Button platform — momentary controls for the ventilation unit."""

# Copyright 2024 Pluggeasy contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.button import ButtonEntity
from homeassistant.const import EntityCategory

from .entity import PluggeasyEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from .coordinator import PluggeasyCoordinator
    from .data import PluggeasyConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: PluggeasyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Pluggeasy buttons."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities([PluggeasyButton(coordinator)])


class PluggeasyButton(PluggeasyEntity, ButtonEntity):
    """Button to reset the filter alarm."""

    _attr_name = "Reset Filter Alarm"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_device_class = None

    def __init__(self, coordinator: PluggeasyCoordinator) -> None:
        """Initialize the button."""
        super().__init__(coordinator, "controls_reset_filter_alarm", "controls")

    async def async_press(self) -> None:
        """Press the button — write True to reset_filter_alarm coil."""
        await self.coordinator.data.controls.write("reset_filter_alarm", True)  # noqa: FBT003
        await self.coordinator.async_request_refresh()
