import pandas as pd

from Instrument import *
from constants import DATA_PATH
from run_timer import *


def get_instruments(filename='instruments.txt'):
    start_time = cmd_output_start('Importing instruments...')

    file = open(filename, "r")
    content = file.read().split("\n")

    # content = ["GBPUSD"]

    instrument_list = []
    for inst in content:
        instrument_list.append(Instrument(inst))

    file.close()

    cmd_output_end(start_time)
    return instrument_list


def import_data():
    start_time = cmd_output_start('Importing data...')

    file_locked = True
    while file_locked:
        try:
            data = pd.read_csv(
                DATA_PATH, usecols=['Time', 'Open', 'High', 'Low', 'Close', 'Instrument', 'Period'], sep=';',
                index_col=0, parse_dates=True).query('Period == 60')
            file_locked = False
        except:
            pass

    # print(data)

    cmd_output_end(start_time)

    return data
