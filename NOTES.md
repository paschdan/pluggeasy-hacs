# NOTES — pluggeasy-hacs

## Cross-repo links

| Repo | Purpose |
| :--- | :--- |
| **[pluggeasy-modbus](https://github.com/paschdan/pluggeasy-modbus)** | Transport-agnostic Python device library |
| **[pluggeasy-core](https://github.com/paschdan/pluggeasy-core)** | HA core integration (shared `modbus_connection` component) |
| **[pluggeasy-hacs](https://github.com/paschdan/pluggeasy-hacs)** (this repo) | HACS custom integration (own-connection, self-contained) |

## Versions

| Artifact | Version | Notes |
| :--- | :--- | :--- |
| This HACS integration | `0.3.0` | `custom_components/pluggeasy/manifest.json` `version` field. |
| Vendored `pluggeasy_modbus` | `0.2.0` | Copied from `pluggeasy-modbus` `0.2.0` release; lives at `custom_components/pluggeasy/vendor/pluggeasy_modbus/`. Refresh with `scripts/vendor.sh`. |
| `modbus-connection[tmodbus]` | `>=3.6` | Listed in `manifest.json` `requirements`; installed by HA at runtime. |
| Minimum Home Assistant | `2026.6.4` | Declared in `hacs.json`. |

## Architecture note

This integration uses the **own-connection** model: the config flow asks for transport details and creates a `ModbusConnection(build_params(entry.data))` directly. This makes it fully self-contained — no shared `modbus_connection` HA component is required, so it works today without unreleased HA core components.

The `build_params()` helper (in `_params.py`) is shared between the config-flow probe (`_async_probe`) and the runtime setup (`async_setup_entry`), so both always use the same connection parameters. It supports:

- **TCP + Socket** (default) — native Modbus TCP; matches `modbus: type: tcp` in classic HA YAML.
- **TCP + RTU / ASCII** — RTU-over-TCP or ASCII-over-TCP gateway modes.
- **Serial + RTU / ASCII** — RS-485 serial; datasheet defaults: 19200 baud, 8 data bits, EVEN parity, 1 stop bit.

Backward-compat: entries created before v0.3.0 (no `connection_type` key) default to TCP + Socket on load.

The `pluggeasy_modbus` device library is **vendored** (not listed in `requirements`) so it is always available offline. Only `modbus-connection[tmodbus]` (the transport layer) is a pip requirement.

For the HA core integration that uses the shared `modbus_connection` component, see [`pluggeasy-core`](https://github.com/paschdan/pluggeasy-core).

## What changed in 0.3.0

- **`_params.py`** (new) — `build_params(data)` shared helper builds `ModbusTcpParams` or `ModbusSerialParams` from config-entry data with backward-compat defaults.
- **`const.py`** — added `CONF_CONNECTION_TYPE`, `CONF_FRAMER`, `CONF_DEVICE`, `CONF_BAUDRATE`, `CONF_BYTESIZE`, `CONF_PARITY`, `CONF_STOPBITS` and matching defaults/tuples.
- **`config_flow.py`** — replaced single `async_step_user` with menu → `async_step_tcp` / `async_step_serial`; `_async_probe` now accepts full data dict and uses `build_params()`; unique IDs prefixed `tcp_` / `serial_`.
- **`__init__.py`** — replaced hardcoded `ModbusTcpParams(host, port, framer="rtu")` with `ModbusConnection(build_params(entry.data), message_spacing=0.03)`; removed now-unused `host`/`port` locals and `ModbusTcpParams` import.
- **`translations/en.json`** — added `step.user` menu labels, `step.tcp` and `step.serial` with data/data_description.
- **`manifest.json`** — version bumped to `0.3.0`.

## What changed in 0.2.0

- **`fan.py`** (new) — `PluggeasyFan` entity with preset modes `low`, `medium`, `nominal`, `auto`, `snooze`. `turn_on` defaults to `nominal`; `turn_off` sets `snooze`. Writes `selected_airflow` holding register via `async_set_airflow()`.
- **`button.py`** (new) — `PluggeasyButton` entity (category: config) for filter alarm reset. Calls `async_reset_filter_alarm()`.
- **`sensor.py`** — `actual_working_mode`, `defrost_status`, `communication_error`, `bypass_damper_position` converted to `SensorDeviceClass.ENUM` sensors with human-readable state names. `selected_airflow` sensor removed (now fan entity). Total: 24 sensors (was 25).
- **`switch.py`** — `working_mode` coil switch and `reset_filter_alarm` switch removed. Total: 5 switches (was 7).
- **`binary_sensor.py`** — `boost_mode_active` renamed to `boost_active`; reads the corrected `status.boost_active` property (inverted).
- **`__init__.py`** — `Platform.FAN` and `Platform.BUTTON` added.
- **`translations/en.json`** — fan/button names and enum state translations added.
- **Vendored library** — updated to `pluggeasy_modbus` 0.2.0 (enums, writable airflow, boost inversion fix).
