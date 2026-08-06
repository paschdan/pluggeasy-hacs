"""pluggeasy-modbus — read a Pluggeasy ventilation unit over Modbus.

Construct ``Pluggeasy(unit)`` with a ``modbus_connection.ModbusUnit``, call
``await device.async_update()``, then read its sub-systems as normal Python
objects::

    device.status.active_alarms
    device.measurements.extract_air_temperature
    device.controls.manual_bypass
    device.parameters.selected_airflow

"""

from .controls import PluggeasyControls
from .enums import (
    ActualWorkingMode,
    BypassDamperPosition,
    CommunicationError,
    DefrostStatus,
    SelectedAirflow,
)
from .measurements import PluggeasyMeasurements
from .parameters import PluggeasyParameters
from .pluggeasy import Pluggeasy
from .status import PluggeasyStatus

__all__ = [
    "ActualWorkingMode",
    "BypassDamperPosition",
    "CommunicationError",
    "DefrostStatus",
    "Pluggeasy",
    "PluggeasyControls",
    "PluggeasyMeasurements",
    "PluggeasyParameters",
    "PluggeasyStatus",
    "SelectedAirflow",
]
