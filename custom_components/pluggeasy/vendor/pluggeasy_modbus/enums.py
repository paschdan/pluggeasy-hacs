"""Pluggeasy IntEnums — authoritative value mappings from the datasheet."""

from __future__ import annotations

from enum import IntEnum


class SelectedAirflow(IntEnum):
    LOW = 0
    MEDIUM = 1
    NOMINAL = 2
    AUTO = 3
    SNOOZE = 4


class ActualWorkingMode(IntEnum):
    SNOOZE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    BOOST = 4
    AUTO_HUMIDITY = 5
    AUTO_VOC = 6
    AUTO_0_10V = 7
    BOOST_IN_AUTO = 8
    WEEKLY_1 = 9
    WEEKLY_2 = 10
    WEEKLY_3 = 11
    WEEKLY_4 = 12


class DefrostStatus(IntEnum):
    NOT_ACTIVE = 0
    FIREPLACE_DEFROST = 1
    PRE_HEATER = 2
    UNBALANCED_AIRFLOWS = 3


class CommunicationError(IntEnum):
    NO_ERROR = 0
    REMOTE_CONTROLLER = 1
    MODBUS_RTU = 4


class BypassDamperPosition(IntEnum):
    CLOSED = 0
    OPEN = 1
    ERROR = 2
