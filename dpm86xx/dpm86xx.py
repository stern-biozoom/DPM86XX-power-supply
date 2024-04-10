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

    def set_port(self, port: Union[str, serial.Serial], baud: int = 9600) -> None:
        """
        Configures the communication port for the device, either by using an existing serial port object or by creating
        a new one.

        This method allows the user to set the communication port with the device by specifying either a serial port
        object directly or a port name from which a new serial port object will be created with the specified baud rate.
        If a serial port object is provided, it is used directly; otherwise, a new serial port object is instantiated
        with the provided port name and baud rate.

        :param port: The communication port to use. Can be a port name (str) or an existing serial.Serial object.
        :type port: Union[str, serial.Serial]
        :param baud: The baud rate for the serial connection, defaults to 9600 if not specified. Used only when creating
                     a new serial port object.
        :type baud: int
        """
        if type(port) is serial.Serial:
            self._port = port
            return
        self._port = serial.Serial(port, baud)

    def get_temperature(self) -> int:
        """
        Reads the temperature from the device.

        Sends a command to the device to read its internal temperature and parses the response to extract
        the temperature value. Assumes the device returns the temperature in a specific format and extracts
        the relevant part of the response to obtain the temperature.

        :return: The temperature read from the device.
        :rtype: int
        :raises AssertionError: If the communication port has not been configured.
        :raises IOError: If the response from the device is shorter than expected, indicating incomplete or corrupted
                data.
        :raises ValueError: If converting the temperature portion of the response to an integer fails, indicating an
                invalid format.
        """
        assert self._port is not None
        command = self.make_read_temperature_command(self._address)
        self._port.write(command)
        response = self._port.read_until(b'\r\n')
        if len(response) < 11:
            raise IOError(f'Response is too short: {response}')
        result = int(response[7:-3])  # may raise ValueError
        return result

    def set_voltage_in_centivolts(self, voltage_in_centivolts: int) -> bool:
        """
        Sends a command to set the device's voltage level, specified in centivolts.

        Before sending the command, it checks that the communication port is configured. The acknowledgment
        from the device, indicated by b':01ok\r\n', means the command was received in the correct format.
        It's important to note that this response does not confirm the successful execution of the command,
        but rather the correct reception.

        :param voltage_in_centivolts: The desired voltage level to set on the device, specified in centivolts.
        :type voltage_in_centivolts: int
        :return: True if the device acknowledges receipt of the command with b':01ok\r\n', indicating
                 the command was received. This does not necessarily mean the command was executed successfully.
        :raises AssertionError: If the communication port has not been configured.
        """
        assert self._port is not None
        command = self.make_write_voltage_command(self._address, voltage_in_centivolts)
        self._port.write(command)
        response = self._port.read_until(b'\r\n')
        # The device always responses with b':01ok\r\n'. This does only mean the device received
        # a command-like byte string, disregarding its actual content. Thus, we cannot tell if the
        # command was successful, but only if the command was received.
        return response == b':01ok\r\n'

    def set_voltage(self, voltage: float) -> bool:
        """
        Attempts to set the device's voltage level, specified in volts.

        Validates the input voltage to ensure it is a float, converting if necessary, before generating
        and sending the command to the device. Ensures that the communication port is available before
        proceeding. The device's response, b':01ok\r\n', signifies that the command was received. It's
        important to note that this response does not indicate the successful execution of the command,
        but rather the correct format of the received command.

        :param voltage: The desired voltage level to set on the device, in volts.
        :type voltage: float
        :return: True if the device acknowledges receipt of the command with b':01ok\r\n', indicating
                 the command was received in the correct format but not necessarily executed as intended.
        :rtype: bool
        :raises AssertionError: If the communication port has not been configured.
        :raises ValueError: If the input voltage cannot be converted to a float, indicating an invalid
                 input type.
        """
        assert self._port is not None
        if type(voltage) is not float:
            voltage = float(voltage)  # may raise ValueError
        command = self.make_write_voltage_command(self._address, voltage)
        self._port.write(command)
        response = self._port.read_until(b'\r\n')
        # The device always responses with b':01ok\r\n'. This does only mean the device received
        # a command-like byte string, disregarding its actual content. Thus, we cannot tell if the
        # command was successful, but only if the command was received.
        return response == b':01ok\r\n'

    def get_actual_voltage_in_centivolts(self) -> int:
        """
        Reads the actual voltage level from the device, returning the value in centivolts.

        This method sends a command to the device to read the current actual voltage. It ensures that
        the communication port is configured before sending the command. The method parses the device's
        response, extracting the voltage value in centivolts.

        :return: The actual voltage level read from the device, in centivolts.
        :rtype: int
        :raises AssertionError: If the communication port has not been configured.
        :raises IOError: If the response from the device is shorter than expected, suggesting incomplete
                 or corrupted data.
        :raises ValueError: If converting the response to an integer fails, indicating an invalid response format.
        """
        assert self._port is not None
        command = self.make_read_actual_voltage_command(self._address)
        self._port.write(command)
        response = self._port.read_until(b'\r\n')
        if len(response) < 11:
            raise IOError(f'Response is too short: {response}')
        result = int(response[7:-3])  # may raise ValueError
        return result

    def get_actual_voltage(self) -> float:
        """
        Reads the actual voltage level from the device, converting the result to volts.

        This method leverages `read_actual_voltage_in_centivolts` to fetch the actual voltage in centivolts
        and then converts that value to volts for more convenient interpretation.

        :return: The actual voltage level read from the device, in volts.
        :rtype: float
        :raises AssertionError: If the communication port has not been configured.
        :raises IOError: If the response from the device is shorter than expected, suggesting incomplete
                 or corrupted data.
        :raises ValueError: If converting the response to an integer fails, indicating an invalid response format.
        """
        return self.get_actual_voltage_in_centivolts() / 100.0

    def set_output_status(self, status) -> bool:
        """
        Sends a command to the device to set the output status (on/off).

        Ensures the communication port is configured before sending the command. The device's acknowledgment,
        b':01ok\r\n', only indicates that the command was received in the correct format and does not guarantee
        the command's successful execution.

        :param status: The desired output status; True to enable or False to disable the output.
        :return: True if the device acknowledges receipt of the command with b':01ok\r\n', indicating
                 the command was received. It does not ensure the command was executed as intended.
        :raises AssertionError: If the communication port has not been configured.
        """
        assert self._port is not None
        command = self.make_write_output_status_command(self._address, status)
        self._port.write(command)
        response = self._port.read_until(b'\r\n')
        # The device always responses with b':01ok\r\n'. This does only mean the device received
        # a command-like byte string, disregarding its actual content. Thus, we cannot tell if the
        # command was successful, but only if the command was received.
        return response == b':01ok\r\n'

    def get_output_status(self) -> bool:
        """
        Queries the device for its output status (on/off).

        Sends a command to the device to check whether its output is currently enabled or disabled.
        Validates the communication port's configuration before proceeding. The method parses the device's
        response to determine the output status.

        :return: True if the output is enabled (on), False if it is disabled (off).
        :rtype: bool
        :raises AssertionError: If the communication port has not been configured.
        :raises IOError: If the device's response is shorter than expected, suggesting that the data received is
                incomplete or corrupted.
        :raises ValueError: If converting the relevant portion of the response to an integer is unsuccessful,
                indicating an invalid response format.
        """
        assert self._port is not None
        command = self.make_read_output_status_command(self._address)
        self._port.write(command)
        response = self._port.read_until(b'\r\n')
        if len(response) < 11:
            raise IOError(f'Response is too short: {response}')
        result = int(response[7:-3])  # may raise ValueError
        return result == 1

    def set_current_in_milliampere(self, current_in_milliampere: int) -> bool:
        """
        Sends a command to set the device's current level, specified in milliamperes.

        Before issuing the command, it verifies that the communication port is properly configured.
        The device's acknowledgment, indicated by b':01ok\r\n', confirms the receipt of the command in
        the correct format. This acknowledgment does not, however, verify the successful execution of the
        command, merely the reception of a command structured correctly.

        :param current_in_milliampere: The desired current level to set on the device, specified in milliamperes.
        :type current_in_milliampere: int
        :return: True if the device acknowledges receipt of the command with b':01ok\r\n', signifying
                 that the command was received. It does not ascertain the command's successful execution.
        :raises AssertionError: If the communication port has not been configured.
        """
        assert self._port is not None
        command = self.make_write_current_command(self._address, current_in_milliampere)
        self._port.write(command)
        response = self._port.read_until(b'\r\n')
        # The device always responses with b':01ok\r\n'. This does only mean the device received
        # a command-like byte string, disregarding its actual content. Thus, we cannot tell if the
        # command was successful, but only if the command was received.
        return response == b':01ok\r\n'

    def set_current(self, current: float) -> bool:
        """
        Sets the device's current level, converting the given value from amperes to milliamperes before sending the
        command.

        Converts the specified current from amperes to milliamperes by multiplying by 1000. This conversion
        may raise a ValueError if the provided current cannot be converted to an integer.
        The method then delegates the command sending to `set_current_in_milliampere`, which sends the
        appropriate command to the device.

        :param current: The desired current level to set on the device, specified in amperes.
        :type current: float
        :return: True if the device acknowledges receipt of the command with b':01ok\r\n', indicating
                 the command was received. This does not guarantee the command's successful execution.
        :raises AssertionError: If the communication port has not been configured.
        :raises ValueError: If the current value cannot be converted to an integer.
        """
        current_in_milliampere = int(current * 1000)  # may raise ValueError
        return self.set_current_in_milliampere(current_in_milliampere)

    def set_voltage_and_current(self, voltage: Union[float, int], current: Union[float, int]) -> bool:
        """
        Sends a command to set both the voltage and current levels on the device.

        This method constructs and sends a command to simultaneously set the voltage and current levels of the device.
        It accommodates both float and integer inputs for voltage and current, with integers being treated as centivolts
        and milliamperes respectively. It's crucial to note that the device's acknowledgment (b':01ok\r\n') only
        confirms the receipt of a well-formed command, not the successful application of the settings.

        :param voltage: The voltage level to set, in volts if a float, or centivolts if an integer.
        :type voltage: Union[float, int]
        :param current: The current level to set, in amperes if a float, or milliamperes if an integer.
        :type current: Union[float, int]
        :return: True if the device acknowledges receipt of the command with b':01ok\r\n', indicating the command
                 was received in the correct format. This does not confirm the successful execution of the command.
        :raises AssertionError: If the communication port has not been configured.
        """
        assert self._port is not None
        # Beware: If voltage and current given as int, they will get converted in centivolts and milliamperes!
        command = self.make_write_voltage_and_current_command(self._address, voltage, current)
        self._port.write(command)
        response = self._port.read_until(b'\r\n')
        # The device always responses with b':01ok\r\n'. This does only mean the device received
        # a command-like byte string, disregarding its actual content. Thus, we cannot tell if the
        # command was successful, but only if the command was received.
        return response == b':01ok\r\n'

    def get_actual_current_in_milliamperes(self) -> int:
        """
        Reads the actual current output from the device, returning the value in milliamperes.

        Sends a command to the device to query its current output level. The method checks for the
        configured communication port before issuing the command. Parses the device's response to extract
        the current level in milliamperes.

        :return: The actual current output from the device, in milliamperes.
        :rtype: int
        :raises AssertionError: If the communication port has not been configured.
        :raises IOError: If the device's response is shorter than expected, indicating incomplete or corrupted data.
        :raises ValueError: If converting the response to an integer fails, suggesting an invalid response format.
        """
        assert self._port is not None
        command = self.make_read_actual_current_command(self._address)
        self._port.write(command)
        response = self._port.read_until(b'\r\n')
        if len(response) < 11:
            raise IOError(f'Response is too short: {response}')
        result = int(response[7:-3])  # may raise ValueError
        return result

    def get_actual_current(self) -> float:
        """
        Reads the actual current output from the device, converting the result to amperes.

        Utilizes `read_actual_current_in_milliamperes` to obtain the current output in milliamperes and
        converts this value to amperes for easier interpretation.

        :return: The actual current output from the device, in amperes.
        :rtype: float
        :raises AssertionError: If the communication port has not been configured.
        :raises IOError: If the device's response is shorter than expected, indicating incomplete or corrupted data.
        :raises ValueError: If converting the response to an integer fails, suggesting an invalid response format.
        """
        return self.get_actual_current_in_milliamperes() / 1000.0

    def get_cc_cv_status(self) -> bool:
        """
        Reads the device's current operational mode to determine if it is in Constant Voltage (CV) mode.

        Sends a command to the device to query its operational mode, checking the setup of the communication port before
        proceeding. Parses the device's response to discern between Constant Current (CC) and Constant Voltage (CV) modes.
        In this context, a return value of 0 indicates the device is operating in CV mode, and 1 indicates CC mode.

        :return: True if the device is operating in Constant Voltage (CV) mode, False if operating in Constant Current (CC) mode.
        :rtype: bool
        :raises AssertionError: If the communication port has not been configured.
        :raises IOError: If the device's response is shorter than expected, suggesting incomplete or corrupted data.
        :raises ValueError: If converting the response to an integer fails, indicating an invalid response format.
        """
        assert self._port is not None
        command = self.make_read_cc_cv_status_command(self._address)
        self._port.write(command)
        response = self._port.read_until(b'\r\n')
        if len(response) < 11:
            raise IOError(f'Response is too short: {response}')
        result = int(response[7:-3])  # may raise ValueError
        # 1 means CC (constant current), 0 means CV (constant voltage)
        return result == 0

    def is_in_cv_mode(self) -> bool:
        """
        Determines if the device is operating in Constant Voltage (CV) mode.

        Utilizes `read_cc_cv_status` to check the device's operational mode, specifically identifying if it is in CV
        mode.

        :return: True if the device is in CV mode, False otherwise.
        :rtype: bool
        :raises AssertionError: If the communication port has not been configured.
        :raises IOError: If the device's response is shorter than expected, indicating that the data is incomplete or
                corrupted.
        :raises ValueError: If there is an issue converting the response to an integer, suggesting an invalid response
                format.
        """
        return self.get_cc_cv_status()

    def is_in_cc_mode(self) -> bool:
        """
        Determines if the device is operating in Constant Current (CC) mode.

        Utilizes `read_cc_cv_status` to check the device's operational mode, specifically identifying if it is in CC
        mode.

        :return: True if the device is in CC mode, False otherwise (indicating CV mode).
        :rtype: bool
        :raises AssertionError: If the communication port has not been configured.
        :raises IOError: If the device's response is shorter than expected, indicating that the data is incomplete or
                corrupted.
        :raises ValueError: If there is an issue converting the response to an integer, suggesting an invalid response
                format.
        """
        return not self.get_cc_cv_status()
