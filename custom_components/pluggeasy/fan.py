"""Fan platform — ventilation speed control via preset modes."""

# Copyright 2024 Pluggeasy contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from homeassistant.components.fan import FanEntity, FanEntityFeature

from .entity import PluggeasyEntity
from .vendor.pluggeasy_modbus import SelectedAirflow

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from .coordinator import PluggeasyCoordinator
    from .data import PluggeasyConfigEntry

_DEFAULT_PRESET = "nominal"


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: PluggeasyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Pluggeasy fan."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities([PluggeasyFan(coordinator)])


class PluggeasyFan(PluggeasyEntity, FanEntity):
    """Primary fan entity — controls ventilation speed via selected_airflow preset."""

    _attr_name = None
    _attr_supported_features = (
        FanEntityFeature.PRESET_MODE
        | FanEntityFeature.TURN_ON
        | FanEntityFeature.TURN_OFF
    )
    _attr_preset_modes: ClassVar[list[str]] = [
        "low", "medium", "nominal", "auto", "snooze"
    ]

    def __init__(self, coordinator: PluggeasyCoordinator) -> None:
        """Initialize the fan."""
        super().__init__(coordinator, "parameters_selected_airflow", "parameters")

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        value = self._subsystem.selected_airflow
        if value is None:
            return None
        return value.name.lower()

    @property
    def is_on(self) -> bool | None:
        """Return True when the fan is running (not in snooze)."""
        mode = self.preset_mode
        if mode is None:
            return None
        return mode != "snooze"

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the ventilation speed preset."""
        await self.coordinator.data.parameters.write(
            "selected_airflow", SelectedAirflow[preset_mode.upper()]
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_on(
        self,
        percentage: int | None = None,  # noqa: ARG002
        preset_mode: str | None = None,
        **kwargs: Any,  # noqa: ARG002
    ) -> None:
        """Turn the fan on, optionally to a specific preset (default: nominal)."""
        await self.async_set_preset_mode(preset_mode or _DEFAULT_PRESET)

    async def async_turn_off(self, **kwargs: Any) -> None:  # noqa: ARG002
        """Turn the fan off by setting snooze mode."""
        await self.async_set_preset_mode("snooze")
