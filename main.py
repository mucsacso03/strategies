import datetime as dt
import os
import time
from datetime import datetime, date

from dimbesdombos import dd_make_charts
from make_message import make_email_message
from system_components.constants import DATA_PATH, USED_TIMEFRAMES
from system_components.init import get_instruments, import_data


def run(user, debug):
    start_time = time.time()

    instruments = get_instruments()
    data = import_data()

    # dd_make_charts_for_plotting(USED_TIMEFRAMES, instruments, data)
    signals = dd_make_charts(USED_TIMEFRAMES, instruments, data, quiet=True)

    message, new_signal = make_email_message(signals)
    # if new_signal: send_email(message, "MT dimbes-dombos", user, debug)

    print("--- Total runtime: %s seconds ---" % (time.time() - start_time))


def check_chart_data(user, debug):
    last_update = 0
    update_time = 0
    off_time = dt.time(22, 0, 0)
    off_day = ['Friday', 'Saturday', 'Sunday']

    while True:
        current_time = datetime.now().time()
        current_day = datetime.today().strftime("%A")
        if (current_day in off_day) & (current_time > off_time):
            print('Sleeping for the weekend...')
            time.sleep(172800)  # Sleep for 2 day, if time is later then 23:00 and is Friday

        if current_time > off_time:
            print('Sleeping until 01:00 AM...')
            sleep_seconds_until_midnight = (
                    datetime.combine(date.today(), dt.time(23, 59, 59)) -
                    datetime.combine(date.today(), off_time)).total_seconds()
            time.sleep(sleep_seconds_until_midnight + 3601)  # Sleep for until 01:00 AM, if time is later then 22:00

        vmi = datetime.combine(date.today(), dt.time(23, 59, 59)) - datetime.combine(date.today(), off_time)
        print(vmi)
        print(vmi.total_seconds() + 3601)
        print(dt.timedelta(seconds=(vmi.total_seconds() + 3601)))
        # print(dt.time(24,0,0))
        try:
            update_time = os.stat(DATA_PATH).st_mtime
        except:
            pass
        # print(str(last_update) + " --- " + str(update_time))
        if update_time > last_update:
            last_update = update_time
            # run(user, debug)

        time.sleep(15)


if __name__ == '__main__':
    user = False
    debug = False
    check_chart_data(user, debug)
