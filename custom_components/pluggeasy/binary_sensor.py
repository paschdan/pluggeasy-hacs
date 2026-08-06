"""Binary-sensor platform — discrete-input status flags."""

# Copyright 2024 Pluggeasy contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory

from .entity import PluggeasyEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from .coordinator import PluggeasyCoordinator
    from .data import PluggeasyConfigEntry


@dataclass(frozen=True, kw_only=True)
class PluggeasyBinaryDescription(BinarySensorEntityDescription):
    """Describes a binary sensor reading one discrete input of one component."""

    component: str
    attribute: str


def _binary(
    attribute: str,
    name: str,
    device_class: BinarySensorDeviceClass | None = None,
) -> PluggeasyBinaryDescription:
    return PluggeasyBinaryDescription(
        key=f"status_{attribute}",
        name=name,
        component="status",
        attribute=attribute,
        device_class=device_class,
        entity_category=EntityCategory.DIAGNOSTIC,
    )


DESCRIPTIONS: tuple[PluggeasyBinaryDescription, ...] = (
    _binary("active_alarms", "Active Alarms", BinarySensorDeviceClass.PROBLEM),
    _binary("filter_alarm", "Filter Alarm", BinarySensorDeviceClass.PROBLEM),
    _binary(
        "extract_air_sensor_fault",
        "Extract Air Sensor Fault",
        BinarySensorDeviceClass.PROBLEM,
    ),
    _binary(
        "exhaust_air_sensor_fault",
        "Exhaust Air Sensor Fault",
        BinarySensorDeviceClass.PROBLEM,
    ),
    _binary(
        "outdoor_air_sensor_fault",
        "Outdoor Air Sensor Fault",
        BinarySensorDeviceClass.PROBLEM,
    ),
    _binary(
        "supply_air_sensor_fault",
        "Supply Air Sensor Fault",
        BinarySensorDeviceClass.PROBLEM,
    ),
    _binary(
        "extract_air_fan_fault",
        "Extract Air Fan Fault",
        BinarySensorDeviceClass.PROBLEM,
    ),
    _binary(
        "supply_air_fan_fault",
        "Supply Air Fan Fault",
        BinarySensorDeviceClass.PROBLEM,
    ),
    _binary(
        "automatic_bypass_active",
        "Automatic Bypass Active",
        BinarySensorDeviceClass.RUNNING,
    ),
    _binary(
        "boost_contact_active",
        "Boost Contact Active",
        BinarySensorDeviceClass.RUNNING,
    ),
    _binary(
        "boost_active",
        "Boost Active",
        BinarySensorDeviceClass.RUNNING,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: PluggeasyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Pluggeasy binary sensors."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        PluggeasyBinarySensor(coordinator, description) for description in DESCRIPTIONS
    )


class PluggeasyBinarySensor(PluggeasyEntity, BinarySensorEntity):
    """A single discrete input read from the status component."""

    entity_description: PluggeasyBinaryDescription

    def __init__(
        self,
        coordinator: PluggeasyCoordinator,
        description: PluggeasyBinaryDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, description.key, description.component)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        """Return true if the discrete input is set."""
        return getattr(self._subsystem, self.entity_description.attribute)  # type: ignore[return-value]
