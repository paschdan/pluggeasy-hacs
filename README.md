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
| `binary_sensor` | 11 | Alarms, sensor faults, fan faults, bypass/boost status |
| `sensor` | 24 | Air temperatures, humidity, motor voltages/RPM, VOC, enum status sensors (actual working mode, defrost status, communication error, bypass damper position), parameters |
| `switch` | 5 | Bypass, summer mode, boost, snooze, allow automatic bypass |
| `fan` | 1 | Ventilation speed (presets: low / medium / nominal / auto / snooze) |
| `button` | 1 | Reset filter alarm |

## Installation

1. Install [HACS](https://hacs.xyz) in your Home Assistant instance.
2. Add this repository as a custom repository in HACS (category: Integration).
3. Install **Pluggeasy** from HACS.
4. Restart Home Assistant.
5. Add the integration via **Settings → Devices & Services → Add Integration → Pluggeasy**.

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
