from tkinter import Tk, Canvas, PhotoImage, Entry, END, Button
from win32api import GetTickCount, GetLastInputInfo

import time
import threading
from win10toast import ToastNotifier
from pystray import MenuItem
import pystray
from PIL import Image
import sys
import datetime

import os


def threadAtTheBackground():
    threading.Thread(target=start, daemon=True).start()


def start():
    timer = timerStart()
    activityCheck()


# Main Logic :

# Default duration of prompt Interval
promptInterval = 25*60
# Default duration of break Interval
breakDuration = 2*60
# Default duration of idle time
idleThreshold = 5*60
threads = 0
startButton = True
absoluteAlertTime = 0
absoluteBreakTime = 0
timer = 0
whatIsHappening = "nothing"

# This variable will be useful when we will create the executable file of this application
base_path = getattr(sys, '_MEIPASS', '.')+'/'


def getIdleTime():
    '''
    This function will continuouly return the
    idleTime of the system if evalutes the idle time by
    substracting the LastInput time of the system from the
    total time from which the system is started it uses
    the win32api to achieve this
    '''
    return (GetTickCount() - GetLastInputInfo()) // 1000


n = ToastNotifier()


def eyeNotify():
    '''
      This function will remind the user
      to take a break for given minutes
      and getting back to work after the time is passed
    '''
    idleTime = getIdleTime()
    if idleTime < idleThreshold:
        n.show_toast(
            title="eyeCare Time !",
            msg="Time to take your eyes off the screen for " +
                (str(breakDuration/60) if breakDuration != 0 else "few") + " minutes",
            duration=5,
            icon_path=base_path + "logo.ico",
            threaded=True,
        )

        global absoluteBreakTime, whatIsHappening
        absoluteBreakTime = datetime.datetime.now(
        ) + datetime.timedelta(seconds=breakDuration)

        whatIsHappening = "breakTimerCountDown"

        time.sleep(breakDuration)

        if breakDuration != 0:
            n.show_toast(
                "Back to Work !",
                "You can get back to work now",
                duration=5,
                icon_path=base_path + "logo.ico",
                threaded=True
            )
        global timer
        whatIsHappening = "timerCountDown"
        timer = timerStart()
        activityCheck()
    else:
        timer.cancel() # type: ignore
        waitingForReset()


def timerStart():
    '''
        This function will restart the
        countdown after every break
    '''
    global timer, absoluteAlertTime
    timer = threading.Timer(promptInterval, eyeNotify)
    timer.start()
    absoluteAlertTime = datetime.datetime.now(
    ) + datetime.timedelta(seconds=promptInterval)
    return timer


def activityCheck():
    '''
    This function will check
    whether the user is interacting with the
    system or not
    '''
    global stopThread
    global threads
    while 1:

        time.sleep(idleThreshold)

        idleTime = getIdleTime()
        if idleTime >= idleThreshold:
            timer.cancel() # type: ignore

            waitingForReset()


def waitingForReset():
    '''
    This function will reset the countdown
    if the idleTime will cross the idleTimeThreshhold
    '''
    global whatIsHappening
    whatIsHappening = "standbyMode"

    while 1:
        time.sleep(1)
        idleTime = getIdleTime()

        if idleTime < 1:
            global timer
            timer.cancel() # type: ignore
            timer = timerStart()

            whatIsHappening = "timerCountDown"
            activityCheck()

# GUI Representation


def timerDisplay():
    '''
    This function will display the
    countdown for you
    '''
    while 1:
        timeRemaining = absoluteAlertTime - datetime.datetime.now() # type: ignore

        if timeRemaining.days >= 0 and whatIsHappening == "timerCountDown":

            canvas.itemconfig(standbyPage, state='hidden')
            canvas.itemconfig(breakTimeRemainingText, state='hidden')
            canvas.itemconfig(hh, state='normal')
            canvas.itemconfig(mm, state='normal')
            canvas.itemconfig(ss, state='normal')
            canvas.itemconfig(background1, state='normal')
            canvas.itemconfig(timeRemainingText, state='normal')

            timeRemaining = timeRemaining.seconds

            minute, second = (timeRemaining // 60, timeRemaining % 60)
            hour = 0
            if minute > 60:
                hour, minute = (minute // 60, minute % 60)

            canvas.itemconfig(hh, text=hour)
            canvas.itemconfig(mm, text=minute)
            canvas.itemconfig(ss, text=second)

            window.update()

            time.sleep(1)
        elif whatIsHappening == "breakTimerCountDown":

            canvas.itemconfig(standbyPage, state='hidden')
            canvas.itemconfig(timeRemainingText, state='hidden')
            canvas.itemconfig(hh, state='normal')
            canvas.itemconfig(mm, state='normal')
            canvas.itemconfig(ss, state='normal')
            canvas.itemconfig(background1, state='normal')
            canvas.itemconfig(breakTimeRemainingText, state='normal')

            breakTimeRemaining = (absoluteBreakTime -
                                  datetime.datetime.now()).seconds # type: ignore

            minute, second = (breakTimeRemaining // 60,
                              breakTimeRemaining % 60)
            hour = 0
            if minute > 60:
                hour, minute = (minute // 60, minute % 60)

            canvas.itemconfig(hh, text=hour)
            canvas.itemconfig(mm, text=minute)
            canvas.itemconfig(ss, text=second)

            window.update()

            time.sleep(1)

        elif whatIsHappening == "standbyMode":
            canvas.itemconfig(hh, state='hidden')
            canvas.itemconfig(mm, state='hidden')
            canvas.itemconfig(ss, state='hidden')
            canvas.itemconfig(background1, state='hidden')
            canvas.itemconfig(timeRemainingText, state='hidden')
            canvas.itemconfig(breakTimeRemainingText, state='hidden')
            canvas.itemconfig(standbyPage, state='normal')

            time.sleep(1)
        else:
            time.sleep(1)


def clickingTheStartButton():
    '''
      This function will begin the countdown
      when we click the start button of the
      application .
    '''
    global startButton
    global promptInterval, breakDuration, idleThreshold

    if startButton == True:

        promptInterval = float(entry0.get())*60
        breakDuration = float(entry1.get())*60
        idleThreshold = float(entry2.get())*60

        if idleThreshold > 0.1 and promptInterval > 5:
            startButton = False
            b0.configure(image=img2)

            threadAtTheBackground()

            n.show_toast(
                title="Your eyeCare Timer Set",
                msg="Your eyeCare timer is set \n You can close the program now and access it later in the system tray",
                duration=5,
                icon_path=base_path + "logo.ico",
                threaded=True,
            )

            canvas.itemconfig(background, state='hidden')
            canvas.itemconfig(entry0_bg, state='hidden')
            canvas.itemconfig(entry1_bg, state='hidden')
            canvas.itemconfig(entry2_bg, state='hidden')
            entry0.destroy()
            entry1.destroy()
            entry2.destroy()

            canvas.itemconfig(background1, state='normal')
            canvas.itemconfig(hh, state='normal')
            canvas.itemconfig(mm, state='normal')
            canvas.itemconfig(ss, state='normal')
            canvas.itemconfig(timeRemainingText, state='normal')

            global whatIsHappening
            whatIsHappening = "timerCountDown"
            threading.Thread(target=timerDisplay, daemon=True).start()
    else:
        window.destroy()


# Creating the main interface by the Tkinter GUI
window = Tk()

window.wm_title("Smart visCare")
window.iconbitmap(base_path + "logo.ico")

window.geometry("703x500")
window.configure(bg="#ffffff")
canvas = Canvas(
    window,
    bg="#ffffff",
    height=500,
    width=703,
    bd=0,
    highlightthickness=0,
    relief="ridge")
canvas.place(x=0, y=0)

entry0_img = PhotoImage(file=base_path + "imageOfTextBox.png")
entry0_bg = canvas.create_image(
    458.5, 190.0,
    image=entry0_img)

entry0 = Entry(
    bd=0,
    bg="#1983c0",
    highlightthickness=0,
    fg="#ffffff",
    font="Montserrat 22 bold")

entry0.place(
    x=434.7890625, y=170,
    width=57.421875,
    height=38)

entry0.insert(END, '25')

entry1_img = PhotoImage(file=base_path + "imageOfTextBox.png")
entry1_bg = canvas.create_image(
    458.5, 266.0,
    image=entry1_img)

entry1 = Entry(
    bd=0,
    bg="#1983c0",
    highlightthickness=0,
    fg="#ffffff",
    font="Montserrat 22 bold")

entry1.place(
    x=434.7890625, y=246,
    width=57.421875,
    height=38)

entry1.insert(END, '2')

entry2_img = PhotoImage(file=base_path + "imageOfTextBox.png")
entry2_bg = canvas.create_image(
    458.5, 341.0,
    image=entry2_img)

entry2 = Entry(
    bd=0,
    bg="#1983c0",
    highlightthickness=0,
    fg="#ffffff",
    font="Montserrat 22 bold")

entry2.place(
    x=434.7890625, y=321,
    width=57.421875,
    height=38)

entry2.insert(END, '5')

img2 = PhotoImage(file=base_path + "image2.png")
img0 = PhotoImage(file=base_path + "image0.png")
b0 = Button(
    image=img0,
    borderwidth=0,
    highlightthickness=0,
    command=clickingTheStartButton,
    relief="flat")

b0.place(
    x=291, y=415,
    width=121,
    height=42)

# First Window

background_img = PhotoImage(file=base_path + "firstBackground.png")
background = canvas.create_image(
    316.0, 175.0,
    image=background_img)


# Second Window
background_img1 = PhotoImage(file=base_path + "secondBackground.png")
background1 = canvas.create_image(
    293.5, 175.0,
    image=background_img1)
canvas.itemconfig(background1, state='hidden')

timeRemainingText = canvas.create_text(
    360, 233.5,
    text="Time remaining :",
    fill="#2f423f",
    font=("Montserrat-SemiBold", int(24.0)))
canvas.itemconfig(timeRemainingText, state='hidden')

breakTimeRemainingText = canvas.create_text(
    365.0, 233.5,
    text="Break time remaining :",
    fill="#2f423f",
    font=("Montserrat-SemiBold", int(24.0)))
canvas.itemconfig(breakTimeRemainingText, state='hidden')

hh = canvas.create_text(
    250.0, 290.5,
    text="60",
    fill="#2f423f",
    font=("Montserrat-SemiBold", int(48.0)))
canvas.itemconfig(hh, state='hidden')

mm = canvas.create_text(
    352.0, 290.5,
    text="60",
    fill="#2f423f",
    font=("Montserrat-SemiBold", int(48.0)))
canvas.itemconfig(mm, state='hidden')

ss = canvas.create_text(
    453.0, 290.5,
    text="60",
    fill="#2f423f",
    font=("Montserrat-SemiBold", int(48.0)))
canvas.itemconfig(ss, state='hidden')


# Third Window(Stand By Mode )
standby_img = PhotoImage(file=base_path + "standByBackground.png")
standbyPage = canvas.create_image(
    301.5, 180.0,
    image=standby_img)
canvas.itemconfig(standbyPage, state='hidden')


# Showing the icon in the systemtray
def quit_window(icon, item):
    icon.stop()
    window.destroy()


def show_window(icon, item):
    icon.stop()
    window.after(0, window.deiconify)

    global whatIsHappening
    timeRemaining = absoluteAlertTime - datetime.datetime.now() # type: ignore
    whatIsHappening = ("timerCountDown" if timeRemaining.days >=
                       0 else "breakTimerCountDown")


def withdraw_window():
    window.withdraw()
    iconImage = Image.open(base_path + "logo.ico")
    app_menu = pystray.Menu(MenuItem('Quit', quit_window),
                            MenuItem('Show', show_window))
    global icon
    icon = pystray.Icon(name="Smart visCare", icon=iconImage,
                        title="Smart visCare", menu=app_menu)
    icon.run()


window.protocol('WM_DELETE_WINDOW', withdraw_window)

window.resizable(False, False)
window.mainloop()
