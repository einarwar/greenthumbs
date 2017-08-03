import Tkinter
import numpy as np
import threading, time
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.animation as animation
from matplotlib import style
style.use('ggplot')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

from collections import deque
from PIL import Image, ImageTk
from bt import Device, discover_btle_devices

class Reciever_thread(threading.Thread):
    def __init__(self, GUI):
        threading.Thread.__init__(self)
        self.GUI = GUI
        self.doRun = True
    def run(self):
        while self.doRun:
            #print("Watering duration is: {}".format(self.GUI.watering_time_stringvar.get()))
            #print("Measuring interval is : {}".format(self.GUI.measuring_interval_stringvar.get()))
            #print("Thresh_low is : {}".format(self.GUI.thresh_low_stringvar.get()))
            #print("Thresh_high is : {}".format(self.GUI.thresh_high_stringvar.get()))
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
        #Set up buttons
        self.setup_buttons()

        self.thread = Reciever_thread(self)
        self.thread.start()

    def quit(self):
        self.thread.doRun = False
        self.master.destroy()

    def setup_buttons(self):
        self.buttons = Tkinter.LabelFrame(self.master)
        self.buttons.grid(row=1,column=0)

        self.close_button = Tkinter.Button(self.buttons, text="Close", command=self.quit)
        self.close_button.grid(row=0, column = 0)

        self.measure_button = Tkinter.Button(self.buttons, text="Measure now")
        self.measure_button.grid(row=0, column=1)

        self.water_button = Tkinter.Button(self.buttons, text="Water now")
        self.water_button.grid(row=0, column = 2)

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

        self.refresh_button = Tkinter.Button(self.parameter_sidebar, text="Refresh", command=self.refresh_parameters_from_device)
        self.refresh_button.grid(row=4,column=0)
        self.apply_button = Tkinter.Button(self.parameter_sidebar, text="Apply", command=self.apply_parameters_to_device)
        self.apply_button.grid(row=4, column=1)

    def setup_graph(self):
        self.graph = Tkinter.LabelFrame(self.master, text="Measurement data", padx=5, pady=5)
        self.graph.grid(row=0,column=1)

        self.f = Figure(figsize=(5,4),dpi=100)
        self.a = self.f.add_subplot(111)

        canvas = FigureCanvasTkAgg(self.f,self.graph)
        canvas.show()
        canvas.get_tk_widget().pack(expand=True)

        self.last_measurement_stringvar = Tkinter.StringVar()
        self.last_measurement_stringvar.set("Last measurement: A second ago")
        self.text_last_measurement = Tkinter.Label(self.graph, textvar=self.last_measurement_stringvar)
        self.text_last_measurement.pack()

    def refresh_parameters_from_device(self):
        #Read handle values from device characteristics
        #self.thresh_high_stringvar.set(self.device.read(handle=0))
        #self.thresh_low_stringvar.set(self.device.read(handle=1))
        #self.measuring_interval_stringvar.set(self.device.read(handle=2))
        #self.watering_time_stringvar.set(self.device.read(handle=3))
        print("Parameters refreshed")

    def apply_parameters_to_device(self):
        #self.device.write(handle, self.thresh_high_stringvar)
        #self.device.write(handle, self.thresh_low_stringvar)
        #self.device.write(handle, self.measuring_interval_stringvar)
        #self.device.write(handle, self.watering_time_stringvar)
        print("Parameters updated")

def animate(i):
    pullData = open('sampleText.txt','r').read()
    dataArray = pullData.split('\n')
    xar = []
    yar = []
    for eachLine in dataArray:
        if len(eachLine) > 1:
            x,y = eachLine.split(',')
            xar.append(int(x))
            yar.append(int(y))
    my_gui.a.clear
    my_gui.a.plot(xar,yar)

root = Tkinter.Tk()
my_gui = GUI(root)
ani = animation.FuncAnimation(my_gui.f, animate, interval=1000)
root.mainloop()
