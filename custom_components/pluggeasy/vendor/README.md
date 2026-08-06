# Vendored Libraries

## pluggeasy_modbus

- **Source**: https://github.com/paschdan/pluggeasy-modbus
- **Version**: 0.2.0 (enums.py + writable selected_airflow + boost_active inversion fix)
- **Vendored path**: `pluggeasy_modbus/`

### Provenance

This directory contains a verbatim copy of the `pluggeasy_modbus` package from
the [paschdan/pluggeasy-modbus](https://github.com/paschdan/pluggeasy-modbus)
repository (`src/pluggeasy_modbus/`).

The library is vendored here (rather than listed in `manifest.json` requirements)
because it is a pure-Python device model with no compiled dependencies, and
vendoring avoids requiring users to install a private/unreleased PyPI package.

The `modbus-connection[tmodbus]` transport dependency is **not** vendored — it
remains in `manifest.json` requirements and is installed by Home Assistant via pip.

### Regenerate

To refresh this vendored copy after upstream changes:

```bash
scripts/vendor.sh
```

The script copies `../../pluggeasy-modbus/src/pluggeasy_modbus/` into this
directory, replacing the existing copy.
