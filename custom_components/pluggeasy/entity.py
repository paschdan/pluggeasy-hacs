"""Base entity for Pluggeasy ventilation units."""

# Copyright 2024 Pluggeasy contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PluggeasyCoordinator


class PluggeasyEntity(CoordinatorEntity[PluggeasyCoordinator]):
    """Common identity + device-info for every Pluggeasy entity."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: PluggeasyCoordinator, key: str, component: str
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._component = component
        entry = coordinator.config_entry
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            manufacturer="Pluggit",
            model="Pluggeasy",
            name="Pluggeasy",
        )

    @property
    def _subsystem(self) -> object:
        """The library sub-system object this entity reads from."""
        return getattr(self.coordinator.data, self._component)
