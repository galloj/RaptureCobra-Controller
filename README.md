# Controlling of [Rapture Cobra mouse](https://www.alza.cz/rapture-cobra-cerna-d6900118.htm)

The python script in this repository can be used for controlling Rapture Cobra mouse.

## Supported features
- changing of mouse colors
- configuring polling rate
- configuring DPI
- configuring keybindings
- creating macros
- having multiple profiles on the mouse

**WARNING**: Every configuration change is saved to the persistent memory of the mouse. The memory cycle count is not known.


## Installation

You have to install `libusb`/`libusb_package` as dependency. Also if you are running on Windows then you will need to use [Zadig](https://zadig.akeo.ie/), `Options -> List all devices`, `2.4G Wireless Mouse (Interface 2)` and `Replace driver`. Please note that this will make you unable to use the mouse with the original software unless you remove the WinUSB driver from the device.
