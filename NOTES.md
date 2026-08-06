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
| This HACS integration | `0.1.0` | `custom_components/pluggeasy/manifest.json` `version` field. |
| Vendored `pluggeasy_modbus` | `0.1.0` | Copied from `pluggeasy-modbus` `0.1.0` release; lives at `custom_components/pluggeasy/vendor/pluggeasy_modbus/`. Refresh with `scripts/vendor.sh`. |
| `modbus-connection[tmodbus]` | `>=3.6` | Listed in `manifest.json` `requirements`; installed by HA at runtime. |
| Minimum Home Assistant | `2026.6.4` | Declared in `hacs.json`. |

## Architecture note

This integration uses the **own-connection** model: the config flow asks for `host`, `port`, and `unit_id` and creates a `ModbusConnection(ModbusTcpParams(...))` directly. This makes it fully self-contained — no shared `modbus_connection` HA component is required, so it works today without unreleased HA core components.

The `pluggeasy_modbus` device library is **vendored** (not listed in `requirements`) so it is always available offline. Only `modbus-connection[tmodbus]` (the transport layer) is a pip requirement.

For the HA core integration that uses the shared `modbus_connection` component, see [`pluggeasy-core`](https://github.com/paschdan/pluggeasy-core).
