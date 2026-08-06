"""Custom types for the Pluggeasy integration."""

# Copyright 2024 Pluggeasy contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

    from .coordinator import PluggeasyCoordinator

type PluggeasyConfigEntry = ConfigEntry[PluggeasyData]


@dataclass
class PluggeasyData:
    """Runtime data stored on the config entry."""

    coordinator: PluggeasyCoordinator
