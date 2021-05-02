from ctypes import Structure, windll, c_uint, sizeof, byref
from cuesdk import CueSdk, CorsairLedId
import threading
import time
from tkinter import *


class LASTINPUTINFO(Structure):
    _fields_ = [
        ('cbSize', c_uint),
        ('dwTime', c_uint),
    ]


flag = True
timer = threading.Thread()
status = None


def start_click():
    global timer
    global status
    if timer.is_alive():
        print("Timer was already running, restarting!")
        stop_click()
        time.sleep(0.2)
        start_click()
        return
    entered_minutes = float(textEntry.get()) * 60
    timer = threading.Thread(target=main, args=(entered_minutes,))
    timer.start()
    status.set("Status: On\n")


def stop_click():
    global flag
    global timer
    global status
    if not timer.is_alive():
        print("Nothing to stop")
        return
    flag = False
    status.set("Status: Off\n")


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


def turn_on_leds(all_leds):
    print("turn on")
    cnt = len(all_leds)
    for di in range(cnt):
        device_leds = all_leds[di]
        for led in device_leds:
            device_leds[led] = (255, 0, 0)
        sdk.set_led_colors_buffer_by_device_index(di, device_leds)
    sdk.set_led_colors_flush_buffer()


def turn_off_leds(all_leds):
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
    global flag
    global status
    sdk = CueSdk()
    connected = sdk.connect()
    print(sdk.get_devices())
    if not connected:
        err = sdk.get_last_error()
        print("Handshake failed: %s" % err)
        status.set("Status: Error\n")
        return

    colors = get_available_leds()
    if not colors:
        print("Leds not available")
        status.set("Status: Error\n")
        return
    print("keyboard lights will shutdown after: " + str(secs / 60) + " minutes")
    print("Checking idle")
    turn_on_leds(colors)
    print("Timer Started")
    while flag:
        idle = get_idle_duration()
        if sdk.get_device_count() == -1:
            flag = True
            status.set("Status: Error\n")
        if idle > secs:
            # checking current led color to prevent keyboard spamming
            if colors[0][CorsairLedId.K_F] == (255, 0, 0):
                turn_off_leds(colors)
        elif colors[0][CorsairLedId.K_F] == (0, 0, 0):
            turn_on_leds(colors)
        time.sleep(0.1)
    print("Timer stopped")
    flag = True


if __name__ == "__main__":
    window = Tk()
    status = StringVar()
    status.set("Status: Off\n")
    window.title("Corsair Led Sleep Timer")
    window.configure(background="grey18")
    Label(window, text="\nCorsair Sleep Timer\nCreated by Gil Matsliah\n\nAlso Known as gilma0\n", bg="gray18", fg="white", font="none 18 bold").grid(row=0, column=1, columnspan=2, sticky=E)
    Label(window, text="Minutes to shut off:", bg="gray18", fg="white", font="none 12 bold").grid(row=1, column=1, sticky=W)
    textEntry = Entry(window, width=15, bg="white")
    textEntry.grid(row=1, column=2, sticky=W)
    textEntry.insert(END, "5")
    Label(window, text="", bg="gray18").grid(row=2, column=4)
    Label(window, textvariable=status, bg="gray18", fg="white", font="none 12 bold").grid(row=3, column=1, columnspan=2)
    try:
        startButton = PhotoImage(file='buttons/start_img.png')
        Button(window, image=startButton, bg="gray18", border=0, activebackground="gray18", command=start_click).grid(row=4, column=1, sticky=N)
    except:
        Button(window, text="Start", width=5, command=start_click).grid(row=4, column=1, sticky=N)
    try:
        stopButton = PhotoImage(file='buttons/stop_img.png')
        Button(window, image=stopButton, bg="gray18", border=0, activebackground="gray18", command=stop_click).grid(row=4,column=2,sticky=W)
    except:
        Button(window, text="Stop", width=5, command=stop_click).grid(row=4, column=2, sticky=W)
    Label(window, text="\n", bg="gray18").grid(row=5)
    window.mainloop()
