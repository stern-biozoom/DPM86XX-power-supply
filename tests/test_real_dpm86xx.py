import os
import time
from unittest import TestCase

from dpm86xx.dpm86xx import DPM86XX


class TestRealDPM86XX(TestCase):
    def setUp(self):
        # Initialize the DPM86XX instance with the test port from environment variables
        # The environment variable "DPM_TEST_PORT" must be set to the device's port,
        # e.g., "COM4" (Windows), "/dev/ttyUSB0" (Linux).
        self.dpm = DPM86XX(os.environ['DPM_TEST_PORT'])

    def tearDown(self):
        # Reset the device to a known state of 5.0 volts and 100 milliamperes after each test
        self.dpm.set_voltage_and_current(5.0, 100)
        # Ensure the device's output is turned off after each test
        self.dpm.set_output_status(0)

    def test_read_temperature(self):
        # Test to read and print the temperature from the device
        print(f'Temp: {self.dpm.get_temperature()}')

    def test_read_actual_voltage(self):
        # Test to read the actual voltage from the device after enabling the output
        self.dpm.set_output_status(1)
        time.sleep(0.5)  # Wait for the device to stabilize
        self.dpm.get_actual_voltage_in_centivolts()
        self.dpm.set_output_status(0)  # Ensure output is disabled after the test

    def test_output_status_commands(self):
        # Test to toggle the output status and verify it
        self.dpm.set_output_status(1)
        print('Output:', 'enabled' if self.dpm.get_output_status() else 'disabled')
        time.sleep(0.5)
        self.dpm.set_output_status(0)
        print('Output:', 'enabled' if self.dpm.get_output_status() else 'disabled')

    def test_set_voltage(self):
        # Test to sequentially set different voltage levels
        self.dpm.set_output_status(0)  # Ensure output is off before setting voltages
        for voltage in range(0, 501, 100):
            self.dpm.set_voltage_in_centivolts(voltage)
            time.sleep(0.3)  # Short delay to observe changes

    def test_set_current(self):
        # Test to sequentially set different current levels in milliamperes and amperes
        self.dpm.set_output_status(0)  # Start with the output disabled
        for current in range(0, 501, 100):
            self.dpm.set_current_in_milliampere(current)
            time.sleep(0.3)
        for current in (0.12, 0.22, 0.42, 1.0, 0.1):
            self.dpm.set_current(current)
            time.sleep(0.3)

    def test_set_voltage_and_current(self):
        # Test to set combinations of voltage and current
        self.dpm.set_output_status(0)  # Disable output before setting
        for voltage in (0.1, 0.2, 0.4, 3.0, 5.0):
            for current in (0.12, 0.22, 0.42, 1.0, 0.1):
                self.dpm.set_voltage_and_current(voltage, current)
                time.sleep(0.3)  # Allow time for the device to apply the settings

    def test_read_actual_current(self):
        # Test to read and print the actual current output from the device
        self.dpm.set_output_status(1)
        time.sleep(0.3)  # Wait briefly after enabling the output
        print(f'Current: {self.dpm.get_actual_current_in_milliamperes()}mA')
        self.dpm.set_output_status(0)  # Disable output after reading

    def test_cc_cv(self):
        # Test to determine and print whether the device is in CC or CV mode
        self.dpm.set_output_status(1)
        time.sleep(0.3)  # Allow some time for the mode to be determined
        print('In', 'CV' if self.dpm.is_in_cv_mode() else 'CC', 'mode.')
        time.sleep(0.3)  # Brief pause before turning off the output
        self.dpm.set_output_status(0)
