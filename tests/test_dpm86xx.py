import random
from unittest import TestCase

from dpm86xx.dpm86xx import DPM86XX


class TestDPM86XX(TestCase):
    def setUp(self):
        self.dpm = DPM86XX()

    def test_make_command(self):
        # Test all combination of:
        # - all valid addresses
        # - both modes
        # - all valid function members
        # - and 100 random values in the valid range
        for address in range(1, 100):
            for function in ['r', 'w']:
                for function_member in range(0, 100):
                    for operand in [random.randint(0,65536) for _ in range(100)]:
                        self.assertRegex(
                            self.dpm.make_command(address, function, function_member, operand),
                            # Assert format of regular command
                            ':\\d\\d[rw]\\d\\d=\\d{1,5},\r\n'.encode()
                        )
        # Test second operand format
        self.assertRegex(
            self.dpm.make_command(1, 'r', 1, 12345,12345),
            ':\\d\\d[rw]\\d\\d=\\d{1,5},\\d{1,5},\r\n'.encode()
        )
        with self.assertRaises(ValueError):
            # Address out of range
            self.dpm.make_command(0, 'w',1,1234)
        with self.assertRaises(ValueError):
            # function member out of range
            self.dpm.make_command(0, 'w',100,1234)
        with self.assertRaises(ValueError):
            # operand out of range
            self.dpm.make_command(0, 'w',100,123456)

    def test_make_write_voltage_command(self):
        self.assertEqual(self.dpm.make_write_voltage_command(1, 1234), b':01w10=1234,\r\n')
        self.assertEqual(self.dpm.make_write_voltage_command(1, 12.34), b':01w10=1234,\r\n')
        with self.assertRaises(ValueError):
            # Voltage out of range
            self.dpm.make_write_voltage_command(1, -1234)
        with self.assertRaises(ValueError):
            # Voltage out of range
            self.dpm.make_write_voltage_command(1, 70.3)

    def test_make_write_current_command(self):
        self.assertEqual(self.dpm.make_write_current_command(1, 12345), b':01w11=12345,\r\n')
        self.assertEqual(self.dpm.make_write_current_command(1, 12.345), b':01w11=12345,\r\n')
        with self.assertRaises(ValueError):
            # Current out of range
            self.dpm.make_write_current_command(1, -1)
        with self.assertRaises(ValueError):
            # Current out of range
            self.dpm.make_write_current_command(1, 25000)

    def test_make_write_output_status_command(self):
        self.assertEqual(self.dpm.make_write_output_status_command(1, 1), b':01w12=1,\r\n')
        self.assertEqual(self.dpm.make_write_output_status_command(1, True), b':01w12=1,\r\n')
        self.assertEqual(self.dpm.make_write_output_status_command(1, 0), b':01w12=0,\r\n')
        self.assertEqual(self.dpm.make_write_output_status_command(1, False), b':01w12=0,\r\n')

    def test_make_write_voltage_and_current_command(self):
        self.assertEqual(self.dpm.make_write_voltage_and_current_command(1, 1234, 12345),
                         b':01w20=1234,12345,\r\n')
        with self.assertRaises(ValueError):
            # Voltage out of range
            self.dpm.make_write_voltage_and_current_command(1, -1, 1)
        with self.assertRaises(ValueError):
            # Current out of range
            self.dpm.make_write_voltage_and_current_command(1, 1, -1)
