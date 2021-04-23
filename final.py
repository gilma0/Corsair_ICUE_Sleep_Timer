import threading

from cuesdk import CueSdk
import time
import keyboard

timer = 0

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
            device_leds[led] = (255, 0, 0)  # green
        sdk.set_led_colors_buffer_by_device_index(di, device_leds)
    sdk.set_led_colors_flush_buffer()

def turnOffLeds(all_leds):
    print("turn off")
    cnt = len(all_leds)
    for di in range(cnt):
        device_leds = all_leds[di]
        for led in device_leds:
            device_leds[led] = (0, 0, 0)  # green
        sdk.set_led_colors_buffer_by_device_index(di, device_leds)
    sdk.set_led_colors_flush_buffer()

def keyPress():
    global timer
    while True:
        if keyboard.read_key():
            timer = 0
            #print("A Key Has Been Pressed, Lights Up!")
        time.sleep(0.1)

def main(secs):
    global sdk
    global timer
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

    print("Looking for key press...")
    turnOnLeds(colors)
    keyboardEventThread = threading.Thread(target=keyPress)
    keyboardEventThread.start()
    while True:
        #print("timer: " + str(timer))
        if timer > secs:
            turnOffLeds(colors)
            keyboard.read_key() #stops wasted cycles and useless updates to keyboard
            turnOnLeds(colors)
        timer += 0.1
        time.sleep(0.1)

if __name__ == "__main__":
    main(1)