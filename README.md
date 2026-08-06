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
`custom_components/pluggeasy/vendor/` | Vendored `pluggeasy_modbus` device library
`scripts/vendor.sh` | Refresh the vendored library from the upstream repo
`CONTRIBUTING.md` | Contribution guidelines
`LICENSE` | MIT License
`README.md` | This file
`requirements_dev.txt` | Python packages for development/testing
`requirements_lint.txt` | Python packages for linting (CI)
`requirements_common.txt` | Common packages (pip upgrade)

## Data provided

- **11 binary sensors** — alarms, faults, bypass/boost status
- **25 sensors** — temperatures, humidity, motor voltages/RPM, VOC, working mode, parameters
- **7 switches** — filter reset, bypass, summer mode, boost, snooze, working mode

## Installation

1. Install [HACS](https://hacs.xyz) in your Home Assistant instance.
2. Add this repository as a custom repository in HACS (category: Integration).
3. Install **Pluggeasy** from HACS.
4. Restart Home Assistant.
5. Add the integration via **Settings → Devices & Services → Add Integration → Pluggeasy**.

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

The `pluggeasy_modbus` device library is vendored under `custom_components/pluggeasy/vendor/`. See [paschdan/pluggeasy-modbus](https://github.com/paschdan/pluggeasy-modbus) for the upstream source.
