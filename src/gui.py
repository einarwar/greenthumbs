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

device_handles = {  "WATERING_TIME": 0x000b,
                    "MEASURING_INTERVAL": 0x000d,
                    "THRESH_LOW": 0x000f,
                    "THRESH_HIGH": 0x0011,
                    "NEW_DATA": 0x000b,
                    "WATER_NOW_FLAG": 0x0015,
                    "MEASURE_NOW_FLAG": 0x0017,
                    "NEW_DATA_FLAG": 0x000d
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
                    self.GUI.data_flag_stringvar.set("1");
                    print("New data found!\n")
                    data = self.GUI.devices[0].read(device_handles["NEW_DATA"])
                    try:
                        int_data = int(data)
                        print int_data
                        print("Data is a number, writing to file...\n")
                        write_data_to_textfile(int(int_data))
                    except:
                        print("Data is not number, it is: {}".format(data))
                    self.GUI.data_flag_stringvar.set("0")
                    self.GUI.devices[0].write(device_handles["NEW_DATA_FLAG"], "0")
                    print("Done")
                    time.sleep(2)
            except Exception as e:
                print("Exception: {}".format(e))
                try:
                    self.GUI.devices[0].reader.disconnect()
                    self.GUI.devices[0].reader.connect()
                except:
                    self.doRun = False
class GUI:
    def __init__(self, master, reset_data=True):
        if reset_data:
            with open("sampleText.txt", 'w') as f:
                pass

        self.master = master
        #Discover BTLE devices
        self.devices = discover_btle_devices()


        #Set GUI title
        master.title("Greenthumbs")
        master.configure(background='green')

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
        self.buttons.configure(background='green')

        self.close_button = Tkinter.Button(self.buttons, text="Close", command=self.quit)
        self.close_button.grid(row=0, column = 0)

        self.measure_button = Tkinter.Button(self.buttons, text="Measure now", command=self.measure)
        self.measure_button.grid(row=0, column=1)

        self.water_button = Tkinter.Button(self.buttons, text="Water now", command=self.water)
        self.water_button.grid(row=0, column = 2)

    def setup_parameter_sidebar(self):
        self.parameter_sidebar = Tkinter.LabelFrame(self.master, text="Set parameters", padx=5, pady=5)
        self.parameter_sidebar.grid(row=0, column = 0)

        self.text_watering_time = Tkinter.Label(self.parameter_sidebar, text=("Watering duration (ms)"))
        self.text_watering_time.grid(row=0, column=0)

        self.watering_time_stringvar = Tkinter.StringVar()
        self.parameter_watering_time = Tkinter.Entry(self.parameter_sidebar, textvar=self.watering_time_stringvar)
        self.parameter_watering_time.grid(row=0, column=1)

        self.text_measuring_interval = Tkinter.Label(self.parameter_sidebar, text="Measuring interval (seconds)")
        self.text_measuring_interval.grid(row=1, column=0)

        self.measuring_interval_stringvar = Tkinter.StringVar()
        self.parameter_measuring_interval = Tkinter.Entry(self.parameter_sidebar, textvar=self.measuring_interval_stringvar)
        self.parameter_measuring_interval.grid(row=1,column=1)

        self.text_thresh_low = Tkinter.Label(self.parameter_sidebar, text="Low threshold")
        self.text_thresh_low.grid(row=2,column=0)

        self.thresh_low_stringvar = Tkinter.StringVar()
        self.parameter_thresh_low = Tkinter.Entry(self.parameter_sidebar, textvar=self.thresh_low_stringvar)
        self.parameter_thresh_low.grid(row=2,column=1)

        self.text_thresh_high = Tkinter.Label(self.parameter_sidebar, text="High threshold")
        self.text_thresh_high.grid(row=3,column=0)

        self.thresh_high_stringvar = Tkinter.StringVar()
        self.parameter_thresh_high = Tkinter.Entry(self.parameter_sidebar, textvar=self.thresh_high_stringvar)
        self.parameter_thresh_high.grid(row=3,column=1)

        self.data_flag_stringvar = Tkinter.StringVar()
        self.parameter_data_flag = Tkinter.Entry(self.parameter_sidebar, textvar=self.data_flag_stringvar)
        self.parameter_data_flag.grid(row=5,column=0)

        self.data_stringvar = Tkinter.StringVar()
        self.parameter_data = Tkinter.Entry(self.parameter_sidebar, textvar=self.data_stringvar)
        self.parameter_data.grid(row=5,column=1)


        #self.refresh_parameters_from_device()

        #self.refresh_button = Tkinter.Button(self.parameter_sidebar, text="Refresh", command=self.refresh_parameters_from_device)
        #self.refresh_button.grid(row=4,column=0)
        #self.apply_button = Tkinter.Button(self.parameter_sidebar, text="Apply", command=self.apply_parameters_to_device)
        #self.apply_button.grid(row=4, column=1)



    def setup_graph(self):
        self.graph = Tkinter.LabelFrame(self.master, text="Measurement data", padx=5, pady=5)
        self.graph.grid(row=0,column=1)
        self.graph.configure(background='green')
        self.f = Figure(figsize=(5,4),dpi=100)
        self.a1 = self.f.add_subplot(111)
        self.a1.set_ylim([0,1024])
        canvas = FigureCanvasTkAgg(self.f,self.graph)
        canvas.show()
        canvas.get_tk_widget().pack(expand=True)

        self.last_measurement_stringvar = Tkinter.StringVar()
        self.last_measurement_stringvar.set("Last measurement: A second ago")
        self.text_last_measurement = Tkinter.Label(self.graph, textvar=self.last_measurement_stringvar)
        self.text_last_measurement.pack()

    def refresh_parameters_from_device(self):
        #Read handle values from device characteristics
        self.thresh_high_stringvar.set(self.devices[0].read(device_handles["THRESH_HIGH"]))
        self.thresh_low_stringvar.set(self.devices[0].read(device_handles["THRESH_LOW"]))
        self.measuring_interval_stringvar.set(self.devices[0].read(device_handles["MEASURING_INTERVAL"]))
        self.watering_time_stringvar.set(self.devices[0].read(device_handles["WATERING_TIME"]))
        self.data_flag_stringvar.set(self.devices[0].read(device_handles["NEW_DATA_FLAG"]))
        self.data_stringvar.set(self.devices[0].read(device_handles["NEW_DATA"]))
        print("Parameters refreshed")

    def apply_parameters_to_device(self):
        self.devices[0].write(device_handles["THRESH_HIGH"], self.thresh_high_stringvar.get())
        self.devices[0].write(device_handles["THRESH_LOW"], self.thresh_low_stringvar.get())
        self.devices[0].write(device_handles["MEASURING_INTERVAL"], self.measuring_interval_stringvar.get())
        self.devices[0].write(device_handles["WATERING_TIME"], self.watering_time_stringvar.get())
        self.devices[0].write(device_handles["NEW_DATA_FLAG"], self.data_flag_stringvar.get())
        self.devices[0].write(device_handles["NEW_DATA"], self.data_stringvar.get())
        print("Parameters updated")

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
    my_gui.a1.clear
    my_gui.a1.axhline(y=300,linewidth=1, ls='dotted', color='r')

    my_gui.a1.plot(xar,yar,'g-')


root = Tkinter.Tk()
my_gui = GUI(root)
ani = animation.FuncAnimation(my_gui.f, animate, interval=1000)
root.mainloop()
