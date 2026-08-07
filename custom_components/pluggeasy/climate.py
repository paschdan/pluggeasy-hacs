"""Climate platform — ventilation unit climate entity."""

# Copyright 2024 Pluggeasy contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from homeassistant.components.climate import (
    FAN_AUTO,
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
    FAN_OFF,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import UnitOfTemperature
from pluggeasy_modbus import SelectedAirflow

from .entity import PluggeasyEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from .coordinator import PluggeasyCoordinator
    from .data import PluggeasyConfigEntry

_TO_FAN: dict[SelectedAirflow, str] = {
    SelectedAirflow.SNOOZE: FAN_OFF,
    SelectedAirflow.AUTO: FAN_AUTO,
    SelectedAirflow.LOW: FAN_LOW,
    SelectedAirflow.MEDIUM: FAN_MEDIUM,
    SelectedAirflow.NOMINAL: FAN_HIGH,
}

_FROM_FAN: dict[str, SelectedAirflow] = {
    FAN_OFF: SelectedAirflow.SNOOZE,
    FAN_AUTO: SelectedAirflow.AUTO,
    FAN_LOW: SelectedAirflow.LOW,
    FAN_MEDIUM: SelectedAirflow.MEDIUM,
    FAN_HIGH: SelectedAirflow.NOMINAL,
}


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: PluggeasyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Pluggeasy climate."""
    async_add_entities([PluggeasyClimate(entry.runtime_data.coordinator)])


class PluggeasyClimate(PluggeasyEntity, ClimateEntity):
    """Climate entity for the Pluggeasy ventilation unit."""

    _attr_translation_key = "climate"
    _attr_name = None
    _attr_hvac_modes: ClassVar[list[HVACMode]] = [HVACMode.FAN_ONLY]
    _attr_supported_features = (
        ClimateEntityFeature.FAN_MODE | ClimateEntityFeature.TARGET_TEMPERATURE
    )
    _attr_fan_modes: ClassVar[list[str]] = [
        FAN_OFF,
        FAN_AUTO,
        FAN_LOW,
        FAN_MEDIUM,
        FAN_HIGH,
    ]
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_target_temperature_step = 0.1
    _attr_min_temp = 0.0
    _attr_max_temp = 35.0

    def __init__(self, coordinator: PluggeasyCoordinator) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator, "parameters_climate", "parameters")
        self._optimistic: str | None = None

    @property
    def hvac_mode(self) -> HVACMode:
        """Return the current HVAC mode (always FAN_ONLY)."""
        return HVACMode.FAN_ONLY

    @property
    def hvac_action(self) -> HVACAction:
        """Return the current HVAC action."""
        fm = self.fan_mode
        if fm is None or fm == FAN_OFF:
            return HVACAction.OFF
        return HVACAction.FAN

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature (supply air)."""
        data = self.coordinator.data
        if data is None or data.measurements is None:
            return None
        return data.measurements.supply_air_temperature  # type: ignore[no-any-return]

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature (mirrors supply air — read-only display)."""
        data = self.coordinator.data
        if data is None or data.measurements is None:
            return None
        return data.measurements.supply_air_temperature  # type: ignore[no-any-return]

    @property
    def fan_mode(self) -> str | None:
        """Return the current fan mode."""
        if self._optimistic is not None:
            return self._optimistic
        val = self.coordinator.data.parameters.selected_airflow  # type: ignore[union-attr]
        return _TO_FAN.get(val) if val is not None else None

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set the fan mode."""
        value = _FROM_FAN[fan_mode]
        await self.coordinator.data.parameters.write(  # type: ignore[union-attr]
            "selected_airflow", value
        )
        self._optimistic = fan_mode
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """No-op: unit has no room-target setpoint; mirrors supply air temp."""

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """No-op: only FAN_ONLY is supported."""

    def _handle_coordinator_update(self) -> None:
        """Clear optimistic state on coordinator refresh so live value wins."""
        self._optimistic = None
        super()._handle_coordinator_update()
