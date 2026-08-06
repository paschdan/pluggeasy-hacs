"""Select platform — ventilation mode setpoint control."""

# Copyright 2024 Pluggeasy contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from homeassistant.components.select import SelectEntity

from .entity import PluggeasyEntity
from .vendor.pluggeasy_modbus import SelectedAirflow

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
    """Set up Pluggeasy select."""
    async_add_entities([PluggeasyVentilationModeSelect(entry.runtime_data.coordinator)])


class PluggeasyVentilationModeSelect(PluggeasyEntity, SelectEntity):
    """Select entity for the ventilation mode setpoint (parameters.selected_airflow)."""

    _attr_translation_key = "ventilation_mode"
    _attr_options: ClassVar[list[str]] = ["low", "medium", "nominal", "auto", "snooze"]
    _attr_icon = "mdi:fan"

    def __init__(self, coordinator: PluggeasyCoordinator) -> None:
        """Initialize the select."""
        super().__init__(coordinator, "parameters_ventilation_mode", "parameters")
        self._optimistic: str | None = None

    @property
    def current_option(self) -> str | None:
        """Return the currently selected option."""
        if self._optimistic is not None:
            return self._optimistic
        value = self._subsystem.selected_airflow  # type: ignore[union-attr]
        return value.name.lower() if value is not None else None

    async def async_select_option(self, option: str) -> None:
        """Select a ventilation mode."""
        await self.coordinator.data.parameters.write(  # type: ignore[union-attr]
            "selected_airflow", SelectedAirflow[option.upper()]
        )
        self._optimistic = option
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    def _handle_coordinator_update(self) -> None:
        """Clear optimistic state on coordinator refresh so live value wins."""
        self._optimistic = None
        super()._handle_coordinator_update()
