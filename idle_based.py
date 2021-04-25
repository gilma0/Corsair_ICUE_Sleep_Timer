from ctypes import Structure, windll, c_uint, sizeof, byref
from cuesdk import CueSdk
import time

class LASTINPUTINFO(Structure):
    _fields_ = [
        ('cbSize', c_uint),
        ('dwTime', c_uint),
    ]

def get_idle_duration():
    lastInputInfo = LASTINPUTINFO()
    lastInputInfo.cbSize = sizeof(lastInputInfo)
    windll.user32.GetLastInputInfo(byref(lastInputInfo))
    millis = windll.kernel32.GetTickCount() - lastInputInfo.dwTime
    return millis / 1000.0

def get_available_leds():
    leds = list()
    device_count = sdk.get_device_count()
    for device_index in range(device_count):
        led_positions = sdk.get_led_positions_by_device_index(device_index)
        leds.append(led_positions)
    return leds


def turnOnLeds(all_leds):
    print("turn on")
    cnt = len(all_leds)
    for di in range(cnt):
        device_leds = all_leds[di]
        for led in device_leds:
            device_leds[led] = (255, 0, 0)
        sdk.set_led_colors_buffer_by_device_index(di, device_leds)
    sdk.set_led_colors_flush_buffer()

def turnOffLeds(all_leds):
    print("turn off")
    cnt = len(all_leds)
    for di in range(cnt):
        device_leds = all_leds[di]
        for led in device_leds:
            device_leds[led] = (0, 0, 0)
        sdk.set_led_colors_buffer_by_device_index(di, device_leds)
    sdk.set_led_colors_flush_buffer()

def main(secs):
    global sdk
    sdk = CueSdk()
    connected = sdk.connect()
    print(sdk.protocol_details)
    print(sdk.get_devices())
    if not connected:
        err = sdk.get_last_error()
        print("Handshake failed: %s" % err)
        return

    colors = get_available_leds()
    if not colors:
        print("Leds not available")
        return

    print("Checking idle")
    turnOnLeds(colors)
    while True:
        idle = get_idle_duration()
        #print(idle)
        if idle > secs:
            #checking current led color to prevent keyboard spamming
            if colors[0][14] == (255, 0, 0):
                turnOffLeds(colors)
        elif colors[0][14] == (0, 0, 0):
                turnOnLeds(colors)
        time.sleep(0.1)


if __name__ == "__main__":
    main(300) #change to how many seconds until leds shuts off