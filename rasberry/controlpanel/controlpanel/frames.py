# -*- coding: utf-8 -*-
import time
from datetime import datetime
from tkinter import Frame, StringVar, CENTER, Label, Tk, PhotoImage, Button, E, W

from loguru import logger

class MainApp(Tk):
    def __init__(self, updater_subject):
        Tk.__init__(self)

        self.left_img = PhotoImage(
            file='images/left_white.png')
        self.right_img = PhotoImage(
            file='images/right_white.png')

        self.active_frame = -1
        self.config(bg="#333")

        Button(self, bg="#333", fg="#333", activebackground='#333', image=self.left_img, highlightthickness=0, bd=0,
               command=lambda: self.next_frame(False)).pack(side="left", fill="y", padx=10)

        Button(self, bg="#333", fg="#333", activebackground='#333', image=self.right_img,  highlightthickness=0, bd=0,
               command=lambda: self.next_frame(True)).pack(side="right", fill="y", padx=10)

        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = []

        for F in [Frame1, WeatherFrame, IsItFridayFrame]: #, HouseMapFrame]:
            page_name = F.__name__
            frame = F(parent=container, updater_subject=updater_subject)
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
    def __init__(self, parent, updater_subject):
        Frame.__init__(self, parent)
        self.updater_subject = updater_subject

    def on_show(self):
        pass


class Frame1(ControlPanelFrame):
    def __init__(self, parent, updater_subject):
        ControlPanelFrame.__init__(self, parent, updater_subject)
        self.initUI()
        #self.mq_thread = MqttUpdater(self.the_queue)
        #self.mq_thread.start()
        #self.refresh_data()
        self.time = None
        self.tick()
        self.updater_subject.subscribe(lambda x: self.refresh_data(x))

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
        self.clockValue = StringVar()
        self.clockValue.set('---')
        self.clock_label = Label(self, textvariable=self.clockValue, bg="#333", fg="#fff", font=("Courier", 80, "bold"))
        self.clock_label.place(relx=0.5, rely=0.1, anchor=CENTER)

        self.powerValue = StringVar()
        self.powerValue.set('---')
        power_label = Label(self, textvariable=self.powerValue, bg="#333", fg="#fff", font=("Courier", 100, "bold"))
        power_label.place(relx=0.5, rely=0.4, anchor=CENTER)

        self.tempValue = StringVar()
        self.tempValue.set('---')
        temp_label = Label(self, textvariable=self.tempValue, bg="#333", fg="#fff", font=("Courier", 100, "bold"))
        temp_label.place(relx=0.5, rely=0.7, anchor=CENTER)

    def refresh_data(self, data):
        """
        """
        try:
            key, data = data
            if key == 'power':
                self.powerValue.set(data)
            if key == 'temp':
                self.tempValue.set(data)
        except:
            pass


class WeatherFrame(ControlPanelFrame):
    def __init__(self, parent, updater_subject):
        ControlPanelFrame.__init__(self, parent, updater_subject)
        self.data = []
        self.initUI()
        self.updater_subject.subscribe(lambda x: self.refresh_data(x))

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
    def __init__(self, parent, updater_subject):
        ControlPanelFrame.__init__(self, parent, updater_subject)
        self.fredag = StringVar()
        self.fredag.set("Är det fredag?")
        self.initUI()

    def initUI(self):
        self.config(bg="#333")

        # Frames to display data from the asyncio tasks
        font = ("Courier", 50, "bold")

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