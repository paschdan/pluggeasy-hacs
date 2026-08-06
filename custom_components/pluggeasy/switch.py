"""Switch platform — writable coil controls."""

# Copyright 2024 Pluggeasy contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription

from .entity import PluggeasyEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from .coordinator import PluggeasyCoordinator
    from .data import PluggeasyConfigEntry


@dataclass(frozen=True, kw_only=True)
class PluggeasySwitchDescription(SwitchEntityDescription):
    """Describes a switch controlling one writable coil of one component."""

    component: str
    attribute: str


def _switch(attribute: str, name: str) -> PluggeasySwitchDescription:
    return PluggeasySwitchDescription(
        key=f"controls_{attribute}",
        name=name,
        component="controls",
        attribute=attribute,
    )


DESCRIPTIONS: tuple[PluggeasySwitchDescription, ...] = (
    _switch("reset_filter_alarm", "Reset Filter Alarm"),
    _switch("manual_bypass", "Manual Bypass"),
    _switch("allow_automatic_bypass", "Allow Automatic Bypass"),
    _switch("summer_mode", "Summer Mode"),
    _switch("manual_boost", "Manual Boost"),
    _switch("snooze_mode", "Snooze Mode"),
    _switch("working_mode_coil", "Working Mode"),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: PluggeasyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Pluggeasy switches."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        PluggeasySwitch(coordinator, description) for description in DESCRIPTIONS
    )


class PluggeasySwitch(PluggeasyEntity, SwitchEntity):
    """A single writable coil in the controls component."""

    entity_description: PluggeasySwitchDescription

    def __init__(
        self,
        coordinator: PluggeasyCoordinator,
        description: PluggeasySwitchDescription,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, description.key, description.component)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        """Return true if the coil is set."""
        return getattr(self._subsystem, self.entity_description.attribute)  # type: ignore[return-value]

    async def async_turn_on(self, **kwargs: Any) -> None:  # noqa: ARG002
        """Turn the switch on."""
        await self.coordinator.data.controls.write(  # type: ignore[union-attr]
            self.entity_description.attribute, True  # noqa: FBT003
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:  # noqa: ARG002
        """Turn the switch off."""
        await self.coordinator.data.controls.write(  # type: ignore[union-attr]
            self.entity_description.attribute, False  # noqa: FBT003
        )
        await self.coordinator.async_request_refresh()
