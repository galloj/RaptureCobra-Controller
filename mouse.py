import libusb_package
from enum import IntEnum
from abc import ABC, abstractmethod

dev = libusb_package.find(idVendor=0x1d57, idProduct=0xfa61)

if dev is None:
    print("Mouse not found!")
    exit(1)

def send_packet(dev, packet_id: int, packet_data: list[int]):
    print([packet_id, len(packet_data) + 2] + packet_data)
    assert dev.ctrl_transfer(0x21, 0x09, 0x0300 | packet_id, 2, [packet_id, len(packet_data) + 2] + packet_data)

class Color:
    def __init__(self, r: int, g: int, b: int):
        self.r = r
        self.g = g
        self.b = b
    
    def color_to_bytes(self):
        return [self.r, self.g, self.b]

def set_active_profile(dev, profile_id: int):
    send_packet(dev, 0x0c, [profile_id, 0x05])

#import time
#time.sleep(0.1)

class ColorMode(IntEnum):
    DISABLED = 0x00
    STATIC = 0x01
    BREATHING = 0x02
    COLOR_CYCLE = 0x03
    COLOR_CYCLE_BREATHING = 0x04
    WHEEL_COLOR_STATIC = 0x05
    WHEEL_COLOR_BREATHING = 0x06
    COLOR_CYCLE_SLIDING = 0x07
    KNIGHT_RIDER = 0x08

# mode speed 0 is fastest, 255 is slowest

def set_color(dev, profile_id: int, color: Color, color_mode: ColorMode, mode_speed: int):
    color_brightness = 0x08 # 0 is lowest, 8 is highest; or maybe actually pwm resolution?
    send_packet(dev, 0x05, [profile_id, color_mode, mode_speed, color_brightness] + color.color_to_bytes() + [0x01, 0x01, 0x00, 0x00])

#set_color(dev, 1, Color(0xff, 0xff, 0xff), ColorMode.COLOR_CYCLE_SLIDING, 0x04)


class PollingRate(IntEnum):
    HZ_1000 = 0x01 # 1000 Hz
    HZ_500 = 0x02 # 500 Hz
    HZ_250 = 0x03 # 250 Hz
    HZ_125 = 0x04 # 125 Hz
    # other values set it to 250 Hz

def set_polling_rate(dev, profile_id: int, pooling_rate: PollingRate):
    send_packet(dev, 0x06, [profile_id, pooling_rate, 0x00, 0x00, 0x00, 0x00, 0x00])

#set_polling_rate(dev, 1, PollingRate.HZ_1000)

# default values: 800, 1200, 2000, 3200, 5000
# DPI table:
# 100 - 0x04
# 300 - 0x06
# 400 - 0x08
# 500 - 0x0b
# 800 - 0x12
# 1000 - 0x16
# 1200 - 0x1b
# 2000 - 0x2e
# 3000 - 0x45
# 3200 - 0x49
# 4000 - 0x5c
# 5000 - 0x73
# 6000 - 0x145
# 7000 - 0x150
# 8000 - 0x15c
# 9000 - 0x168
# 10000 - 0x173

def set_dpi(dev, profile_id: int, default_option: int, speeds: list[int], colors: list[Color]):
    assert len(speeds) > 0
    assert len(speeds) <= 8
    assert default_option >= 1 and default_option <= len(speeds)
    enabled_options = 0
    for x in speeds:
        enabled_options *= 2
        enabled_options += 1
    assert len(speeds) == len(colors)
    while len(speeds) < 8:
        speeds.append(0x73)
        colors.append(Color(0xff, 0xff, 0xff))
    assert len(speeds) == 8
    assert len(colors) == 8
    data = [profile_id, 0x08, 0x08, enabled_options]
    for _ in range(2):
        number = 0
        for x in range(8):
            number += (speeds[x] & 0x80) >> (7 - x)
        data+=[number]
    for _ in range(2):
        for x in speeds:
            data.append(x & 0x7f)
    data.append(default_option)
    for x in colors:
        data += x.color_to_bytes()
    data.append(0x03)
    send_packet(dev, 0x04, data)

"""set_dpi(dev, 
    1,
    3,
[
    0x12,
    0x1b,
    0x2e,
    0x49,
    0x73,
], [
    Color(0xff, 0x00, 0x00),
    Color(0x00, 0xff, 0x00),
    Color(0x00, 0x00, 0xff),
    Color(0xff, 0x00, 0xff),
    Color(0x00, 0xff, 0xff),
])"""


# left click is [0x02, 0x00, 0x00]
# right lick click is [0x03, 0x00, 0x00]
# middle click is [0x04, 0x00, 0x00]
# back button [0x05, 0x00, 0x00]
# forward button [0x06, 0x00, 0x00]
# left double click [0x07, 0x00, 0x00]
# repeated left click [0x08, 0x00, 0x00]
# scroll up [0x09, 0x00, 0x00]
# scroll down [0x0a, 0x00, 0x00]
# scroll left [0x0b, 0x00, 0x00]
# scroll right [0x0c, 0x00, 0x00]
# cycle dpi is [0x0d, 0x00, 0x00]
# dpi+ is [0x0e, 0x00, 0x00]
# dpi- is [0x0f, 0x00, 0x00]
# keyboard click is [0x11, modifier, hid_code]
# if keyboard modifier is 0x01, then ctrl is pressed
# macro is [0x12, 0x00, macro_id]

# buttons configuration contains 24 buttons -> 72 bytes

# button order:
# - left
# - right
# - middle
# - side up
# - side down
# - unknown
# - center up
# - center down
# - unknown
# - unknown
# - scroll down
# - scroll up

def set_key_binding(dev, profile_id: int, buttons_configuration: list[int]):
    assert profile_id >= 1

    send_packet(dev, 0x08, [profile_id] + buttons_configuration + [0x00, 0x00])

class MacroCommand(ABC):
    @abstractmethod
    def to_bytes(self) -> list[int]:
        pass

class MacroButtonPress(MacroCommand):
    # button from https://deskthority.net/wiki/Scancode
    # or alternative mouse buttons:
    # 0xf1 - mouse left button
    # 0xf2 - mouse right button
    # 0xf3 - mouse middle button
    # 0xf4 - mouse backward button
    # 0xf5 - mouse forward button
    #
    # delay is in ms
    #
    # release is True if it isn't press, but release
    def __init__(self, button: int, delay: int, release: bool):
        self.button = button
        self.delay = delay
        self.release = release

    def to_bytes(self):
        delay_num = round(self.delay/2)
        assert delay_num >= 0 and delay_num <= 0x7f
        return [(0x80 * self.release) | delay_num, self.button]
    
class MacroDelay(MacroCommand):
    # delay is in ms
    def __init__(self, delay: int):
        self.delay = delay

    def to_bytes(self):
        delay_num = round(self.delay/200)
        assert delay_num >= 0 and delay_num <= 0xff
        return [delay_num, 0x03]

class RepeatCondition(IntEnum):
    REPEAT_COUNT = 0 # repeat based on repeat count
    BUTTON_PRESS = 1 # repeat till another button press
    BUTTON_RELEASE = 2 # repeat till button release

def set_macro(dev, profile_id: int, repeat_condition: RepeatCondition, repeat_count: int, macro_name: str, macro: list[MacroCommand]):
    assert profile_id >= 1

    macro_name_bytes = [*macro_name.encode('ascii')]
    assert len(macro_name) <= 20
    macro_name_bytes += b'\x00' * (20 - len(macro_name))

    assert len(macro) <= 200

    byte_macro = []
    for x in macro:
        byte_macro += x.to_bytes()
    byte_macro += [0x00] * (200 - len(byte_macro))


    send_packet(dev, 0x09, [profile_id, repeat_condition, 0x00, 0x00, 0x00, repeat_count] + macro_name_bytes + [len(macro)] + byte_macro)