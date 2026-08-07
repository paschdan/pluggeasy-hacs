# Pluggeasy — Home Assistant Custom Integration

[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)
[![Lint](https://github.com/paschdan/pluggeasy-hacs/actions/workflows/lint.yml/badge.svg)](https://github.com/paschdan/pluggeasy-hacs/actions/workflows/lint.yml)
[![Validate](https://github.com/paschdan/pluggeasy-hacs/actions/workflows/validate.yml/badge.svg)](https://github.com/paschdan/pluggeasy-hacs/actions/workflows/validate.yml)

A Home Assistant custom integration for the **Pluggeasy** (Pluggit) heat-recovery ventilation unit, distributed via [HACS](https://hacs.xyz).

## What?

This repository contains the HACS-distributable custom integration for the Pluggeasy ventilation unit. It communicates over Modbus TCP using its own connection (no shared `modbus_connection` component required), making it fully self-contained and installable today.

File | Purpose
-- | --
`.devcontainer.json` | Development/testing with Visual Studio Code devcontainer
`.github/renovate.json` | Dependency update configuration for Renovate
`.github/ISSUE_TEMPLATE/*.yml` | Issue tracker templates
`custom_components/pluggeasy/` | Integration files
`custom_components/pluggeasy/vendor/` | Vendored `pluggeasy_modbus` device library (v0.2.0)
`scripts/vendor.sh` | Refresh the vendored library from the upstream repo
`CONTRIBUTING.md` | Contribution guidelines
`LICENSE` | MIT License
`README.md` | This file
`requirements_dev.txt` | Python packages for development/testing
`requirements_lint.txt` | Python packages for linting (CI)
`requirements_common.txt` | Common packages (pip upgrade)

## Data provided

| Platform | Count | Description |
| :--- | :---: | :--- |
| `climate` | 1 | `climate.pluggeasy_climate` — HVACMode.FAN_ONLY; fan modes: off / auto / low / medium / high (mapped to selected_airflow); read-only supply-air temperature shown as the climate temperature (no writable setpoint). Coexists with `select.pluggeasy_ventilation_mode`. |
| `binary_sensor` | 14 | Alarms, sensor faults, fan faults, bypass/boost status; **new in 0.4.0**: Bypass Valve (open/closed), Summer Mode (mirrors the summer switch), Preheat (defrost pre-heater active) |
| `sensor` | 26 | Air temperatures, humidity, motor voltages/RPM, VOC, enum status sensors (actual working mode, defrost status, communication error, bypass damper position), parameters; **new in 0.4.0**: Supply Air Level (%), Return Air Level (%) |
| `switch` | 5 | Bypass, summer mode, boost, snooze, allow automatic bypass |
| `select` | 1 | Ventilation speed setpoint (`select.pluggeasy_ventilation_mode`): low / medium / nominal / auto / snooze |
| `button` | 1 | Reset filter alarm |

## Installation

1. Install [HACS](https://hacs.xyz) in your Home Assistant instance.
2. Add this repository as a custom repository in HACS (category: Integration).
3. Install **Pluggeasy** from HACS.
4. Restart Home Assistant.
5. Add the integration via **Settings → Devices & Services → Add Integration → Pluggeasy**.

## What's new in 0.4.0

### Climate entity + lovelace-comfoair card support

Version 0.4.0 adds a `climate` entity and a set of new sensors/binary_sensors that enable the [TimWeyand/lovelace-comfoair](https://github.com/TimWeyand/lovelace-comfoair) card to auto-detect entities from the Pluggeasy device.

#### New: `climate.pluggeasy_climate`

- **HVAC mode**: `FAN_ONLY` (a ventilation unit only ventilates — no heating/cooling setpoint).
- **Fan modes**: `off` / `auto` / `low` / `medium` / `high` — mapped to `selected_airflow` (off → Snooze, auto → Auto, low → Low, medium → Medium, high → Nominal). Setting a fan mode writes the airflow setpoint; the ventilation-mode select (`select.pluggeasy_ventilation_mode`) continues to work alongside it.
- **Temperature**: the read-only supply-air temperature is exposed as the climate `temperature` attribute (the big center number in the card). There is no writable setpoint — `set_temperature` is a no-op.

#### New sensors (0.4.0)

| Entity | Unit | Description |
| :--- | :---: | :--- |
| `sensor.pluggeasy_supply_air_level` | % | Supply fan stage approximation from `actual_working_mode`: snooze → 0 %, low → 33 %, medium → 66 %, high / boost / auto-variants → 66–100 % |
| `sensor.pluggeasy_return_air_level` | % | Return fan stage approximation (same mapping) |

#### New binary sensors (0.4.0)

| Entity | Description |
| :--- | :--- |
| `binary_sensor.pluggeasy_bypass_valve` | `on` when the bypass damper position is `open` |
| `binary_sensor.pluggeasy_summer_mode` | `on` when summer mode is active (mirrors `switch.pluggeasy_summer_mode`) |
| `binary_sensor.pluggeasy_preheat` | `on` when the defrost pre-heater is active |

#### lovelace-comfoair card setup

Install [TimWeyand/lovelace-comfoair](https://github.com/TimWeyand/lovelace-comfoair) via HACS (Frontend / Dashboard category), then add a card:

```yaml
type: custom:comfoair-card
entity: climate.pluggeasy_climate
fan_speed_exhaust: sensor.pluggeasy_rpm_extract_motor
```

> **Note**: the exhaust-fan RPM sensor is named `extract` (not `exhaust`) in this integration, so `fan_speed_exhaust` must be set explicitly. All other entities are auto-detected from the device by the card.

## Breaking changes in 0.3.3

### Ventilation speed is now a Select entity

The `fan.pluggeasy` entity has been **removed**. Ventilation speed is now controlled via a **Select** entity:

- **New entity**: `select.pluggeasy_ventilation_mode` — options: low / medium / nominal / auto / snooze
- **Removed entity**: `fan.pluggeasy` (breaking: update any dashboards or automations that reference `fan.pluggeasy*`)
- **Unchanged**: `sensor.pluggeasy_actual_working_mode` still shows the real running state from the device
- **Optimistic updates**: selecting an option updates the UI immediately; the coordinator refresh confirms the live value
- **Library pin**: `modbus-connection[tmodbus]` is now pinned to `>=3.9,<4`

## Breaking changes in 0.3.0

### Connection-type selector

Version 0.3.0 adds a **connection-type / framer selector** to the config flow. When adding a new entry you now choose between:

| Transport | Framer | Description |
| :--- | :--- | :--- |
| TCP | **Socket** *(default)* | Native Modbus TCP — matches a classic `modbus: type: tcp` YAML config. **Use this if your device connects directly over TCP.** |
| TCP | RTU | RTU-over-TCP (legacy gateway mode) |
| TCP | ASCII | ASCII-over-TCP |
| Serial | RTU *(default)* | RS-485 serial, RTU framing |
| Serial | ASCII | RS-485 serial, ASCII framing |

**Serial defaults** (from the Pluggeasy datasheet): 19200 baud, 8 data bits, EVEN parity, 1 stop bit.

**Existing entries keep working** — entries created with v0.2.0 (which lacked a connection-type field) are treated as TCP + Socket on load. This is a safe migration: the old hardcoded framer was `rtu`, but the only reported issue was "cannot connect" caused by that mismatch; Socket is the correct default for native TCP devices.

> **"Cannot connect" fix**: If you were unable to add the integration because of a connection error, choose **TCP → Socket** (the new default). This matches native Modbus TCP, the same protocol used by `modbus: type: tcp` in classic HA YAML.

## Breaking changes in 0.2.0

> **Users upgrading from 0.1.0 must update any automations referencing the old entity IDs.**

| Change | Old entity_id suffix | New entity_id suffix / replacement |
| :--- | :--- | :--- |
| Boost binary sensor renamed + inverted | `boost_mode_active` | `boost_active` (value now correct: `on` = boost running) |
| Speed control replaced by fan entity | `selected_airflow` sensor | `fan.pluggeasy` (preset modes) |
| Working mode switch removed | `working_mode` switch | Folded into fan entity (Auto preset) |
| Filter reset switch replaced by button | `reset_filter_alarm` switch | `button.pluggeasy_reset_filter_alarm` |

**Unchanged switches**: `manual_bypass`, `allow_automatic_bypass`, `summer_mode`, `manual_boost`, `snooze_mode`.

## Development

Open in Visual Studio Code devcontainer (recommended):

```bash
scripts/setup   # install dependencies
scripts/develop # start Home Assistant with the integration loaded
scripts/lint    # run ruff format + check
```

To refresh the vendored device library after upstream changes:

```bash
scripts/vendor.sh
```

## Device library

The `pluggeasy_modbus` device library (v0.2.0) is vendored under `custom_components/pluggeasy/vendor/`. See [paschdan/pluggeasy-modbus](https://github.com/paschdan/pluggeasy-modbus) for the upstream source.
