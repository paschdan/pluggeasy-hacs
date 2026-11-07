"""Exercise the device library and pymodbus backend without a live device."""

import json
import warnings
from functools import partial
from pathlib import Path
from unittest import IsolatedAsyncioTestCase, TestCase
from unittest.mock import AsyncMock, Mock, patch

from modbus_connection import ModbusSerialParams, ModbusTcpParams
from modbus_connection.pymodbus import ModbusConnection
from pluggeasy_modbus import ActualWorkingMode, Pluggeasy, SelectedAirflow

from custom_components.pluggeasy._params import build_params
from custom_components.pluggeasy.config_flow import PluggeasyFlowHandler

ROOT = Path(__file__).resolve().parents[1]


class TestModbusParameters(TestCase):
    """Keep configured transports and dependency declarations compatible."""

    def test_legacy_tcp_entry(self) -> None:
        """Existing entries without a transport retain TCP/socket defaults."""
        with warnings.catch_warnings(action="error", category=DeprecationWarning):
            params = build_params({"host": "pluggeasy.invalid"})
        self.assertIsInstance(params, ModbusTcpParams)
        self.assertEqual(params.host, "pluggeasy.invalid")
        self.assertEqual(params.port, 8899)
        self.assertEqual(params.framer, "socket")

    def test_serial_entry(self) -> None:
        """The new dependency accepts the existing serial configuration."""
        params = build_params(
            {
                "connection_type": "serial",
                "device": "/dev/pluggeasy-test",
                "baudrate": "19200",
                "bytesize": "8",
                "parity": "E",
                "stopbits": "1",
                "framer": "rtu",
            }
        )
        self.assertIsInstance(params, ModbusSerialParams)
        self.assertEqual(params.device, "/dev/pluggeasy-test")
        self.assertEqual(params.baudrate, 19200)
        self.assertEqual(params.bytesize, 8)
        self.assertEqual(params.parity, "E")
        self.assertEqual(params.stopbits, 1)
        self.assertEqual(params.framer, "rtu")

    def test_tcp_gateway_framing(self) -> None:
        """Existing gateway framing still works, despite upstream deprecation."""
        for framer in ("rtu", "ascii"):
            with self.subTest(framer=framer), self.assertWarns(DeprecationWarning):
                params = build_params({"host": "pluggeasy.invalid", "framer": framer})
            self.assertEqual(params.framer, framer)

    def test_dependency_declarations_match(self) -> None:
        """Runtime, development and CI must test the same Modbus dependency."""
        manifest = json.loads(
            (ROOT / "custom_components/pluggeasy/manifest.json").read_text()
        )
        requirement = next(
            value
            for value in manifest["requirements"]
            if value.startswith("modbus-connection[")
        )
        self.assertEqual(requirement, "modbus-connection[pymodbus]>=4.12.7,<5")
        self.assertIn(requirement, (ROOT / "requirements_dev.txt").read_text())
        self.assertIn(requirement, (ROOT / ".github/workflows/tests.yml").read_text())


class TestModbusBackend(IsolatedAsyncioTestCase):
    """Run real connection, unit and device code with mocked wire responses."""

    async def asyncSetUp(self) -> None:
        """Replace only the pymodbus client; no sockets are opened."""
        self.holding = {132: 3}
        self.input = {90: 11, 61: 1574, 62: 1839}
        self.client = Mock()
        self.client.connected = True
        self.client.connect = AsyncMock(return_value=True)
        self.client.read_holding_registers = AsyncMock(
            side_effect=partial(self._register_response, self.holding)
        )
        self.client.read_input_registers = AsyncMock(
            side_effect=partial(self._register_response, self.input)
        )
        self.client.read_coils = AsyncMock(side_effect=self._bit_response)
        self.client.read_discrete_inputs = AsyncMock(side_effect=self._bit_response)
        success = Mock()
        success.isError.return_value = False
        self.client.write_register = AsyncMock(return_value=success)
        self.client.write_coil = AsyncMock(return_value=success)
        constructor = patch(
            "modbus_connection.pymodbus.AsyncModbusTcpClient",
            return_value=self.client,
        )
        self.constructor = constructor.start()
        self.addCleanup(constructor.stop)
        self.connection = ModbusConnection(
            build_params({"host": "pluggeasy.invalid"}), message_spacing=0.03
        )
        self.addAsyncCleanup(self.connection.close)
        self.device = Pluggeasy(self.connection.for_unit(1))

    def _register_response(
        self, store: dict[int, int], address: int, *, count: int, device_id: int
    ) -> Mock:
        self.assertEqual(device_id, 1)
        response = Mock()
        response.isError.return_value = False
        response.registers = [
            store.get(index, 0) for index in range(address, address + count)
        ]
        return response

    def _bit_response(self, _address: int, *, count: int, device_id: int) -> Mock:
        self.assertEqual(device_id, 1)
        response = Mock()
        response.isError.return_value = False
        response.bits = [False] * count
        return response

    async def test_pooled_update(self) -> None:
        """Decode all components through the actual pymodbus unit adapter."""
        await self.connection.connect()
        await self.device.async_update()
        self.assertEqual(self.device.parameters.selected_airflow, SelectedAirflow.AUTO)
        self.assertEqual(
            self.device.measurements.actual_working_mode, ActualWorkingMode.WEEKLY_3
        )
        self.assertEqual(self.device.measurements.rpm_supply_motor, 1839)
        self.assertEqual(self.device.measurements.rpm_extract_motor, 1574)
        self.assertEqual(self.device.effective_airflow_mode(), "auto")
        self.client.write_register.assert_not_called()
        self.client.write_coil.assert_not_called()

    async def test_unknown_airflow_remains_unknown(self) -> None:
        """The dependency update must not silently assign a meaning to value 6."""
        self.holding[132] = 6
        with self.assertLogs("modbus_connection.model.fields", level="WARNING") as logs:
            await self.device.async_update()
        self.assertIn("no mapping for value 6", "\n".join(logs.output))
        self.assertIsNone(self.device.parameters.selected_airflow)
        self.assertIsNone(self.device.effective_airflow_mode())
        self.assertEqual(
            self.device.measurements.actual_working_mode, ActualWorkingMode.WEEKLY_3
        )

    async def test_airflow_writes(self) -> None:
        """Known speeds and Snooze keep their documented register/coil writes."""
        for mode, value in (("low", 0), ("medium", 1), ("high", 2), ("auto", 3)):
            with self.subTest(mode=mode):
                await self.device.async_set_airflow_mode(mode)
                self.client.write_register.assert_awaited_with(132, value, device_id=1)
                self.client.write_coil.assert_awaited_with(17, False, device_id=1)  # noqa: FBT003
        self.client.write_register.reset_mock()
        await self.device.async_set_airflow_mode("off")
        self.client.write_register.assert_not_called()
        self.client.write_coil.assert_awaited_with(17, True, device_id=1)  # noqa: FBT003

    async def test_probe_closes_client(self) -> None:
        """The config-flow probe still connects, polls and closes its client."""
        flow = PluggeasyFlowHandler()
        await flow._async_probe({"host": "pluggeasy.invalid", "unit_id": 1})  # noqa: SLF001
        self.client.connect.assert_awaited_once()
        self.client.close.assert_called_once()
        self.client.read_holding_registers.assert_awaited()
        self.client.read_input_registers.assert_awaited()
