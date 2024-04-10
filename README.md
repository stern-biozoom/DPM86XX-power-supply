# Python class to control Joy-IT DPM86XX power supply

## Name
Joy-IT DPM86XX Power Supply Controller

## Description
This Python library provides an interface to control and automate operations for the Joy-IT DPM86XX series programmable lab power supply units. It enables developers and engineers to integrate power supply management into their automation scripts or projects, offering capabilities such as setting voltage/current levels, reading device outputs, and toggling power supply status programmatically. The library abstracts the communication protocol details, making it straightforward to use the DPM86XX's features without deep knowledge of its underlying communication mechanisms.

### Features
- Set output voltage and current
- Read actual output voltage and current
- Toggle output status (on/off)
- Read device temperature
- Monitor CC (Constant Current) and CV (Constant Voltage) modes
- Easy integration with Python projects

### Background
The Joy-IT DPM86XX series are versatile and programmable power supply units ideal for a wide range of applications in electronics testing, repair, and research. This library leverages the DPM86XX communication protocol to provide an accessible and efficient way to control these devices through Python, enhancing automation and monitoring capabilities.

## Usage
To use this library, ensure you have a Joy-IT DPM86XX power supply connected to your computer or control device via a serial connection. Here's a simple example of how to set the voltage and current:

```python
from dpm86xx import DPM86XX

# Initialize the DPM86XX controller with the serial port
dpm = DPM86XX('/dev/ttyUSB0')  # Adjust the port as necessary

# Set the voltage to 5V and current to 500mA
dpm.set_voltage_and_current(5.0, 500)

# Read back the actual voltage and current
voltage = dpm.get_actual_voltage()
current = dpm.get_actual_current_in_milliamperes()

print(f'Voltage: {voltage}V, Current: {current}mA')

# Turn off the output
dpm.set_output_status(0)
```

### Expected Output
```
Voltage: 5.0V, Current: 500mA
```

For more sophisticated examples and usage, refer to the included examples in the project repository or the detailed documentation.

## References
For detailed information about the power supply and its capabilities, refer to the following resources:
- [Data sheet](https://joy-it.net/files/files/Produkte/JT-DPM8605/Datasheet%20JT-DPM8605-20200605.pdf)
- [Communication protocol description](https://joy-it.net/files/files/Produkte/JT-DPM8624/JT-DPM86XX_Communication_protocol_2023-01-05.pdf)

## Support
For support, start by checking the [issue tracker](#) for similar issues. If your issue is unique, feel free to open a new issue. For direct inquiries or detailed discussions, you can contact [biozoom services GmbH](#).

## Project status
This project is actively maintained. New features and improvements are continually being added. Contributions are welcome. For major changes or new feature requests, please open an issue first to discuss what you would like to change.