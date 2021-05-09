import webbrowser
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
model = None
keyboard_index = None
rgb_or_profile = None


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
    R = int(red.get())
    G = int(green.get())
    B = int(blue.get())
    timer = threading.Thread(target=main, args=(entered_minutes, R, G, B,))
    timer.start()
    status.set("Status: On\n")

def donate():
    webbrowser.open('https://www.paypal.com/donate?business=G5MLHBKCAHYRW&currency_code=USD', new=0, autoraise=True)


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


def turn_on_leds(all_leds, R, G, B):
    print("turn on")
    for led in all_leds[keyboard_index]:
        all_leds[keyboard_index][led] = (R, G, B)
    sdk.set_led_colors_buffer_by_device_index(keyboard_index, all_leds[keyboard_index])
    sdk.set_led_colors_flush_buffer()
    #old
    """cnt = len(all_leds)
    for di in range(cnt):
        device_leds = all_leds[di]
        for led in device_leds:
            device_leds[led] = (R, G, B)
        sdk.set_led_colors_buffer_by_device_index(di, device_leds)
    sdk.set_led_colors_flush_buffer()"""


def turn_off_leds(all_leds):
    print("turn off")
    for led in all_leds[keyboard_index]:
        all_leds[keyboard_index][led] = (0, 0, 0)
    sdk.set_led_colors_buffer_by_device_index(keyboard_index, all_leds[keyboard_index])
    sdk.set_led_colors_flush_buffer()
    #old
    """cnt = len(all_leds)
    for di in range(cnt):
        device_leds = all_leds[di]
        for led in device_leds:
            device_leds[led] = (0, 0, 0)
        sdk.set_led_colors_buffer_by_device_index(di, device_leds)
    sdk.set_led_colors_flush_buffer()"""


def main(secs, R, G, B):
    global sdk
    global flag
    global status
    global model
    global keyboard_index
    global rgb_or_profile
    print(rgb_or_profile.get())
    sdk = CueSdk()
    connected = sdk.connect()
    print(sdk.get_devices())

    keyboard_index = 0
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
    for i in sdk.get_devices():
        if str(i.type) == 'CorsairDeviceType.Keyboard':
            break
        else:
            keyboard_index += 1
    print(str(sdk.get_devices()[keyboard_index].type))
    model.set("\nModel: " + str(sdk.get_devices()[keyboard_index]) + "\n")
    print("keyboard_index :" + str(keyboard_index))
    print("keyboard lights will shutdown after: " + str(secs / 60) + " minutes")
    print("Checking idle")
    if rgb_or_profile.get() == 0:
        turn_on_leds(colors, R, G, B)
    print("Timer Started")
    while flag:
        idle = get_idle_duration()
        if rgb_or_profile.get() == 0:
            if sdk.get_device_count() == -1:
                flag = True
                status.set("Status: Error\n")
            if idle > secs:
                # checking current led color to prevent keyboard spamming
                if colors[keyboard_index][CorsairLedId.K_F] != (0, 0, 0):
                    turn_off_leds(colors)
            elif colors[keyboard_index][CorsairLedId.K_F] == (0, 0, 0):
                turn_on_leds(colors, R, G, B)
        elif rgb_or_profile.get() == 1:
            if sdk.get_device_count() == -1:
                flag = True
                status.set("Status: Error\n")
            if idle > secs:
                sdk.request_control()
            else:
                sdk.release_control()
        time.sleep(0.1)
    print("Timer stopped")
    flag = True


if __name__ == "__main__":
    window = Tk()
    status = StringVar()
    model = StringVar()
    rgb_or_profile = IntVar()
    model.set("\nModel: \n")
    status.set("Status: Off\n")
    window.title("Corsair Sleep Timer")
    window.configure(background="grey18")
    Label(window, text="\nCorsair Sleep Timer\n Created by Gil Matsliah \n\nAlso Known as gilma0\n", bg="gray18", fg="white", font="none 18 bold").grid(row=0, columnspan=8)
    Label(window, text="          Minutes to shut off:", bg="gray18", fg="white", font="none 12 bold").grid(row=2, column=0, columnspan=4, sticky=E)
    textEntry = Entry(window, width=7, bg="white")
    textEntry.grid(row=2, column=4, columnspan=3, sticky=W)
    textEntry.insert(END, "5")
    Label(window, text="", bg="gray18").grid(row=3, columnspan=7)
    Label(window, text="R:", bg="gray18", fg="white", font="none 12 bold").grid(row=4, column=0, sticky=E)
    Label(window, text="G:", bg="gray18", fg="white", font="none 12 bold").grid(row=4, column=2, sticky=E)
    Label(window, text="B:", bg="gray18", fg="white", font="none 12 bold").grid(row=4, column=5, sticky=E)
    red = Entry(window, width=7)
    red.grid(row=4, column=1, sticky=W)
    green = Entry(window, width=7)
    green.grid(row=4, column=3, sticky=W)
    blue = Entry(window, width=7)
    blue.grid(row=4, column=6, sticky=W)
    red.insert(END, "255")
    green.insert(END, "0")
    blue.insert(END, "0")
    Label(window, text="", bg="gray18").grid(row=5, columnspan=8)
    #Checkbutton(window, text="Ignore RGB values and use current profile", bg="gray18", fg="white", font="none 12 bold", variable=rgb_or_profile).grid(row=6, columnspan=8)
    Checkbutton(window, text="Ignore RGB values and use current profile", onvalue=1, offvalue=0, bg="gray18", fg="white", activebackground="gray18", activeforeground="white", selectcolor="gray18", font="none 12 bold", variable=rgb_or_profile).grid(row=6, columnspan=8)
    Label(window, textvariable=model, bg="gray18", fg="white", font="none 12 bold").grid(row=7, columnspan=8)
    Label(window, textvariable=status, bg="gray18", fg="white", font="none 12 bold").grid(row=8, columnspan=8)
    try:
        startButton = PhotoImage(file='buttons/start_img.png')
        Button(window, image=startButton, bg="gray18", border=0, activebackground="gray18", command=start_click).grid(row=9, column=0, columnspan=4)
    except:
        Button(window, text="Start", width=5, command=start_click).grid(row=9, column=0, columnspan=4)
    try:
        stopButton = PhotoImage(file='buttons/stop_img.png')
        Button(window, image=stopButton, bg="gray18", border=0, activebackground="gray18", command=stop_click).grid(row=9, column=3, columnspan=4)
    except:
        Button(window, text="Stop", width=5, command=stop_click).grid(row=9, column=3, columnspan=4)
    Label(window, text="\nIf you like my work\n please consider donating :)\n", bg="gray18", fg="white", font="none 12 bold").grid(row=10, columnspan=8)
    try:
        donate_img = PhotoImage(file='buttons/donate.png')
        Button(window, image=donate_img, bg="gray18", border=0, activebackground="gray18", command=donate).grid(row=11, columnspan=8)
    except:
        Button(window, text="Donate!", width=7, command=donate).grid(row=11, columnspan=8)
    Label(window, text="\n", bg="gray18").grid(row=12)
    window.mainloop()
