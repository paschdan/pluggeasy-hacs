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

DEFAULT_PORT: Final = 8899
DEFAULT_UNIT_ID: Final = 1

SCAN_INTERVAL: Final = timedelta(seconds=30)
