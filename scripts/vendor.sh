#!/usr/bin/env bash
# vendor.sh — refresh the vendored pluggeasy_modbus library
#
# Usage: scripts/vendor.sh
#
# This script copies the pluggeasy_modbus package from the sibling
# pluggeasy-modbus repository into custom_components/pluggeasy/vendor/.
# Run this whenever the upstream library is updated.
#
# Source:  ../../pluggeasy-modbus/src/pluggeasy_modbus/
# Target:  custom_components/pluggeasy/vendor/pluggeasy_modbus/

set -e

cd "$(dirname "$0")/.."

SRC="$(cd "$(dirname "$0")/../../pluggeasy-modbus/src/pluggeasy_modbus" && pwd)"
DST="${PWD}/custom_components/pluggeasy/vendor/pluggeasy_modbus"

if [[ ! -d "${SRC}" ]]; then
    echo "ERROR: source not found at ${SRC}" >&2
    exit 1
fi

echo "Vendoring ${SRC} → ${DST}"
rm -rf "${DST}"
mkdir -p "$(dirname "${DST}")"
cp -r "${SRC}" "${DST}"
echo "Done. Vendored pluggeasy_modbus refreshed."
