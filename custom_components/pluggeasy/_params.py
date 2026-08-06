"""Shared Modbus params builder for the Pluggeasy integration."""

# Copyright 2024 Pluggeasy contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Mapping

from modbus_connection import ModbusSerialParams, ModbusTcpParams

try:
    from .const import (
        CONF_BAUDRATE,
        CONF_BYTESIZE,
        CONF_CONNECTION_TYPE,
        CONF_DEVICE,
        CONF_FRAMER,
        CONF_HOST,
        CONF_PARITY,
        CONF_PORT,
        CONF_STOPBITS,
        DEFAULT_BAUDRATE,
        DEFAULT_BYTESIZE,
        DEFAULT_PARITY,
        DEFAULT_PORT,
        DEFAULT_SERIAL_FRAMER,
        DEFAULT_STOPBITS,
        DEFAULT_TCP_FRAMER,
    )
except ImportError:
    from const import (  # type: ignore[no-redef]
        CONF_BAUDRATE,
        CONF_BYTESIZE,
        CONF_CONNECTION_TYPE,
        CONF_DEVICE,
        CONF_FRAMER,
        CONF_HOST,
        CONF_PARITY,
        CONF_PORT,
        CONF_STOPBITS,
        DEFAULT_BAUDRATE,
        DEFAULT_BYTESIZE,
        DEFAULT_PARITY,
        DEFAULT_PORT,
        DEFAULT_SERIAL_FRAMER,
        DEFAULT_STOPBITS,
        DEFAULT_TCP_FRAMER,
    )

ModbusParams = ModbusTcpParams | ModbusSerialParams


def build_params(data: Mapping[str, Any]) -> ModbusParams:
    """
    Build ModbusTcpParams or ModbusSerialParams from config-entry data.

    Backward-compatible: missing connection_type defaults to "tcp";
    missing framer defaults to "socket" for TCP and "rtu" for serial.
    """
    connection_type = data.get(CONF_CONNECTION_TYPE, "tcp")
    if connection_type == "tcp":
        return ModbusTcpParams(
            host=data[CONF_HOST],
            port=int(data.get(CONF_PORT, DEFAULT_PORT)),
            framer=data.get(CONF_FRAMER, DEFAULT_TCP_FRAMER),
        )
    return ModbusSerialParams(
        device=data[CONF_DEVICE],
        baudrate=int(data.get(CONF_BAUDRATE, DEFAULT_BAUDRATE)),
        bytesize=int(data.get(CONF_BYTESIZE, DEFAULT_BYTESIZE)),
        parity=data.get(CONF_PARITY, DEFAULT_PARITY),
        stopbits=int(data.get(CONF_STOPBITS, DEFAULT_STOPBITS)),
        framer=data.get(CONF_FRAMER, DEFAULT_SERIAL_FRAMER),
    )
