from datetime import datetime
from decimal import Decimal

from system_components.enum_classes import *


class BoundingBox():
    # (0,0) a bal felső sarok. X tengely megy jobbra, az Y lefele. A kép pixel méretével normalizálva vannak az értékek.
    def __init__(self, values):  # type, x_center, y_center, width, height):
        self.type = values[0]
        self.x_center = Decimal(values[1])
        self.y_center = Decimal(values[2])
        self.width = Decimal(values[3])
        self.height = Decimal(values[4])


class Idosik:

    def __init__(self, period):
        self.period = period.value
        self.periodname = period.name
        self.timestamp = None
        self.signal = None
        self.fxdata = None

    def add_data(self, fxdata):
        self.fxdata = fxdata


class Instrument:

    def __init__(self, name):
        self.name = name
        self.idosikok = []

    def add_idosik(self, idosik):
        self.idosikok.append(idosik)

    def add_data(self, timeframe, fxdata):
        for i in self.idosikok:
            if i.period == timeframe.value:
                i.fxdata = fxdata

    def print_idosikok(self):
        for i in self.idosikok:
            print(self.name + ": " + str(i.period))

    def get_idosikok(self):
        return self.idosikok

    def get_signals(self):
        for i in self.idosikok:
            if i.signal != None and i.peak_timestamp != None:
                try:
                    return self.name + ": " + str(i.periodname) + " - " + str(
                        Signals(int(i.signal)).name)  # + " | " + datetime.datetime.fromtimestamp(i.timestamp).strftime(
                    # '%Y-%m-%d %H:%M:%S')
                except Exception as e:
                    print(e)
                    pass

    def print_signals(self):
        for i in self.idosikok:
            if i.signal != None and i.peak_timestamp != None:
                try:
                    print(self.name + ": " + str(i.periodname) + " - " + str(
                        Signals(int(i.signal)).name) + " | " + datetime.fromtimestamp(i.peak_timestamp).strftime(
                        '%Y-%m-%d %H:%M:%S'))
                except Exception as e:
                    print(e)
                    pass
