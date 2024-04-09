# -*- coding: utf-8 -*-
import serial
from typing import Union, Literal


class DPM86XX:
    def __init__(self, com_port=None, address=1, baud=9600):
        if com_port is not None:
            self._port = serial.Serial(com_port, baudrate=baud)
        self._address = address

    @staticmethod
    def make_command(address: int, function: Literal['r', 'w'], function_member: int, operand: int,
                     operand2: Union[int, None] = None) -> bytes:
        """
        Formats a command string for the Joy-IT programmable lab power supply DPM86XX series according
        to its communication protocol.

        Constructs a command to read from or write to the power supply, following the protocol
        specification provided in the Joy-IT DPM86XX series documentation.

        :param address: The device address (1 - 99).
        :param function: The command function, 'r' for read or 'w' for write.
        :param function_member: The function member (0 - 99) to be accessed by the command.
        :param operand: The primary operand for the command, in the range 0 - 65536.
        :param operand2: An optional second operand for the command, in the range 0 - 65536. Default is None.
        :return: The encoded command string ready to be sent over a serial connection.
        :rtype: bytes
        :raises ValueError: If any parameter is out of its valid range, or if `function` is not 'r' or 'w'.
        """

        # Create commands according to simple protocol description at
        # [link](https://joy-it.net/files/files/Produkte/JT-DPM8624/JT-DPM86XX_Communication_protocol_2023-01-05.pdf)
        # for Joy-IT programmable lab power supply DPM86XX series.

        if not 1 <= address <= 99:
            raise ValueError('Address must be in the range of 1 - 99.')
        if not 0 <= function_member <= 99:
            raise ValueError('Function member must be in the range of 0 - 99.')
        if not 0 <= operand <= 65536:
            raise ValueError('Operand must be in the range of 0 - 65536.')
        if operand2 is not None:
            if not 0 <= operand2 <= 65536:
                raise ValueError('2nd operand must be in the range of 0 - 65536.')
            operand = f'{operand},{operand2}'
        if function not in ['r', 'w']:
            raise ValueError('Function must be either \'r\' or \'w\'.')
        return f':{address:02d}{function}{function_member:02d}={operand},\r\n'.encode()

    @classmethod
    def make_write_voltage_command(cls, address: int, voltage: Union[float, int]) -> bytes:
        """
        Creates a command to set a specific voltage at a given address.

        This method formats a command to instruct a device to set a specified voltage. It accepts
        voltage values as either a float or an integer. For float values, it converts the voltage to
        an integer representation (multiplied by 100) to comply with the command protocol, which
        expects voltage in centivolts. The method ensures the voltage is within the acceptable range
        before creating the command.

        :param address: The device address where the voltage should be set.
        :type address: int
        :param voltage: The voltage value to set, which can be a float or an integer. Float values
                        represent volts, and integer values represent centivolts.
        :type voltage: Union[float, int]
        :return: A byte string representing the formatted command to write the voltage.
        :rtype: bytes
        :raises ValueError: If the voltage is outside the acceptable range of 0.00 to 60.00 V.
        """
        if type(voltage) is float:
            voltage = int(voltage * 100)
        if not 0 <= voltage <= 6000:
            raise ValueError('Voltage must be in the range of 0.00 to 60.00 V')
        return cls.make_command(address, 'w', 10, voltage)

    @classmethod
    def make_write_current_command(cls, address: int, current: Union[float, int]) -> bytes:
        """
        Creates a command to set a specific current at a given address.

        This method formats a command to instruct a device to set a specified current. It accepts
        current values as either a float or an integer. For float values, it converts the current to
        an integer representation (multiplied by 1000) to comply with the command protocol, which
        expects current in milliamperes. The method ensures the current is within the acceptable range
        before creating the command.

        :param address: The device address where the current should be set.
        :type address: int
        :param current: The current value to set, which can be a float or an integer. Float values
                        represent amperes, and integer values represent milliamperes.
        :type current: Union[float, int]
        :return: A byte string representing the formatted command to write the current.
        :rtype: bytes
        :raises ValueError: If the current is outside the acceptable range of 0.000 to 24.000 A.
        """
        if type(current) is float:
            current = int(current * 1000)
        if not 0 <= current <= 24000:
            raise ValueError('Current must be in the range of 0.000 to 24.000 A')
        return cls.make_command(address, 'w', 11, current)

    @classmethod
    def make_write_output_status_command(cls, address: int, status: Union[bool, int]) -> bytes:
        """
        Creates a command to enable or disable the output at a given address.

        This method formats a command to control the output status of a device, enabling or disabling
        it based on the provided status. It accepts the status as either a boolean or an integer (with
        0 representing disabled and any non-zero value representing enabled) and formats it into the
        appropriate command format.

        :param address: The device address where the output status should be set.
        :type address: int
        :param status: The desired output status, where True (or any non-zero integer) enables the output
                       and False (or 0) disables it.
        :type status: Union[bool, int]
        :return: A byte string representing the formatted command to set the output status.
        :rtype: bytes
        """
        if type(status) is int:
            status = not status == 0
        status = 1 if status else 0
        return cls.make_command(address, 'w', 12, status)

    @classmethod
    def make_write_voltage_and_current_command(cls, address: int, voltage: Union[float, int],
                                               current: Union[float, int]) -> bytes:
        """
        Creates a command to set both voltage and current at a given address.

        This method formats a command for setting both voltage and current simultaneously on a device.
        It handles voltage and current values provided as either floats or integers, converting them
        to their respective integer representations needed by the command protocol. The method ensures
        both voltage and current are within acceptable ranges before creating the command.

        :param address: The device address where the voltage and current should be set.
        :type address: int
        :param voltage: The voltage value to set, in volts (as a float) or centivolts (as an integer).
        :type voltage: Union[float, int]
        :param current: The current value to set, in amperes (as a float) or milliamperes (as an integer).
        :type current: Union[float, int]
        :return: A byte string representing the formatted command to set both voltage and current.
        :rtype: bytes
        :raises ValueError: If the voltage or current is outside their acceptable ranges.
        """
        if type(voltage) is float:
            voltage = int(voltage * 100)
        if not 0 <= voltage <= 6000:
            raise ValueError('Voltage must be in the range of 0.00 to 60.00 V')
        if type(current) is float:
            current = int(current * 1000)
        if not 0 <= current <= 24000:
            raise ValueError('Current must be in the range of 0.000 to 24.000 A')
        return cls.make_command(address, 'w', 20, voltage, current)

    @classmethod
    def make_read_maximum_output_voltage_command(cls, address: int) -> bytes:
        """
        Generates a command to read the maximum output voltage setting of the device.

        :param address: The address of the device.
        :type address: int
        :return: Encoded command to read the maximum output voltage.
        :rtype: bytes
        """
        return cls.make_command(address, 'r', 0, 0)

    @classmethod
    def make_read_maximum_output_current_command(cls, address: int) -> bytes:
        """
        Generates a command to read the maximum output current setting of the device.

        :param address: The address of the device.
        :type address: int
        :return: Encoded command to read the maximum output current.
        :rtype: bytes
        """
        return cls.make_command(address, 'r', 1, 0)

    @classmethod
    def make_read_voltage_setting_command(cls, address: int) -> bytes:
        """
        Generates a command to read the voltage setting of the device.

        :param address: The address of the device.
        :type address: int
        :return: Encoded command to read the voltage setting.
        :rtype: bytes
        """
        return cls.make_command(address, 'r', 10, 0)

    @classmethod
    def make_read_current_setting_command(cls, address: int) -> bytes:
        """
        Generates a command to read the current setting of the device.

        :param address: The address of the device.
        :type address: int
        :return: Encoded command to read the current setting.
        :rtype: bytes
        """
        return cls.make_command(address, 'r', 11, 0)

    @classmethod
    def make_read_output_status_command(cls, address: int) -> bytes:
        """
        Generates a command to read the output status of the device.

        :param address: The address of the device.
        :type address: int
        :return: Encoded command to read the output status (on/off).
        :rtype: bytes
        """
        return cls.make_command(address, 'r', 12, 0)

    @classmethod
    def make_read_actual_voltage_command(cls, address: int) -> bytes:
        """
        Generates a command to read the actual output voltage of the device.

        :param address: The address of the device.
        :type address: int
        :return: Encoded command to read the actual output voltage.
        :rtype: bytes
        """
        return cls.make_command(address, 'r', 30, 0)

    @classmethod
    def make_read_actual_current_command(cls, address: int) -> bytes:
        """
        Generates a command to read the actual output current of the device.

        :param address: The address of the device.
        :type address: int
        :return: Encoded command to read the actual output current.
        :rtype: bytes
        """
        return cls.make_command(address, 'r', 31, 0)

    @classmethod
    def make_read_cc_cv_status_command(cls, address: int) -> bytes:
        """
        Generates a command to read the CC (Constant Current) or CV (Constant Voltage) status of the device.

        :param address: The address of the device.
        :type address: int
        :return: Encoded command to read the CC/CV status.
        :rtype: bytes
        """
        return cls.make_command(address, 'r', 32, 0)

    @classmethod
    def make_read_temperature_command(cls, address: int) -> bytes:
        """
        Generates a command to read the internal temperature of the device at a specified address.

        :param address: The address of the device from which the temperature is to be read.
        :type address: int
        :return: A byte string representing the formatted command to read the device's internal temperature.
        :rtype: bytes
        """
        return cls.make_command(address, 'r', 33, 0)

