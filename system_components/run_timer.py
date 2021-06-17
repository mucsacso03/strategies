import time
from datetime import datetime as da


def cmd_output_start(string):
    start_time = time.time()
    print(str(da.fromtimestamp(start_time)) + ":  " + string, end=' ')
    return start_time


def cmd_output_end(start_time):
    print('Done! %s seconds' % (time.time() - start_time))
