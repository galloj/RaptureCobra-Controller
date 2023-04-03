import libusb_package

dev = libusb_package.find(idVendor=0x1d57, idProduct=0xfa61)

if dev is None:
    print("Mouse not found!")
    exit(1)

def send_packet(dev, packet_id, packet_data):
    print([packet_id, len(packet_data) + 2] + packet_data)
    assert dev.ctrl_transfer(0x21, 0x09, 0x0300 | packet_id, 2, [packet_id, len(packet_data) + 2] + packet_data)

class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
    
    def color_to_bytes(self):
        return [self.r, self.g, self.b]

# not sure what is purpose of this packet, but it is sent before every other packet
#send_packet(dev, 0x0c, [0x01, 0x05])
#import time
#time.sleep(0.1)

# color modes:
# 0x00 - disabled
# 0x01 - static
# 0x02 - breathing
# 0x03 - color cycle
# 0x04 - color cycle breathing
# 0x05 - wheel color static
# 0x06 - wheel color breathing
# 0x07 - color cycle sliding
# 0x08 - knight rider

# mode speed 0 is fastest, 255 is slowest

def set_color(dev, color, color_mode, mode_speed):
    color_brightness = 0x08 # 0 is lowest, 8 is highest; or maybe actually pwm resolution?
    send_packet(dev, 0x05, [0x01, color_mode, mode_speed, color_brightness] + color.color_to_bytes() + [0x01, 0x01, 0x00, 0x00])

#set_color(dev, Color(0xff, 0xff, 0xff), 0x07, 0x04)

# only supported polling rates are:
# 0x01 - 1000 Hz
# 0x02 - 500 Hz
# 0x04 - 250 Hz
# 0x08 - 125 Hz
# others set it to 250 Hz
def set_polling_rate(dev, pooling_rate):
    send_packet(dev, 0x06, [0x01, pooling_rate, 0x00, 0x00, 0x00, 0x00, 0x00])

#set_polling_rate(dev, 0x1)

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

def set_dpi(dev, default_option, speeds, colors):
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
    data = [0x01, 0x08, 0x08, enabled_options]
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