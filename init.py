from run_timer import *
from Instrument import *

def sc_get_instruments(filename = 'instruments.txt'):
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