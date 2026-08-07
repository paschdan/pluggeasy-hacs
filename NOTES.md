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
| This HACS integration | `0.6.1` | `custom_components/pluggeasy/manifest.json` `version` field. |
| `pluggeasy-modbus` | `0.3.0` | Pip-installed from PyPI; declared in `manifest.json` `requirements`. See [paschdan/pluggeasy-modbus](https://github.com/paschdan/pluggeasy-modbus). |
| `modbus-connection[pymodbus]` | `>=3.9,<4` | Listed in `manifest.json` `requirements`; installed by HA at runtime. |
| Minimum Home Assistant | `2026.6.4` | Declared in `hacs.json`. |

## Architecture note

This integration uses the **own-connection** model: the config flow asks for transport details and creates a `ModbusConnection(build_params(entry.data))` directly. This makes it fully self-contained — no shared `modbus_connection` HA component is required, so it works today without unreleased HA core components.

The `build_params()` helper (in `_params.py`) is shared between the config-flow probe (`_async_probe`) and the runtime setup (`async_setup_entry`), so both always use the same connection parameters. It supports:

- **TCP + Socket** (default) — native Modbus TCP; matches `modbus: type: tcp` in classic HA YAML.
- **TCP + RTU / ASCII** — RTU-over-TCP or ASCII-over-TCP gateway modes.
- **Serial + RTU / ASCII** — RS-485 serial; datasheet defaults: 19200 baud, 8 data bits, EVEN parity, 1 stop bit.

Backward-compat: entries created before v0.3.0 (no `connection_type` key) default to TCP + Socket on load.

The `pluggeasy_modbus` device library is **pip-installed from PyPI** (`pluggeasy-modbus==0.3.0` in `manifest.json` `requirements`), consistent with the Core integration. Home Assistant installs it at runtime.

**Maintenance flow**: change the library → release a new version to PyPI → bump the `pluggeasy-modbus==` pin in both Core and HACS manifests.

For the HA core integration that uses the shared `modbus_connection` component, see [`pluggeasy-core`](https://github.com/paschdan/pluggeasy-core).

## What changed in 0.6.1

- **Graceful shutdown**: `coordinator._async_update_data` short-circuits when `hass.is_stopping`, and `__init__` closes the connection on `EVENT_HOMEASSISTANT_STOP`. Eliminates the spurious "Request cancelled outside library" ERROR logged when HA restarts (an in-flight read was being cancelled mid-request). Integration-layer only; no library change.

## What changed in 0.6.0

- **`climate.py`** — replaced `_TO_FAN`/`_FROM_FAN` dicts (which wrote `selected_airflow` directly) with `_LIB_TO_FAN`/`_FAN_TO_LIB` maps (library mode strings ↔ HA fan constants). `fan_mode` property now calls `effective_airflow_mode()` on the device; `async_set_fan_mode` calls `async_set_airflow_mode()`. Removed `SelectedAirflow` import.
- **`select.py`** — replaced direct `parameters.write("selected_airflow", SelectedAirflow[...])` with `async_set_airflow_mode()`; `current_option` now calls `effective_airflow_mode()` mapped through `_MODE_TO_LABEL` (`"off"→"snooze"`, `"high"→"nominal"`). Added `_LABEL_TO_MODE`/`_MODE_TO_LABEL` translation dicts. Removed `SelectedAirflow` import.
- **`manifest.json`** — `pluggeasy-modbus` pin bumped `0.2.0→0.3.0`; version `0.5.0→0.6.0`.
- **`requirements_dev.txt`** — `pluggeasy-modbus` bumped to `0.3.0`.
- **Fix**: climate `off` and select `snooze` now correctly engage the snooze coil via the library. **Note**: `off` = ~1-hour Snooze that auto-resumes — the entity flipping back to a running speed after ~1 h is expected behavior.

## What changed in 0.5.0

- **De-vendored `pluggeasy_modbus`** — removed `custom_components/pluggeasy/vendor/` and `scripts/vendor.sh`. The library is now declared as `pluggeasy-modbus==0.2.0` in `manifest.json` `requirements` and installed by HA from PyPI at runtime.
- **Import sites updated** — all 7 `from .vendor.pluggeasy_modbus import …` replaced with `from pluggeasy_modbus import …` in `coordinator.py`, `sensor.py`, `__init__.py`, `binary_sensor.py`, `select.py`, `climate.py`, `config_flow.py`.
- **`requirements_dev.txt`** — added `pluggeasy-modbus==0.2.0` for local tooling/type resolution.
- **No behavior change** — delivery-only refactor; entity logic is unchanged.

## What changed in 0.4.0

- **`climate.py`** (new) — `PluggeasyClimate` entity: `HVACMode.FAN_ONLY`; fan modes `off` / `auto` / `low` / `medium` / `high` mapped to `SelectedAirflow` (off → Snooze, auto → Auto, low → Low, medium → Medium, high → Nominal); read-only supply-air temperature exposed as both `current_temperature` and `target_temperature` (no writable setpoint); `set_temperature` is a no-op. Coexists with `select.pluggeasy_ventilation_mode`.
- **`sensor.py`** — 2 new air-level % sensors: `Supply Air Level` and `Return Air Level`. Stage approximation from `actual_working_mode`: snooze → 0 %, low → 33 %, medium → 66 %, high / boost / auto-variants → 66–100 %. Total: 26 sensors (was 24).
- **`binary_sensor.py`** — 3 new computed binary sensors: `Bypass Valve` (on when bypass damper position is `open`), `Summer Mode` (mirrors `switch.pluggeasy_summer_mode`), `Preheat` (on when defrost pre-heater is active). Total: 14 binary sensors (was 11).
- **`__init__.py`** — `Platform.CLIMATE` added to `PLATFORMS`.
- **`translations/en.json`** — names added for all 5 new entities.
- **`manifest.json`** — version bumped to `0.4.0`.
- **lovelace-comfoair card**: the new entity set enables [TimWeyand/lovelace-comfoair](https://github.com/TimWeyand/lovelace-comfoair) to auto-detect entities from the device. The exhaust-fan RPM sensor is named `extract` (not `exhaust`), so set `fan_speed_exhaust: sensor.pluggeasy_rpm_extract_motor` explicitly in the card config; everything else auto-detects.

## What changed in 0.3.3

- **`select.py`** (new) — `PluggeasyVentilationModeSelect` entity replaces the fan. Controls `parameters.selected_airflow` (the setpoint enum). Supports optimistic updates: state updates immediately on selection, then clears on the next coordinator refresh so the live value wins.
- **`fan.py`** (deleted) — removed; `fan.pluggeasy` entity no longer exists. **Breaking**: update dashboards and automations to use `select.pluggeasy_ventilation_mode`.
- **`__init__.py`** — `Platform.FAN` replaced with `Platform.SELECT` in `PLATFORMS`.
- **`translations/en.json`** — `fan` block removed; `select.ventilation_mode` block added with state labels for all five options.
- **`manifest.json`** — `requirements` pinned to `modbus-connection[tmodbus]>=3.9,<4`; version bumped to `0.3.3`.
- **Unchanged**: `sensor.pluggeasy_actual_working_mode` still shows the real running state from the device.

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
