"""Pluggeasy measurements component — input register space, read-only."""

from __future__ import annotations

from modbus_connection.model import Component, gauge, integer


class PluggeasyMeasurements(Component):
    """Sensor measurements from the Pluggeasy ventilation unit (input registers)."""

    register_space = "input"

    communication_error = integer(4, signed=True)
    defrost_status = integer(5, signed=True)
    extract_air_temperature = gauge(25, 0.1, unit="°C")
    exhaust_air_temperature = gauge(26, 0.1, unit="°C")
    outdoor_air_temperature = gauge(27, 0.1, unit="°C")
    supply_air_temperature = gauge(28, 0.1, unit="°C")
    rh_extract_air = integer(29, signed=True, unit="%")
    rh_exhaust_air = integer(30, signed=True, unit="%")
    rh_outdoor_air = integer(31, signed=True, unit="%")
    rh_supply_air = integer(32, signed=True, unit="%")
    voltage_extract_motor = gauge(59, 0.1, unit="V")
    voltage_supply_motor = gauge(60, 0.1, unit="V")
    rpm_extract_motor = integer(61, signed=True, unit="rpm")
    rpm_supply_motor = integer(62, signed=True, unit="rpm")
    bypass_damper_position = integer(63, signed=True)
    voc = integer(81, signed=True, unit="ppm")
    actual_working_mode = integer(90, signed=True)
