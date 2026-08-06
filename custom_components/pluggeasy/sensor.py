"""Sensor platform — measurements and parameters from the ventilation unit."""

# Copyright 2024 Pluggeasy contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    EntityCategory,
    UnitOfElectricPotential,
    UnitOfTemperature,
)

from .entity import PluggeasyEntity
from .vendor.pluggeasy_modbus import (
    ActualWorkingMode,
    BypassDamperPosition,
    CommunicationError,
    DefrostStatus,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from .coordinator import PluggeasyCoordinator
    from .data import PluggeasyConfigEntry


@dataclass(frozen=True, kw_only=True)
class PluggeasySensorDescription(SensorEntityDescription):
    """Describes a sensor reading one attribute of one component."""

    component: str
    attribute: str
    is_enum: bool = False


def _temp(
    component: str,
    attribute: str,
    name: str,
) -> PluggeasySensorDescription:
    return PluggeasySensorDescription(
        key=f"{component}_{attribute}",
        name=name,
        component=component,
        attribute=attribute,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    )


def _humidity(
    attribute: str,
    name: str,
) -> PluggeasySensorDescription:
    return PluggeasySensorDescription(
        key=f"measurements_{attribute}",
        name=name,
        component="measurements",
        attribute=attribute,
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    )


def _voltage(
    attribute: str,
    name: str,
) -> PluggeasySensorDescription:
    return PluggeasySensorDescription(
        key=f"measurements_{attribute}",
        name=name,
        component="measurements",
        attribute=attribute,
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    )


def _rpm(
    attribute: str,
    name: str,
) -> PluggeasySensorDescription:
    return PluggeasySensorDescription(
        key=f"measurements_{attribute}",
        name=name,
        component="measurements",
        attribute=attribute,
        native_unit_of_measurement="rpm",
        state_class=SensorStateClass.MEASUREMENT,
    )


def _diag(
    component: str,
    attribute: str,
    name: str,
) -> PluggeasySensorDescription:
    return PluggeasySensorDescription(
        key=f"{component}_{attribute}",
        name=name,
        component=component,
        attribute=attribute,
        entity_category=EntityCategory.DIAGNOSTIC,
    )


def _enum_sensor(
    component: str,
    attribute: str,
    name: str,
    enum_class: type[IntEnum],
) -> PluggeasySensorDescription:
    return PluggeasySensorDescription(
        key=f"{component}_{attribute}",
        name=name,
        component=component,
        attribute=attribute,
        device_class=SensorDeviceClass.ENUM,
        options=[m.name.lower() for m in enum_class],
        entity_category=EntityCategory.DIAGNOSTIC,
        is_enum=True,
    )


DESCRIPTIONS: tuple[PluggeasySensorDescription, ...] = (
    # --- Component 3: PluggeasyMeasurements (input registers) ---
    # Diagnostic enum sensors
    _enum_sensor(
        "measurements", "communication_error", "Communication Error", CommunicationError
    ),
    _enum_sensor("measurements", "defrost_status", "Defrost Status", DefrostStatus),
    # Temperatures (gauge, precision 1)
    _temp("measurements", "extract_air_temperature", "Extract Air Temperature"),
    _temp("measurements", "exhaust_air_temperature", "Exhaust Air Temperature"),
    _temp("measurements", "outdoor_air_temperature", "Outdoor Air Temperature"),
    _temp("measurements", "supply_air_temperature", "Supply Air Temperature"),
    # Humidity
    _humidity("rh_extract_air", "Relative Humidity Extract Air"),
    _humidity("rh_exhaust_air", "Relative Humidity Exhaust Air"),
    _humidity("rh_outdoor_air", "Relative Humidity Outdoor Air"),
    _humidity("rh_supply_air", "Relative Humidity Supply Air"),
    # Voltage (gauge, precision 1)
    _voltage("voltage_extract_motor", "Control Voltage Extract Motor"),
    _voltage("voltage_supply_motor", "Control Voltage Supply Motor"),
    # RPM
    _rpm("rpm_extract_motor", "RPM Extract Motor"),
    _rpm("rpm_supply_motor", "RPM Supply Motor"),
    # Diagnostic enum sensor
    _enum_sensor(
        "measurements",
        "bypass_damper_position",
        "Bypass Damper Position",
        BypassDamperPosition,
    ),
    # VOC
    PluggeasySensorDescription(
        key="measurements_voc",
        name="VOC",
        component="measurements",
        attribute="voc",
        device_class=SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # Diagnostic enum sensor
    _enum_sensor(
        "measurements", "actual_working_mode", "Actual Working Mode", ActualWorkingMode
    ),
    # --- Component 4: PluggeasyParameters (holding registers) ---
    # Temperatures (gauge, precision 1)
    _temp("parameters", "bypass_min_outdoor_temp", "Bypass Min Outdoor Temperature"),
    _temp("parameters", "bypass_min_extract_temp", "Bypass Min Extract Temperature"),
    _temp(
        "parameters",
        "bypass_min_extract_outdoor_diff",
        "Bypass Min Extract-Outdoor Difference",
    ),
    # Plain integers
    _diag("parameters", "manual_bypass_timer", "Manual By-Pass Timer"),
    _diag("parameters", "modbus_slave_address", "Modbus Slave Address"),
    _diag("parameters", "modbus_baudrate", "Modbus Baudrate"),
    _diag("parameters", "modbus_parity", "Modbus Parity"),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: PluggeasyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Pluggeasy sensors."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        PluggeasySensor(coordinator, description) for description in DESCRIPTIONS
    )


class PluggeasySensor(PluggeasyEntity, SensorEntity):
    """A single value read from a component attribute."""

    entity_description: PluggeasySensorDescription

    def __init__(
        self,
        coordinator: PluggeasyCoordinator,
        description: PluggeasySensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, description.key, description.component)
        self.entity_description = description

    @property
    def native_value(self) -> object:
        """Return the current sensor value."""
        value = getattr(self._subsystem, self.entity_description.attribute)
        if self.entity_description.is_enum:
            if value is None:
                return None
            if isinstance(value, IntEnum):
                return value.name.lower()
        return value
