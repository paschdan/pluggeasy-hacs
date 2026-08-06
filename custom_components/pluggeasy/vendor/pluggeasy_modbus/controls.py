"""Pluggeasy controls component — coil (bit) space, writable."""

from __future__ import annotations

from modbus_connection.model import Component, coil


class PluggeasyControls(Component):
    """Writable control coils for the Pluggeasy ventilation unit."""

    reset_filter_alarm = coil(0, writable=True)
    manual_bypass = coil(7, writable=True)
    allow_automatic_bypass = coil(8, writable=True)
    summer_mode = coil(9, writable=True)
    manual_boost = coil(16, writable=True)
    snooze_mode = coil(17, writable=True)
    working_mode_coil = coil(25, writable=True)
