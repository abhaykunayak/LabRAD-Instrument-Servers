# LabRAD Instrument Servers

The LabRAD Instrument Servers repository houses a collection of LabRAD servers, each tailored for specific pieces of hardware. Some servers provide basic functionality, while others cater to more specialized needs. As you explore this repository, you’ll encounter servers that facilitate communication with various instruments and devices used in scientific experiments.

## Instrument servers

List of instruments with supported servers:

- SR770: A server related to Anritsu instruments.

### Sub-subheading

## Auxillary files

gpib_bus.py: This server offers an interface to a GPIB bus (using VISA). If you’re dealing with GPIB-connected devices, this one’s handy.
serial_server: If you’re working with serial ports, this server provides a straightforward interface using pyserial.
data_vault.py: Need to store numeric data from experiments? This server integrates with the LabRAD grapher client to manage your data.
sampling_scope.py: For interfacing with sampling oscilloscopes.
Contributing
Feel free to contribute to this repository! If you encounter any issues or have improvements to suggest, follow these steps:

- Item 1
- Item 2
  - Subitem A
  - Subitem B
