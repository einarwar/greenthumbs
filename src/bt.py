#!/usr/bin/python
# -*- mode: python; coding: utf-8 -*-

# Copyright (C) 2014, Oscar Acena <oscaracena@gmail.com>
# This software is under the terms of Apache License v2 or later.

from __future__ import print_function

import sys
from gattlib import GATTRequester, DiscoveryService
import Tkinter


accepted_uuids = ["00:1E:C0:22:A8:DB", "00:1E:C0:22:A8:FB"]

class Device():
    def __init__(self, address, info):
        self.address = address
        self.appearance = info["appearance"]
        self.flags = info["flags"]

        self.name_text = info["name"]
        self.name = Tkinter.StringVar()
        self.name.set(self.name_text)

        self.THRESH_LOW = 0
        self.THRESH_HIGH = 0
        self.WATERING_TIME_MS = 0
        self.MEASURE_PERIOD_S = 0

        self.MEASURE_NOW_FLAG = False
        self.WATER_NOW_FLAG = False

        self.uuids = info["uuids"]
        self.reader = Reader(address)

    def set_THRESH_LOW(self, val):
        self.THRESH_LOW = val

    def set_THRESH_HIGH(self, val):
        self.THRESH_HIGH = val

    def set_WATERING_TIME_MS(self, val):
        self.WATERING_TIME_MS = val

    def set_MEASURE_PERIOD_S(self, val):
        self.MEASURE_PERIOD_S = val

    def water_now(self):
        self.WATER_NOW_FLAG = True

    def measure_now(self):
        self.MEASURE_NOW_FLAG = True

    def read(self, handle):
        return self.reader.request_data(handle)

    def write(self, handle, data):
        self.reader.send_data(handle,data)

class Reader(object):
    def __init__(self, address):
        self.requester = GATTRequester(address, False)
        self.connect()
        #self.request_data()

    def connect(self):
        print("Connecting...", end=' ')
        sys.stdout.flush()

        self.requester.connect(True)
        print("OK!")

    def request_data(self, handle):
        return self.requester.read_by_handle(handle)[0]

    def send_data(self, handle, data):
        #self.requester.write_by_handle(handle, str(bytearray([data])))
        self.requester.write_by_handle(handle, data)


def discover_btle_devices(adapter="hci0"):
    service = DiscoveryService(adapter)
    devices = service.discover(4)
    print("Found {} devices".format(len(list(devices.items()))))
    for address, name in list(devices.items()):
        if address in accepted_uuids:
            print("Found device with address: {} that is accpeted, good job!".format(address))

        else:
            print("Device with address {} not listed in accepted_uuids. If you want it to play, add it to the accepted uuids".format(address))
    d = [Device(address, name) for address, name in list(devices.items()) if address in accepted_uuids]
    return d


if __name__ == '__main__':
    #service = DiscoveryService("hci0")
    #devices = service.discover(4)

    #for address, name in list(devices.items()):
    #    d = Device(address,name)
    #    print("Found the following devices: {}".format(address))

    d = discover_btle_devices()
    #for dev in d:
    #    print(dev.name_text)
    print("Done.")
