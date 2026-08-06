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
| This HACS integration | `0.2.0` | `custom_components/pluggeasy/manifest.json` `version` field. |
| Vendored `pluggeasy_modbus` | `0.2.0` | Copied from `pluggeasy-modbus` `0.2.0` release; lives at `custom_components/pluggeasy/vendor/pluggeasy_modbus/`. Refresh with `scripts/vendor.sh`. |
| `modbus-connection[tmodbus]` | `>=3.6` | Listed in `manifest.json` `requirements`; installed by HA at runtime. |
| Minimum Home Assistant | `2026.6.4` | Declared in `hacs.json`. |

## Architecture note

This integration uses the **own-connection** model: the config flow asks for `host`, `port`, and `unit_id` and creates a `ModbusConnection(ModbusTcpParams(...))` directly. This makes it fully self-contained — no shared `modbus_connection` HA component is required, so it works today without unreleased HA core components.

The `pluggeasy_modbus` device library is **vendored** (not listed in `requirements`) so it is always available offline. Only `modbus-connection[tmodbus]` (the transport layer) is a pip requirement.

For the HA core integration that uses the shared `modbus_connection` component, see [`pluggeasy-core`](https://github.com/paschdan/pluggeasy-core).

## What changed in 0.2.0

- **`fan.py`** (new) — `PluggeasyFan` entity with preset modes `low`, `medium`, `nominal`, `auto`, `snooze`. `turn_on` defaults to `nominal`; `turn_off` sets `snooze`. Writes `selected_airflow` holding register via `async_set_airflow()`.
- **`button.py`** (new) — `PluggeasyButton` entity (category: config) for filter alarm reset. Calls `async_reset_filter_alarm()`.
- **`sensor.py`** — `actual_working_mode`, `defrost_status`, `communication_error`, `bypass_damper_position` converted to `SensorDeviceClass.ENUM` sensors with human-readable state names. `selected_airflow` sensor removed (now fan entity). Total: 24 sensors (was 25).
- **`switch.py`** — `working_mode` coil switch and `reset_filter_alarm` switch removed. Total: 5 switches (was 7).
- **`binary_sensor.py`** — `boost_mode_active` renamed to `boost_active`; reads the corrected `status.boost_active` property (inverted).
- **`__init__.py`** — `Platform.FAN` and `Platform.BUTTON` added.
- **`translations/en.json`** — fan/button names and enum state translations added.
- **Vendored library** — updated to `pluggeasy_modbus` 0.2.0 (enums, writable airflow, boost inversion fix).
