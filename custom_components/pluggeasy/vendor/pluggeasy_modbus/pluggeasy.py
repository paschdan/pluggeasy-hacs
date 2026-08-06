"""Pluggeasy device object — composes the 4 component models."""

from __future__ import annotations

from typing import TYPE_CHECKING

from modbus_connection.model import Component, ComponentGroup

from .controls import PluggeasyControls
from .measurements import PluggeasyMeasurements
from .parameters import PluggeasyParameters
from .status import PluggeasyStatus

if TYPE_CHECKING:
    from modbus_connection import ModbusUnit


class Pluggeasy:
    """A Pluggeasy ventilation unit accessed over Modbus."""

    DEFAULT_UNIT_ID = 1
    DEFAULT_TCP_PORT = 8899

    def __init__(self, unit: ModbusUnit) -> None:
        self._unit = unit
        self.status = PluggeasyStatus(unit)
        self.controls = PluggeasyControls(unit)
        self.measurements = PluggeasyMeasurements(unit)
        self.parameters = PluggeasyParameters(unit)
        self._group = ComponentGroup(unit, self.components)

    @property
    def components(self) -> tuple[Component, ...]:
        """Return all component subsystems."""
        return (self.status, self.controls, self.measurements, self.parameters)

    async def async_update(self) -> None:
        """Refresh all components in pooled Modbus reads."""
        await self._group.async_update()
