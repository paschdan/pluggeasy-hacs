"""Pluggeasy status component — discrete input (bit) space, read-only."""

from __future__ import annotations

from modbus_connection.model import Component, discrete_input


class PluggeasyStatus(Component):
    """Binary status flags from the Pluggeasy ventilation unit (discrete inputs)."""

    active_alarms = discrete_input(0)
    filter_alarm = discrete_input(1)
    extract_air_sensor_fault = discrete_input(6)
    exhaust_air_sensor_fault = discrete_input(7)
    outdoor_air_sensor_fault = discrete_input(8)
    supply_air_sensor_fault = discrete_input(9)
    extract_air_fan_fault = discrete_input(10)
    supply_air_fan_fault = discrete_input(11)
    automatic_bypass_active = discrete_input(15)
    boost_contact_active = discrete_input(28)
    # Datasheet 10030: 0=Boost ACTIVE, 1=Boost NOT active (inverted logic).
    # discrete_input has no inverted kwarg, so we expose the raw field privately
    # and invert in the property below.
    _boost_active_raw = discrete_input(29)

    @property
    def boost_active(self) -> bool | None:
        raw = self._boost_active_raw
        return None if raw is None else not raw
