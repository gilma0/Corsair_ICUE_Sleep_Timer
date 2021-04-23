import threading

from cuesdk import CueSdk
import time
import keyboard


def get_available_leds():
    leds = list()
    device_count = sdk.get_device_count()
    for device_index in range(device_count):
        led_positions = sdk.get_led_positions_by_device_index(device_index)
        leds.append(led_positions)
    return leds


def turnOnLeds(all_leds):
    cnt = len(all_leds)
    for di in range(cnt):
        device_leds = all_leds[di]
        for led in device_leds:
            device_leds[led] = (255, 0, 0)  # green
        sdk.set_led_colors_buffer_by_device_index(di, device_leds)
    sdk.set_led_colors_flush_buffer()

def turnOffLeds(all_leds):
    cnt = len(all_leds)
    for di in range(cnt):
        device_leds = all_leds[di]
        for led in device_leds:
            device_leds[led] = (0, 0, 0)  # green
        sdk.set_led_colors_buffer_by_device_index(di, device_leds)
    sdk.set_led_colors_flush_buffer()

def main():
    global sdk

    sdk = CueSdk()
    connected = sdk.connect()
    if not connected:
        err = sdk.get_last_error()
        print("Handshake failed: %s" % err)
        return

    colors = get_available_leds()
    if not colors:
        return

    print("Looking for input...")
    x = 0
    while (True):
        try:  # used try so that if user pressed other than the given key error will not be shown
            if keyboard.is_pressed('`'):  # if key 'q' is pressed
                print('You Pressed A Key!')
                turnOnLeds(colors)
                x = 0
                #qbreak  # finishing the loop
        except:
            break  # if user pressed a key other than the given key the loop will break
        x += 0.01
        if(x > 1):
            turnOffLeds(colors)
        time.sleep(0.01)

def main2(secs):
    global sdk

    sdk = CueSdk()
    connected = sdk.connect()
    if not connected:
        err = sdk.get_last_error()
        print("Handshake failed: %s" % err)
        return

    colors = get_available_leds()
    if not colors:
        return

    print("Looking for input...")
    temp = 0
    while (temp < 1):
        temp += 0.01
        if (temp > 1):
            print("First run to turn off the lights before waiting for keyboard events")
            turnOffLeds(colors)
            break
        time.sleep(0.01)
    while True:
        if keyboard.read_key():
            print('A Key Has Been Pressed!, Lights Up!')
            turnOnLeds(colors)
            x = 0
            while True:
                x += 0.01
                if (x > secs):
                    turnOffLeds(colors)
                    break
                time.sleep(0.01)


def main3(secs):
    global sdk

    sdk = CueSdk()
    connected = sdk.connect()
    if not connected:
        err = sdk.get_last_error()
        print("Handshake failed: %s" % err)
        return

    colors = get_available_leds()
    if not colors:
        return

    print("Looking for input...")
    turnOffLeds(colors)
    while True:
        if keyboard.read_key():
            print('A Key Has Been Pressed!, Lights Up!')
            turnOnLeds(colors)
            x = 0
            while True:
                x += 0.01
                if (x > secs):
                    turnOffLeds(colors)
                    break
                time.sleep(0.01)


timer = 0

def keyPress():
    global timer
    while True:
        if keyboard.read_key():
            print("A Key Has Been Pressed, Lights Up!")
            timer = 0
        time.sleep(0.1)



def main4(secs):
    global sdk
    global timer
    sdk = CueSdk()
    connected = sdk.connect()
    if not connected:
        err = sdk.get_last_error()
        print("Handshake failed: %s" % err)
        return

    colors = get_available_leds()
    if not colors:
        print("Leds not available")
        return

    print("Looking for key press...")
    turnOffLeds(colors)
    keyboardEventThread = threading.Thread(target=keyPress)
    keyboardEventThread.start()
    while True:
        #print("timer: " + str(timer))
        if timer > secs:
            turnOffLeds(colors)
        else:
            turnOnLeds(colors)
        timer += 0.1
        time.sleep(0.1)

if __name__ == "__main__":
    main4(1)