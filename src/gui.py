import Tkinter
import numpy as np
import threading, time
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")
import matplotlib.animation as animation
from matplotlib import style
style.use('ggplot')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

from collections import deque
from PIL import Image, ImageTk
from bt import Device, discover_btle_devices
from numbers import Number

device_handles = {  "NEW_DATA": 0x000b,
                    "NEW_DATA_FLAG": 0x000d,
                    "THRESH_LOW": 0x000f,
                    "MEASURING_INTERVAL": 0x0011,
                    "WATERING_TIME": 0x0013,
                    }


def write_data_to_textfile(data, filename="sampleText.txt"):
    with open(filename, 'a+') as f:
        f.write((str(data) + '\n'))



class Reciever_thread(threading.Thread):
    def __init__(self, GUI):
        threading.Thread.__init__(self)
        self.GUI = GUI
        self.doRun = True

    def run(self):
        while self.doRun:
            try:
                got_new_data = self.GUI.devices[0].read(device_handles["NEW_DATA_FLAG"])
                if int(got_new_data):

                    self.GUI.last_measurement_stringvar.set(("Last measurement: " + time.ctime()))
                    data = self.GUI.devices[0].read(device_handles["NEW_DATA"])
                    try:
                        int_data = int(data)
                        write_data_to_textfile(int(int_data))
                    except:
                        print("Data is not number, it is: {}".format(data))
                    self.GUI.devices[0].write(device_handles["NEW_DATA_FLAG"], "0")
                    time.sleep(2)
            except Exception as e:
                print("Exception: {}".format(e))
                try:
                    self.GUI.devices[0].reader.disconnect()
                    self.GUI.devices[0].reader.connect()
                except:
                    self.doRun = False
class GUI:
    def __init__(self, master, reset_data=False):
        if reset_data:
            with open("sampleText.txt", 'w') as f:
                pass

        self.master = master
        #Discover BTLE devices
        self.devices = discover_btle_devices()

        #Get parameters from devices
        self.get_watering_threshold()
        self.get_watering_time()
        self.get_measuring_interval()

        #Set GUI title
        master.title("Greenthumbs")
        master.configure(background='gray')

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
        #Set up buttons
        self.setup_buttons()

        self.thread = Reciever_thread(self)
        self.thread.start()

    def quit(self):
        self.thread.doRun = False
        self.master.destroy()

    def water(self):
        self.devices[0].write(device_handles["WATER_NOW_FLAG"], "1")
        print("Watering plant command sent")

    def measure(self):
        self.devices[0].write(device_handles["MEASURE_NOW_FLAG"], "1")
        print("Measure command sent")

    def setup_buttons(self):
        self.buttons = Tkinter.LabelFrame(self.master)
        self.buttons.grid(row=1,column=0)

        self.close_button = Tkinter.Button(self.buttons, text="Close", command=self.quit)
        self.close_button.grid(row=0, column = 0)

        self.measure_button = Tkinter.Button(self.buttons, text="Measure now", command=self.measure)
        self.measure_button.grid(row=0, column=1)

        self.water_button = Tkinter.Button(self.buttons, text="Water now", command=self.water)
        self.water_button.grid(row=0, column = 2)

    def setup_parameter_sidebar(self):
        self.parameter_sidebar = Tkinter.LabelFrame(self.master, text="Device parameters", padx=5, pady=5)
        self.parameter_sidebar.grid(row=0, column = 0)

        self.text_watering_time = Tkinter.Label(self.parameter_sidebar, text=("Watering duration (ms)"))
        self.text_watering_time.grid(row=0, column=0)

        self.watering_time_stringvar = Tkinter.StringVar()
        self.watering_time_stringvar.set(self.WATERING_TIME)
        self.parameter_watering_time = Tkinter.Label(self.parameter_sidebar, textvar=self.watering_time_stringvar)
        self.parameter_watering_time.grid(row=0, column=1)

        self.text_measuring_interval = Tkinter.Label(self.parameter_sidebar, text="Measuring interval (seconds)")
        self.text_measuring_interval.grid(row=1, column=0)

        self.measuring_interval_stringvar = Tkinter.StringVar()
        self.measuring_interval_stringvar.set(self.MEASURING_INTERVAL)
        self.parameter_measuring_interval = Tkinter.Label(self.parameter_sidebar, textvar=self.measuring_interval_stringvar)
        self.parameter_measuring_interval.grid(row=1,column=1)

        self.text_thresh_low = Tkinter.Label(self.parameter_sidebar, text="Watering threshold:")
        self.text_thresh_low.grid(row=2,column=0)

        self.thresh_low_stringvar = Tkinter.StringVar()
        self.thresh_low_stringvar.set(self.THRESH_LOW)
        self.parameter_thresh_low = Tkinter.Label(self.parameter_sidebar, textvar=self.thresh_low_stringvar)
        self.parameter_thresh_low.grid(row=2,column=1)


    def get_watering_threshold(self):
        self.THRESH_LOW = self.devices[0].read(device_handles["THRESH_LOW"])

    def get_measuring_interval(self):
        self.MEASURING_INTERVAL = self.devices[0].read(device_handles["MEASURING_INTERVAL"])

    def get_watering_time(self):
        self.WATERING_TIME = self.devices[0].read(device_handles["WATERING_TIME"])


    def setup_graph(self):
        self.graph = Tkinter.LabelFrame(self.master, text="Measurement data", padx=5, pady=5)
        self.graph.grid(row=0,column=1)
        self.graph.configure(background='gray')
        self.f = Figure(figsize=(5,4),dpi=100)
        self.a1 = self.f.add_subplot(111)
        self.a1.set_ylim([0,1024])
        self.xlim_low = 0
        self.xlim_hi = 10
        #self.a1.set_xlim([self.xlim_low,self.xlim_hi])
        canvas = FigureCanvasTkAgg(self.f,self.graph)
        canvas.show()
        canvas.get_tk_widget().pack(expand=True)

        self.last_measurement_stringvar = Tkinter.StringVar()
        self.last_measurement_stringvar.set("Last measurement: A second ago")
        self.text_last_measurement = Tkinter.Label(self.graph, textvar=self.last_measurement_stringvar)
        self.text_last_measurement.pack()


    def update_graph_with_data(self):
        write_data_to_textfile(self.devices[0].read(device_handles["NEW_DATA"]))

def animate(i):
    pullData = open('sampleText.txt','r').read()
    dataArray = pullData.split('\n')
    xar = []
    yar = []
    x = 0
    for y in dataArray:
        if len(y) >= 1:
            xar.append(int(x))
            yar.append(int(y))
            x += 1
            #if x % 10 == 0 and x > 1:
            #    my_gui.xlim_low += 10
            #    my_gui.xlim_hi += 10
    my_gui.a1.clear
    my_gui.a1.axhline(y=my_gui.THRESH_LOW,linewidth=1, ls='dotted', color='r')
    #my_gui.a1.set_xlim([my_gui.xlim_low, my_gui.xlim_hi])
    my_gui.a1.plot(xar,yar,'g-')


root = Tkinter.Tk()
my_gui = GUI(root)
ani = animation.FuncAnimation(my_gui.f, animate, interval=1000)
root.mainloop()
