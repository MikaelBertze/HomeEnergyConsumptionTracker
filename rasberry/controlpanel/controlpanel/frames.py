# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta
from tkinter import Frame, StringVar, CENTER, Label, Tk, PhotoImage, Button, E, W, N, S, NE, NW, Canvas
from loguru import logger
from multiprocessing import Process
from controlpanel import sound_player

class MainApp(Tk):
    def __init__(self, updater):
        Tk.__init__(self)

        self.left_img = PhotoImage(
            file='images/left_white.png')
        self.right_img = PhotoImage(
            file='images/right_white.png')

        self.active_frame = -1
        self.config(bg="#333")

        Button(self, bg="#333", fg="#333", activebackground='#333', image=self.left_img, highlightthickness=0, bd=0,
               padx=50,
               command=lambda: self.next_frame(False)).pack(side="left", fill="y")

        Button(self, bg="#333", fg="#333", activebackground='#333', image=self.right_img,  highlightthickness=0, bd=0,
               padx=50,
               command=lambda: self.next_frame(True)).pack(side="right", fill="y")

        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = []

        for F in [Frame1, TimersFrame, WeatherFrame, IsItFridayFrame]: #, SensorsFrame]: #, HouseMapFrame]:
            page_name = F.__name__
            frame = F(parent=container, updater=updater)
            self.frames.append(frame)

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.next_frame(True) #show_frame("Frame1")

    def next_frame(self, forward):
        self.active_frame += 1 if forward else -1
        self.active_frame %= len(self.frames)

        logger.info("Frame switch: " + str(self.active_frame))

        F = self.frames[self.active_frame]
        F.on_show()
        F.tkraise()



    def show_frame(self, page_name):
        """Show a frame for the given page name"""

        frame = self.frames[page_name]
        frame.on_show()
        frame.tkraise()


class ControlPanelFrame(Frame):
    def __init__(self, parent, updater):
        Frame.__init__(self, parent)
        self.updater = updater

    def on_show(self):
        pass


class Frame1(ControlPanelFrame):
    def __init__(self, parent, updater):
        ControlPanelFrame.__init__(self, parent, updater)
        self.initUI()
        #self.mq_thread = MqttUpdater(self.the_queue)
        #self.mq_thread.start()
        #self.refresh_data()
        self.time = None
        self.tick()
        self.updater.power_updater.whenPowerReported.subscribe(
            lambda x: self.power_report(x))
        self.updater.temp_updater.whenTemperatureReported.subscribe(
            lambda x: self.tempValue.set("{:.1f}°C".format(x)))
        self.updater.power_updater.whenHourUsageReported.subscribe(
            lambda x: self.curHourValue.set("{:.2f}kWh".format(x)))
        self.updater.power_updater.whenNoPowerReported.subscribe(
            lambda x: self.no_reporting())

    def no_reporting(self):
        self.powerValue.set("????")
        self.myCanvas.itemconfig(self.oval, fill="red")

    def power_report(self, x):
        self.powerValue.set("{:.0f}W".format(x))
        self.myCanvas.itemconfig(self.oval, fill="green")

    def tick(self):
        # get the current local time from the PC
        time_now = time.strftime('%H:%M:%S')
        # if time string has changed, update it
        if time_now != self.time:
            self.time = time_now
            self.clockValue.set(time_now)
        # calls itself every 200 milliseconds
        # to update the time display as needed
        # could use >200 ms, but display gets jerky
        self.clock_label.after(100, self.tick)

    def initUI(self):
        self.config(bg="#333")

        self.myCanvas = Canvas(self, width=20, height=20, bg="#333", bd=0, highlightthickness=0)
        self.oval = self.myCanvas.create_oval(0, 0, 20, 20, fill="yellow")
        self.myCanvas.place(relx=1, rely=0.05, anchor=NE)

        self.clockValue = StringVar()
        self.clockValue.set('---')
        self.clock_label = Label(self, textvariable=self.clockValue, bg="#333", fg="#fff", font=("Courier", 60, "bold"))
        self.clock_label.place(relx=0.5, rely=0.1, anchor=CENTER)

        self.powerValue = StringVar()
        self.powerValue.set('---')
        power_label = Label(self, textvariable=self.powerValue, bg="#333", fg="#fff", font=("Courier", 90, "bold"))
        power_label.place(relx=0.5, rely=0.35, anchor=CENTER)

        self.curHourValue = StringVar()
        self.curHourValue.set('---')
        curHour_label = Label(self, textvariable=self.curHourValue, bg="#333", fg="#fff", font=("Courier", 60, "bold"))
        curHour_label.place(relx=0.5, rely=0.55, anchor=CENTER)

        self.tempValue = StringVar()
        self.tempValue.set('---')
        temp_label = Label(self, textvariable=self.tempValue, bg="#333", fg="#fff", font=("Courier", 90, "bold"))
        temp_label.place(relx=0.5, rely=0.85, anchor=CENTER)


class WeatherFrame(ControlPanelFrame):
    def __init__(self, parent, updater):
        ControlPanelFrame.__init__(self, parent, updater)
        self.data = []
        self.initUI()
        updater.weather_updater.when_weather_updated.subscribe(lambda x: self.refresh_data(x))

    def on_show(self):
        pass

    def refresh_data(self, data):
        """
        """
        try:
            # refresh the GUI with new data from the queue

            key, data = data
            if key == "weather":
                t, data = data
                if len(data) == 3:
                    for i in range(3):
                        if len(data[i]) == 3:
                            for j in range(3):
                                self.data[i][j].set(data[i][j])
                    self.update_time.set(t.strftime("%Y-%m-%d %H:%M"))
        except:
            pass

    def initUI(self):
        self.config(bg="#333")

        # Frames to display data from the asyncio tasks
        font = ("Courier", 40, "bold")

        header1 = Label(self, text="Dag", bg="#333", fg="#fff", font=font)
        header2 = Label(self, text="Hög", bg="#333", fg="#fff", font=font)
        header3 = Label(self, text="Låg", bg="#333", fg="#fff", font=font)
        header1.place(relx=0.02, rely=0.1, anchor=W)
        header2.place(relx=0.4, rely=0.1, anchor=W)
        header3.place(relx=0.7, rely=0.1, anchor=W)

        for i in range(3):
            self.data.append([])
            y = .25 + i * .2
            for j in range(3):
                x = [.02, .4, .7][j]
                s = StringVar()
                s.set('-')
                Label(self, textvariable=s, bg="#333", fg="#fff", font=font).place(relx=x, rely=y, anchor=W)
                self.data[i].append(s)

        self.update_time = StringVar()
        self.update_time.set('---- -- -- --:--')
        Label(self, textvariable=self.update_time, bg="#333", fg="#fff", font=("Courier", 10, "bold"))\
            .place(relx=.9, rely=.95, anchor=E)


class IsItFridayFrame(ControlPanelFrame):
    def __init__(self, parent, updater):
        ControlPanelFrame.__init__(self, parent, updater)
        self.fredag = StringVar()
        self.fredag.set("Är det fredag?")
        self.initUI()

    def initUI(self):
        self.config(bg="#333")

        # Frames to display data from the asyncio tasks
        font = ("Courier", 30, "bold")

        header = Label(self, textvariable=self.fredag, bg="#333", fg="#fff", font=font)
        header.place(relx=0.5, rely=0.5, anchor=CENTER)

    def visa_svar(self):
        veckodag = datetime.today().weekday()
        if veckodag == 4:
            self.fredag.set("Ja! :-)")
        else:
            self.fredag.set("Nej :-(")

    def on_show(self):
        self.fredag.set("Är det fredag?")
        self.after(5 * 1000, self.visa_svar)  # called only once!


class SensorsFrame(ControlPanelFrame):
    def __init__(self, parent, updater):
        ControlPanelFrame.__init__(self, parent, updater)
        self.initUI()
        #updater.subscribe(lambda x: self.update(x))

    def initUI(self):
        self.config(bg="#333")

        font1 = ("Courier", 30, "bold")
        font2 = ("Courier", 20, "bold")

        #header = Label(self, textvariable=self.fredag, bg="#333", fg="#fff", font=font)
        #header.place(relx=0.5, rely=0.5, anchor=CENTER)

    def update(self, message):
        pass

class TimerWidget(Frame):

    font1 = ("Courier", 40, "bold")

    def __init__(self, parent, name, run_name, minutes, seconds):
        Frame.__init__(self, parent)
        self.config(bg="#333")

        self.start_time = None
        self.alarm_process: Process = None
        self.name = name
        self.run_name = run_name
        self.minutes = minutes
        self.seconds = seconds
        self.mode = "reset"
        self.text = StringVar()
        self.alarm_toggle = False
        self.button = Button(self,
                             textvariable=self.text,
                             bg="#333",
                             fg="#fff",
                             activebackground='#333',
                             activeforeground='#fff',
                             font=TimerWidget.font1,
                             command=lambda: self.toggle(),
                             pady=30,
                             highlightthickness=0, bd=0)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.button.grid(column=0,row=0, sticky='nesw')

        self.reset()

    def reset(self):
        self.mode = "reset"
        #self.config(bg="#333")
        self.button.config(bg="#333", activebackground='#333')

        self.start_time = None
        self.text.set(f"{self.name} ({self.minutes:02}:{self.seconds:02})")

        if self.alarm_process != None and self.alarm_process.is_alive():
            self.alarm_process.kill()

    def start(self):
        self.mode = "running"
        self.start_time = time.time()
        self.tick()
        self.button.config(bg="#335", activebackground='#335')

    def toggle(self):
        logger.info("toggle")
        if self.mode == "reset":
            self.start()
        elif self.mode == "running":
            self.reset()


        logger.info(self.mode)

    def alarm(self):
        if self.mode == "running" and (self.alarm_process is None or not self.alarm_process.is_alive()):
            logger.info("Starting alarm sound")
            self.alarm_process = Process(target=sound_player.alarm)
            self.alarm_process.start()
            self.button.config(bg="#f33", activebackground='#f33')



    def tick(self):
        if self.mode == "reset":
            return
        # get the current local time from the PC
        timeleft = self.start_time + 60*self.minutes + self.seconds - time.time()

        if timeleft <= 0:
            self.alarm()

        minutes = int(timeleft/60)
        sec = int(timeleft - minutes * 60)
        self.text.set(f"{self.run_name} ({abs(minutes):02}:{abs(sec):02})")

        # calls itself every 200 milliseconds
        # to update the time display as needed
        # could use >200 ms, but display gets jerky
        self.after(200, self.tick)

class TimersFrame(ControlPanelFrame):
    def __init__(self, parent, updater):
        ControlPanelFrame.__init__(self, parent, updater)
        self.initUI()

    def initUI(self):
        self.config(bg="#333")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        TimerWidget(self, "Koka ägg", "Ägg", 6, 45).grid(column=0,row=0, sticky='nesw')
        TimerWidget(self, "Baka bröd", "Bakar", 10, 0).grid(column=0,row=1, sticky='nesw')
        TimerWidget(self, "Penne", "Penne", 11, 0).grid(column=0,row=2, sticky='nesw')
        TimerWidget(self, "Åsa", "Åsa", 45, 0).grid(column=0, row=3, sticky='nesw')

