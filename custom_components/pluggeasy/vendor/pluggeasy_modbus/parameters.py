"""Pluggeasy parameters component — holding register space, read-only."""

from __future__ import annotations

from modbus_connection.model import Component, gauge, integer


class PluggeasyParameters(Component):
    """Configuration parameters from the Pluggeasy ventilation unit.

    Holding register space, read-only.
    """

    bypass_min_outdoor_temp = gauge(63, 0.1, unit="°C")
    bypass_min_extract_temp = gauge(65, 0.1, unit="°C")
    bypass_min_extract_outdoor_diff = gauge(67, 0.1, unit="°C")
    selected_airflow = integer(132, signed=True)
    manual_bypass_timer = integer(56, signed=True)
    modbus_slave_address = integer(0, signed=True)
    modbus_baudrate = integer(1, signed=True)
    modbus_parity = integer(2, signed=True)
