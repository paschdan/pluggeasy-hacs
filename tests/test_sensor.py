"""Regression tests for VOC units on old and new Home Assistant versions."""

from enum import StrEnum
from importlib import reload
from types import ModuleType
from unittest import TestCase
from unittest.mock import patch

from homeassistant import const
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass

from custom_components.pluggeasy import sensor


class TestUnitOfRatio(StrEnum):
    """Stand-in for the enum introduced after the minimum HA version."""

    PARTS_PER_MILLION = "ppm"


class TestVocUnits(TestCase):
    """Ensure the deprecated constant is never needed to import the platform."""

    def tearDown(self) -> None:
        """Restore the platform's real Home Assistant imports."""
        reload(sensor)

    def test_ratio_enum(self) -> None:
        """Use the new enum when available without changing sensor metadata."""
        fake_const = ModuleType("homeassistant.const")
        fake_const.__dict__.update(vars(const))
        fake_const.UnitOfRatio = TestUnitOfRatio
        fake_const.__dict__.pop("CONCENTRATION_PARTS_PER_MILLION", None)
        with (
            patch.dict("sys.modules", {"homeassistant.const": fake_const}),
            self.assertNoLogs("homeassistant.const", level="WARNING"),
        ):
            reload(sensor)
            description = next(
                d for d in sensor.DESCRIPTIONS if d.key == "measurements_voc"
            )
            self.assertIs(
                description.native_unit_of_measurement,
                TestUnitOfRatio.PARTS_PER_MILLION,
            )
            self.assertEqual(
                description.device_class,
                SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS,
            )
            self.assertEqual(description.state_class, SensorStateClass.MEASUREMENT)
            self.assertEqual(description.component, "measurements")
            self.assertEqual(description.attribute, "voc")

    def test_without_ratio_enum(self) -> None:
        """Old HA uses the same unit string without the deprecated constant."""
        fake_const = ModuleType("homeassistant.const")
        fake_const.__dict__.update(vars(const))
        fake_const.__dict__.pop("UnitOfRatio", None)
        fake_const.__dict__.pop("CONCENTRATION_PARTS_PER_MILLION", None)
        with (
            patch.dict("sys.modules", {"homeassistant.const": fake_const}),
            self.assertNoLogs("homeassistant.const", level="WARNING"),
        ):
            reload(sensor)
            description = next(
                d for d in sensor.DESCRIPTIONS if d.key == "measurements_voc"
            )
            self.assertEqual(description.native_unit_of_measurement, "ppm")
