import os
import pickle
import webbrowser
from ctypes import Structure, windll, c_uint, sizeof, byref
import pystray
from pystray import MenuItem as item
import PIL.Image
from cuesdk import CueSdk, CorsairLedId
import threading
import time
import datetime
from tkinter import *


class LASTINPUTINFO(Structure):
    """
    Detects input from system
    # took from the web
    """
    _fields_ = [
        ('cbSize', c_uint),
        ('dwTime', c_uint),
    ]


activity_flag = True
control_flag = True
timer = threading.Thread()
icon_thread = threading.Thread()
sleep_thread = threading.Thread()
status = None
model = None
keyboard_index = None
use_icue_settings = None
sdk = None
red_save = None
green_save = None
blue_save = None
minutes_save = None
auto_start = None
auto_minimize = None
auto_start_thread = threading.Thread()


def cue_check():
    """
    In case of auto start checks ICUE and keyboard availability
    """
    while not CueSdk().connect():
        print("ICUE not available!")
        time.sleep(0.1)
    while not CueSdk().get_device_count():
        print("leds not available")
        time.sleep(0.1)
    start_click()


def minimize():
    window.withdraw()


def start_click():
    """
    Once the start button is pressed (or auto start) -> starts a timer thread
    """
    global timer
    global status
    if timer.is_alive():
        print("Timer was already running, restarting!")
        stop_click()
        timer.join()
        start_click()
        return
    entered_minutes = float(textEntry.get()) * 60
    R = int(red.get())
    G = int(green.get())
    B = int(blue.get())
    timer = threading.Thread(target=main, args=(entered_minutes, R, G, B,))
    timer.start()
    status.set("Status: On\n")
    save()


def sleep_timer():
    """
    In case PC sleep is detected restarts the program from scratch.
    """
    curtime = datetime.datetime.now()
    while True:
        time.sleep(1)
        diff = (datetime.datetime.now() - curtime).total_seconds()
        print(diff)
        if diff > 10:
            print("....... I'm Awake .......")
            os.execl(sys.executable, sys.executable, *sys.argv)
            while(True):
                print("blabla")
        curtime = datetime.datetime.now()



def donate():
    webbrowser.open('https://www.paypal.com/donate?business=G5MLHBKCAHYRW&currency_code=USD', new=0, autoraise=True)


def quit_window(icon, item):
    """
    Input: icon thread, item clicked
    Stops the program.
    """
    if icon_thread.is_alive():
        icon.stop()
    stop_app()


def show_window(icon, item):
    """
    Input: icon thread, item clicked
    Restores the program Gui window.
    """
    window.after(0, window.deiconify)


def withdraw_window():
    """
    Minimize the program to an icon
    """
    image = PIL.Image.open("icon\\python.ico")
    menu = pystray.Menu(item('Quit', quit_window), item('Show', show_window, default=True))
    icon = pystray.Icon("name", image, "Corsair timer", menu)
    icon.run()


def stop_click():
    """
    Changing activity_flag to False so the timer thread will stop
    """
    global activity_flag
    if not timer.is_alive():
        print("Nothing to stop")
        return
    sdk.request_control()
    sdk.release_control()
    activity_flag = False
    status.set("Status: Off\n")



def get_idle_duration():
    """
    Output: idle time
    Taken from the web
    Uses the class LASTINPUTINFO to get the current idle time
    """
    lastInputInfo = LASTINPUTINFO()
    lastInputInfo.cbSize = sizeof(lastInputInfo)
    windll.user32.GetLastInputInfo(byref(lastInputInfo))
    millis = windll.kernel32.GetTickCount() - lastInputInfo.dwTime
    return millis / 1000.0


def get_available_leds():
    """
    Output: list of leds available to control
    Taken from a code sample of Cuesdk
    """
    leds = list()
    device_count = sdk.get_device_count()
    for device_index in range(device_count):
        led_positions = sdk.get_led_positions_by_device_index(device_index)
        leds.append(led_positions)
    return leds


def turn_on_leds(all_leds, R, G, B):
    """
    Input: list of leds and RGB values to apply
    Partly taken from a code sample of Cuesdk, added my values.
    """
    print("turn on")
    for led in all_leds[keyboard_index]:
        all_leds[keyboard_index][led] = (R, G, B)
    sdk.set_led_colors_buffer_by_device_index(keyboard_index, all_leds[keyboard_index])
    sdk.set_led_colors_flush_buffer()


def turn_off_leds(all_leds):
    """
    Input: list of leds
    Applies zero RGB values to all the leds available so the keyboard lights will shut off
    """
    print("turn off")
    for led in all_leds[keyboard_index]:
        all_leds[keyboard_index][led] = (0, 0, 0)
    sdk.set_led_colors_buffer_by_device_index(keyboard_index, all_leds[keyboard_index])
    sdk.set_led_colors_flush_buffer()


def save():
    """
    Saving last user applied values using pickle
    """
    config = {
        'use_icue_settings': use_icue_settings.get(),
        'red_save': red.get(),
        'green_save': green.get(),
        'blue_save': blue.get(),
        'minutes_save': textEntry.get(),
        'auto_start' : auto_start.get(),
        'auto_minimize' : auto_minimize.get(),
    }
    with open("saved_settings.dat", "wb") as pickle_file:
        pickle.dump(config, pickle_file, pickle.HIGHEST_PROTOCOL)


def load():
    """
    Loading last user applied values from file created by pickle
    In case none has been found applies default values
    """
    try:
        with open("saved_settings.dat", "rb") as pickle_file:
            config = pickle.load(pickle_file)
        print(config)
        use_icue_settings.set(config.get('use_icue_settings'))
        red.insert(END, config.get('red_save'))
        green.insert(END, config.get('green_save'))
        blue.insert(END, config.get('blue_save'))
        textEntry.insert(END,config.get('minutes_save'))
        auto_start.set(config.get('auto_start'))
        auto_minimize.set(config.get('auto_minimize'))
    except IOError:
        use_icue_settings.set(0)
        textEntry.insert(END, "5")
        red.insert(END, "255")
        green.insert(END, "0")
        blue.insert(END, "0")
        auto_start.set(0)
        auto_minimize.set(0)
        pass
    if auto_start.get() == 1:
        """
        In the case of start at launch
        """
        auto_start_thread = threading.Thread(target=cue_check)
        auto_start_thread.start()
    if auto_minimize.get() == 1:
        minimize()


def stop_app():
    stop_click()
    window.destroy()


def main(secs, R, G, B):
    """
    Input: time to shut leds off and RGB values
    After checking everything is ready to run (mainly ICUE and keyboard) and some GUI updating (keyboard model and such)
    Runs one of the following:
        use_icue_settings.get() == 0:
            apply user set RGB values to the keyboard until set idle time reached
        use_icue_settings.get() == 1:
            apply user set ICUE profile to the keyboard until set idle time reached
    """
    global sdk
    global activity_flag
    global control_flag
    global keyboard_index
    print(use_icue_settings.get())
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
    if use_icue_settings.get() == 0:
        turn_on_leds(colors, R, G, B)
    print("Timer Started")
    while activity_flag:
        idle = get_idle_duration()
        if use_icue_settings.get() == 0:
            if sdk.get_device_count() == -1:
                activity_flag = True
                status.set("Status: Error\n")
            if idle > secs:
                # checking current led color to prevent keyboard spamming
                if colors[keyboard_index][CorsairLedId.K_F] != (0, 0, 0):
                    turn_off_leds(colors)
            elif colors[keyboard_index][CorsairLedId.K_F] == (0, 0, 0):
                turn_on_leds(colors, R, G, B)
        elif use_icue_settings.get() == 1:
            if sdk.get_device_count() == -1:
                activity_flag = True
                status.set("Status: Error\n")
            if idle > secs:
                if control_flag:
                    print("request")
                    control_flag = sdk.request_control()
                    print(control_flag)
            else:
                if not control_flag:
                    print("release")
                    control_flag = sdk.release_control()
                    print(control_flag)
        time.sleep(0.1)
    print("Timer stopped")
    activity_flag = True


if __name__ == "__main__":
    """
    GUI stuff and last user save loading
    """
    window = Tk()
    status = StringVar()
    model = StringVar()
    red_save = StringVar()
    green_save = StringVar()
    blue_save = StringVar()
    minutes_save = StringVar()
    use_icue_settings = IntVar()
    auto_start = IntVar()
    auto_minimize = IntVar()
    icon_thread = threading.Thread(target=withdraw_window)
    sleep_thread = threading.Thread(target=sleep_timer)
    sleep_thread.start()
    icon_thread.start()
    model.set("\nModel: \n")
    status.set("Status: Off\n")
    window.title("Corsair Sleep Timer")
    window.configure(background="grey18")
    Label(window, text="\nCorsair Sleep Timer\n Created by Gil Matsliah \n\nAlso Known as gilma0\n", bg="gray18", fg="white", font="none 18 bold").grid(row=0, columnspan=8)
    Label(window, text="          Minutes to shut off:", bg="gray18", fg="white", font="none 12 bold").grid(row=2, column=0, columnspan=4, sticky=E)
    textEntry = Entry(window, width=7, bg="white")
    textEntry.grid(row=2, column=4, columnspan=3, sticky=W)
    textEntry.insert(END, minutes_save.get())
    print(minutes_save.get())
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
    red.insert(END, red_save.get())
    green.insert(END, green_save.get())
    blue.insert(END, blue_save.get())
    Label(window, text="", bg="gray18").grid(row=5, columnspan=8)
    Checkbutton(window, text="Ignore RGB values and use current profile", onvalue=1, offvalue=0, bg="gray18", fg="white", activebackground="gray18", activeforeground="white", selectcolor="gray18", font="none 12 bold", variable=use_icue_settings).grid(row=6, columnspan=8)
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
    Label(window, text="", bg="gray18").grid(row=12, columnspan=8)
    Checkbutton(window, text="Start at launch", onvalue=1, offvalue=0, bg="gray18",
                fg="white", activebackground="gray18", activeforeground="white", selectcolor="gray18",
                font="none 12 bold", variable=auto_start).grid(row=13, columnspan=8, sticky=W)
    Checkbutton(window, text="Launch minimized", onvalue=1, offvalue=0, bg="gray18",
                fg="white", activebackground="gray18", activeforeground="white", selectcolor="gray18",
                font="none 12 bold", variable=auto_minimize).grid(row=13, columnspan=8, sticky=E)
    Label(window, text="", bg="gray18").grid(row=14)
    window.protocol("WM_DELETE_WINDOW", minimize)
    load()
    window.mainloop()
    os._exit(0)
