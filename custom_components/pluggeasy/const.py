"""Constants for the Pluggeasy HACS integration."""

# Copyright 2024 Pluggeasy contributors
# SPDX-License-Identifier: Apache-2.0

from datetime import timedelta
from logging import Logger, getLogger
from typing import Final

LOGGER: Logger = getLogger(__package__)

DOMAIN: Final = "pluggeasy"

CONF_HOST: Final = "host"
CONF_PORT: Final = "port"
CONF_UNIT_ID: Final = "unit_id"
CONF_CONNECTION_TYPE: Final = "connection_type"
CONF_FRAMER: Final = "framer"
CONF_DEVICE: Final = "device"
CONF_BAUDRATE: Final = "baudrate"
CONF_BYTESIZE: Final = "bytesize"
CONF_PARITY: Final = "parity"
CONF_STOPBITS: Final = "stopbits"

DEFAULT_PORT: Final = 8899
DEFAULT_UNIT_ID: Final = 1
DEFAULT_CONNECTION_TYPE: Final = "tcp"
DEFAULT_TCP_FRAMER: Final = "socket"
DEFAULT_BAUDRATE: Final = 19200
DEFAULT_BYTESIZE: Final = 8
DEFAULT_PARITY: Final = "E"
DEFAULT_STOPBITS: Final = 1
DEFAULT_SERIAL_FRAMER: Final = "rtu"

TCP_FRAMERS: Final = ("socket", "rtu", "ascii")
SERIAL_FRAMERS: Final = ("rtu", "ascii")

SCAN_INTERVAL: Final = timedelta(seconds=30)
