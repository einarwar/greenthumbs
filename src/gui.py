import Tkinter
import numpy as np
import threading, time

from collections import deque
from PIL import Image, ImageTk
from bt import Device, discover_btle_devices

class Reciever_thread(threading.Thread):
    def __init__(self, GUI, n):
        threading.Thread.__init__(self)
        self.n = n
        self.GUI = GUI
        self.device = self.GUI.devices[self.n]
        self.doRun = True
    def run(self):
        while self.doRun:
            data = self.device.read()
            print("Thread{}Data from BLE is: {}".format(self.n,data))
            if data in self.GUI.device_dict:
                self.GUI.device_dict[data].killcount += 1
                self.GUI.device_dict[data].kills.set(self.GUI.device_dict[data].killcount)
                self.device.deathcount += 1
                self.device.deaths.set(self.device.deathcount)
                self.device.write("0")
                time_string = str(time.gmtime().tm_hour).zfill(2) + "." + str(time.gmtime().tm_min).zfill(2) + "." + str(time.gmtime().tm_sec).zfill(2)
                event_string = "{}: Player {} was shot by player {}".format(time_string, self.device.name_text, self.GUI.device_dict[data].name_text)
                self.GUI.add_event(event_string)
                self.GUI.update_event_sidebar()
            time.sleep(2)

class GUI:
    def __init__(self, master):
        self.master = master

        #Discover BTLE devices
        #self.device = Device()
        #self.devices = discover_btle_devices()
        #self.device_names = [dev.name_text for dev in self.devices]
        #self.n_devices = len(self.devices)

        #self.device_dict = dict([(d.name_text, d) for d in self.devices])

        #Start threads for each device to update scoretable
        #self.threads = [Reciever_thread(self, i) for (i,device) in enumerate(self.devices)]
        #for t in self.threads:
        #    t.start()



        #Set GUI title
        master.title("Greenthumbs")
        master.configure(background='grey')

        #Set up parameter_sidebar
        self.setup_parameter_sidebar()

        #Set up data graph
        self.setup_graph()


        #Set up AVR image
        #img = ImageTk.PhotoImage(Image.open("./avr.png"))
        #avr_logo = Tkinter.Label(self.master, image = img)
        #avr_logo.image = img
        #avr_logo.grid(row=0, sticky = Tkinter.NSEW)

        #Create close button
        self.close_button = Tkinter.Button(master, text="Close", command=self.quit)
        self.close_button.grid(row=1, column = 0)

    def quit(self):
        #for t in self.threads:
        #    t.doRun = False
        self.master.destroy()

    def setup_parameter_sidebar(self):
        self.parameter_sidebar = Tkinter.LabelFrame(self.master, text="Set parameters", padx=5, pady=5)
        self.parameter_sidebar.grid(row=0, column = 0)

        self.text_watering_time = Tkinter.Label(self.parameter_sidebar, text=("Watering duration (ms)"))
        self.text_watering_time.grid(row=0, column=0)

        self.watering_time_stringvar = Tkinter.StringVar()
        self.watering_time_stringvar.set("5000")
        self.parameter_watering_time = Tkinter.Entry(self.parameter_sidebar, textvar=self.watering_time_stringvar)
        self.parameter_watering_time.grid(row=0, column=1)

        self.text_measuring_interval = Tkinter.Label(self.parameter_sidebar, text="Measuring interval (seconds)")
        self.text_measuring_interval.grid(row=1, column=0)

        self.measuring_interval_stringvar = Tkinter.StringVar()
        self.measuring_interval_stringvar.set("3000")
        self.parameter_measuring_interval = Tkinter.Entry(self.parameter_sidebar, textvar=self.measuring_interval_stringvar)
        self.parameter_measuring_interval.grid(row=1,column=1)

        self.text_thresh_low = Tkinter.Label(self.parameter_sidebar, text="Low threshold")
        self.text_thresh_low.grid(row=2,column=0)

        self.thresh_low_stringvar = Tkinter.StringVar()
        self.thresh_low_stringvar.set("255")
        self.parameter_thresh_low = Tkinter.Entry(self.parameter_sidebar, textvar=self.thresh_low_stringvar)
        self.parameter_thresh_low.grid(row=2,column=1)

        self.text_thresh_high = Tkinter.Label(self.parameter_sidebar, text="High threshold")
        self.text_thresh_high.grid(row=3,column=0)

        self.thresh_high_stringvar = Tkinter.StringVar()
        self.thresh_high_stringvar.set("1500")
        self.parameter_thresh_high = Tkinter.Entry(self.parameter_sidebar, textvar=self.thresh_high_stringvar)
        self.parameter_thresh_high.grid(row=3,column=1)

    def setup_graph(self):
        pass

root = Tkinter.Tk()
my_gui = GUI(root)
root.mainloop()
