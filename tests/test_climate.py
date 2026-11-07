"""Regression tests for climate action when the airflow setpoint is unknown."""

from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock

from homeassistant.components.climate import FAN_OFF, HVACAction
from pluggeasy_modbus import ActualWorkingMode

from custom_components.pluggeasy.climate import PluggeasyClimate
from custom_components.pluggeasy.select import PluggeasyVentilationModeSelect


class TestPluggeasyClimate(TestCase):
    """Exercise entity properties without a live connection or Home Assistant."""

    def setUp(self) -> None:
        """Create a coordinator with an unmapped selected airflow."""
        self.device = Mock()
        self.device.effective_airflow_mode.return_value = None
        self.device.measurements = SimpleNamespace(actual_working_mode=None)
        self.coordinator = Mock(data=self.device)
        self.coordinator.config_entry.entry_id = "test_entry"
        self.entity = PluggeasyClimate(self.coordinator)

    def test_running_modes_with_unknown_setpoint(self) -> None:
        """All documented running modes report FAN, not OFF."""
        for mode in ActualWorkingMode:
            if mode == ActualWorkingMode.SNOOZE:
                continue
            with self.subTest(mode=mode):
                self.device.measurements.actual_working_mode = mode
                self.assertIsNone(self.entity.fan_mode)
                self.assertEqual(self.entity.hvac_action, HVACAction.FAN)

    def test_snooze_with_unknown_setpoint(self) -> None:
        """Actual Snooze still reports OFF."""
        self.device.measurements.actual_working_mode = ActualWorkingMode.SNOOZE
        self.assertEqual(self.entity.hvac_action, HVACAction.OFF)

    def test_unknown_working_mode_and_setpoint(self) -> None:
        """Missing decoded values must not imply the unit is off."""
        self.assertIsNone(self.entity.hvac_action)

    def test_unknown_setpoint_does_not_change_device(self) -> None:
        """Reading a weekly-mode unit must not guess a setpoint or write one."""
        self.device.measurements.actual_working_mode = ActualWorkingMode.WEEKLY_3
        select = PluggeasyVentilationModeSelect(self.coordinator)
        self.assertIsNone(select.current_option)
        self.assertIsNone(self.entity.fan_mode)
        self.assertEqual(self.entity.hvac_action, HVACAction.FAN)
        self.device.async_set_airflow_mode.assert_not_called()

    def test_unrecognized_working_mode(self) -> None:
        """An undocumented raw working-mode value must not imply FAN."""
        self.device.measurements.actual_working_mode = 99
        self.assertIsNone(self.entity.hvac_action)

    def test_missing_measurements(self) -> None:
        """Missing measurements and setpoint report an unknown action."""
        self.device.measurements = None
        self.assertIsNone(self.entity.hvac_action)

    def test_missing_coordinator_data(self) -> None:
        """No data reports unknown properties without raising."""
        self.coordinator.data = None
        self.assertIsNone(self.entity.fan_mode)
        self.assertIsNone(self.entity.hvac_action)

    def test_known_setpoint_fallback(self) -> None:
        """Known setpoints preserve the previous action when actual mode is absent."""
        for fan_mode, action in (
            ("off", HVACAction.OFF),
            ("low", HVACAction.FAN),
            ("medium", HVACAction.FAN),
            ("high", HVACAction.FAN),
            ("auto", HVACAction.FAN),
        ):
            with self.subTest(fan_mode=fan_mode):
                self.device.effective_airflow_mode.return_value = fan_mode
                self.assertEqual(self.entity.hvac_action, action)

    def test_actual_mode_overrides_optimistic_setpoint(self) -> None:
        """A requested stop must not hide the device's still-running action."""
        self.device.measurements.actual_working_mode = ActualWorkingMode.WEEKLY_3
        self.entity._optimistic = FAN_OFF  # noqa: SLF001
        self.assertEqual(self.entity.fan_mode, FAN_OFF)
        self.assertEqual(self.entity.hvac_action, HVACAction.FAN)

    def test_actual_snooze_overrides_running_setpoint(self) -> None:
        """A selected running speed does not override actual Snooze."""
        self.device.measurements.actual_working_mode = ActualWorkingMode.SNOOZE
        self.device.effective_airflow_mode.return_value = "low"
        self.assertEqual(self.entity.hvac_action, HVACAction.OFF)
