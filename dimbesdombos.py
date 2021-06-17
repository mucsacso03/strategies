import mplfinance as mpf
import numpy as np
import pandas as pd
from pandas._libs.tslibs.timestamps import Timestamp
import datetime as dt
import smtplib
import ssl
import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from Instrument import *
from enum_classes import *
from indicators import *
from run_timer import *
from init import sc_get_instruments
import operator

path = 'C:\\Users\\David\\AppData\\Roaming\\MetaQuotes\\Terminal\\9A88166CEDA39D24B9AAA705731B4583\\MQL4\\Files\\fxprimus_data_simple.csv'
test_path = 'C:\\Users\\David\\AppData\\Roaming\\MetaQuotes\\Terminal\\9A88166CEDA39D24B9AAA705731B4583\\MQL4\\Files\\fxprimus_data_GBPUSD_h1.csv'
charts_path = 'C:\\Users\\David\\PycharmProjects\\dimbesdombos\\robotcharts\\'
cropped_charts_path = 'C:\\Users\\David\\PycharmProjects\\dimbesdombos\\cropped_charts\\'
data: pd
instruments = []
candle_count = 210
picture_width = 24
picture_height = 5.75
chart_time_frames = [TimeFrames.H1
                     # , TimeFrames.H1, TimeFrames.D1, TimeFrames.M30
                     ]
admin_email = 'davidbardos97@gmail.com'


class Dimbesdombos():

    def __init__(self, instrument, timeframe, timestamp, value, orientaton, first_crossing_timestamp,
                 second_crossing_timestamp):
        self.instrument = instrument
        self.timeframe = timeframe
        self.peak_timestamp = timestamp
        self.value = value
        self.sector_trend = None
        self.trend = None
        self.first_crossing_timestamp = first_crossing_timestamp
        self.second_crossing_timestamp = second_crossing_timestamp
        self.orientation = orientaton


def dimbesdombos_for_plotting(fxdata, long, instrument, timeframe):
    start_time = cmd_output_start('Calculating DimbesDombos...')

    peak_or_valleys = []
    signals = []
    ma_20 = fxdata['ma_20']
    ema_200 = fxdata['ema_200']
    trend_candle_number = 150

    # lt(a,b) = a < b
    # gt(a,b) = a > b
    if long:
        ma_1 = fxdata['High']
        relation_operator = operator.lt
        chart_operator = operator.add
        nagy = 'domb_m'
        kicsi = 'domb'
        trend_l = 'trend_l_l'
        trend_s = 'trend_l_s'

    else:
        ma_1 = fxdata['Low']
        relation_operator = operator.gt
        chart_operator = operator.sub
        nagy = 'volgy_m'
        kicsi = 'volgy'
        trend_l = 'trend_s_l'
        trend_s = 'trend_s_s'

    tmp_peak = None
    tmp_first_crossing = None
    tmp_value = None
    init = True
    # inc = 0
    # previous_trend_candle_value = None
    for row_id, value in ma_1.iteritems():
        # inc = inc + 1

        # Ha kezdésnek az ma_20 felett van akkor megvárjuk míg alá megy
        if init and relation_operator(value, ma_20[row_id]):  # (value < ma_20[row_id]):
            init = False

        elif relation_operator(ma_20[row_id], value):  # value > ma_20[row_id]:
            if tmp_peak is None:
                tmp_peak = row_id
                tmp_value = value
                tmp_first_crossing = row_id
            elif tmp_peak is not None and relation_operator(ma_1[tmp_peak], value):  # (ma_1[tmp_peak] < value):
                tmp_peak = row_id
                tmp_value = value

        elif tmp_peak is not None and relation_operator(value, ma_20[row_id]):  # value < ma_20[row_id]:
            if long:
                orientation = Trend.Long
            else:
                orientation = Trend.Short

            # if inc >= trend_candle_number:
            #     previous_trend_candle_value = fxdata[inc - trend_candle_number:inc - trend_candle_number + 1].index[0]
            #     first_ema_200_value = ema_200[previous_trend_candle_value]
            #     second_ema_200_value = ema_200[row_id]
            #     if first_ema_200_value > second_ema_200_value:
            #         trend = Trend.Short
            #     elif first_ema_200_value < second_ema_200_value:
            #         trend = Trend.Long

            peak_or_valleys.append(
                Dimbesdombos(instrument, timeframe, tmp_peak, tmp_value, orientation, tmp_first_crossing, row_id))
            tmp_peak = None
            tmp_value = None
            tmp_first_crossing = None

    # első szűrés. x gyertyával visszanézni a ema_200 irányultságát
    for dd in peak_or_valleys:
        second_crossing_index = fxdata.index.get_loc(dd.second_crossing_timestamp)
        second_crossing_value = ema_200[dd.second_crossing_timestamp]
        previous_trend_candle_index = second_crossing_index - trend_candle_number
        if previous_trend_candle_index > 0:
            previous_trend_candle_value = \
                fxdata[previous_trend_candle_index: previous_trend_candle_index + 1]['ema_200'][0]
        else:
            previous_trend_candle_value = None

        if previous_trend_candle_value is not None:
            if previous_trend_candle_value > second_crossing_value:
                dd.trend = Trend.Short
            if previous_trend_candle_value < second_crossing_value:
                dd.trend = Trend.Long

    for i in range(0, len(peak_or_valleys) - 1):
        first = peak_or_valleys[i]
        second = peak_or_valleys[i + 1]
        first_crossing_value = ema_200[first.first_crossing_timestamp]
        second_crossing_value = ema_200[second.second_crossing_timestamp]
        if first_crossing_value > second_crossing_value:
            second.sector_trend = Trend.Short
        if first_crossing_value < second_crossing_value:
            second.sector_trend = Trend.Long

    # for i in peak_or_valleys:
    #    print(str(i.timestamp) + " " + str(i.value))
    # print(peak_or_valleys[len(peak_or_valleys)-5:])

    # Kis dombok/volgyek kiválasztása
    for i in range(0, len(peak_or_valleys) - 1):
        first = peak_or_valleys[i]
        second = peak_or_valleys[i + 1]
        if relation_operator(second.value, first.value):  # first.value > second.value:
            signals.append(second)

    signals = signals[-1:]
    # for i in signals:
    #    print(str(i.timestamp) + " " + str(i.value))

    # charton lévő signál
    jel = []
    dombdate = []
    for i in signals:
        dombdate.append(i.peak_timestamp)
    for row_id, value in ma_1.iteritems():
        if row_id in dombdate:
            jel.append(chart_operator(value, 0.001020))
        else:
            jel.append(None)
    fxdata[kicsi] = jel

    jel_m = []
    dombdate_m = []
    for i in peak_or_valleys:
        dombdate_m.append(i.peak_timestamp)
    for row_id, value in ma_1.iteritems():
        if row_id in dombdate_m:
            jel_m.append(chart_operator(value, 0.001020))
        else:
            jel_m.append(None)
    fxdata[nagy] = jel_m

    # charton trend
    trend_long = []
    trend_short = []
    found_match = False
    for row_id, value in ma_1.iteritems():
        for i in signals:
            if row_id == i.peak_timestamp:
                found_match = True
                if i.sector_trend == Trend.Long:
                    trend_long.append(chart_operator(value, 0.001020))
                    trend_short.append(0)
                elif i.sector_trend == Trend.Short:
                    trend_short.append(chart_operator(value, 0.001020))
                    trend_long.append(0)
                else:
                    trend_short.append(0)
                    trend_long.append(0)
        if not found_match:
            trend_short.append(0)
            trend_long.append(0)

        found_match = False

    # print(trend_long)
    fxdata[trend_l] = trend_long
    fxdata[trend_s] = trend_short

    cmd_output_end(start_time)

    return fxdata


def dimbesdombos(fxdata, long, instrument, timeframe):
    #start_time = cmd_output_start('Calculating DimbesDombos...')

    peak_or_valleys = []
    signals = []
    ma_20 = fxdata['ma_20']
    ema_200 = fxdata['ema_200']
    trend_candle_number = 150

    # lt(a,b) = a < b
    # gt(a,b) = a > b
    if long:
        ma_1 = fxdata['High']
        relation_operator = operator.lt

    else:
        ma_1 = fxdata['Low']
        relation_operator = operator.gt

    tmp_peak = None
    tmp_first_crossing = None
    tmp_value = None
    init = True
    for row_id, value in ma_1.iteritems():
        # Ha kezdésnek az ma_20 felett van akkor megvárjuk míg alá megy
        if init and relation_operator(value, ma_20[row_id]):  # (value < ma_20[row_id]):
            init = False

        elif relation_operator(ma_20[row_id], value):  # value > ma_20[row_id]:
            if tmp_peak is None:
                tmp_peak = row_id
                tmp_value = value
                tmp_first_crossing = row_id
            elif tmp_peak is not None and relation_operator(ma_1[tmp_peak], value):  # (ma_1[tmp_peak] < value):
                tmp_peak = row_id
                tmp_value = value

        elif tmp_peak is not None and relation_operator(value, ma_20[row_id]):  # value < ma_20[row_id]:
            if long:
                orientation = Trend.Long
            else:
                orientation = Trend.Short
            peak_or_valleys.append(
                Dimbesdombos(instrument, timeframe, tmp_peak, tmp_value, orientation, tmp_first_crossing, row_id))
            tmp_peak = None
            tmp_value = None
            tmp_first_crossing = None

    # első szűrés. x gyertyával visszanézni a ema_200 irányultságát
    for dd in peak_or_valleys:
        second_crossing_index = fxdata.index.get_loc(dd.second_crossing_timestamp)
        second_crossing_value = ema_200[dd.second_crossing_timestamp]
        previous_trend_candle_index = second_crossing_index - trend_candle_number
        if previous_trend_candle_index > 0:
            previous_trend_candle_value = \
                fxdata[previous_trend_candle_index: previous_trend_candle_index + 1]['ema_200'][0]
        else:
            previous_trend_candle_value = None

        if previous_trend_candle_value is not None:
            if previous_trend_candle_value > second_crossing_value:
                dd.trend = Trend.Short
            if previous_trend_candle_value < second_crossing_value:
                dd.trend = Trend.Long

    # második szűrés. Nagy és kis domb/volgy távolságában vizsgálni az ema_200-at
    for i in range(0, len(peak_or_valleys) - 1):
        first = peak_or_valleys[i]
        second = peak_or_valleys[i + 1]
        first_crossing_value = ema_200[first.first_crossing_timestamp]
        second_crossing_value = ema_200[second.second_crossing_timestamp]
        if first_crossing_value > second_crossing_value:
            second.sector_trend = Trend.Short
        if first_crossing_value < second_crossing_value:
            second.sector_trend = Trend.Long

    # Kis dombok/volgyek kiválasztása
    for i in range(len(peak_or_valleys) - 2, len(peak_or_valleys) - 1):
        first = peak_or_valleys[i]
        second = peak_or_valleys[i + 1]
        if relation_operator(second.value, first.value):  # first.value > second.value:
            signals.append(second)

    #cmd_output_end(start_time)
    # print(signals)
    return signals


def dd_import_data():
    start_time = cmd_output_start('Importing data...')

    global data
    file_locked = True
    while file_locked:
        try:
            data = pd.read_csv(
                path, usecols=['Time', 'Open', 'High', 'Low', 'Close', 'Instrument', 'Period'], sep=';',
                index_col=0, parse_dates=True).query('Period == 60')
            file_locked = False
        except:
            pass
    # print(fxdata)

    # print(data)
    # print(data)
    cmd_output_end(start_time)


def dd_make_charts_for_plotting(time_frames_list):
    start_time = cmd_output_start('Initializing charts...')

    # chart_to_delete = os.listdir(charts_path)

    # for item in chart_to_delete:
    # if item.endswith(".png"):
    # os.remove(os.path.join(str(charts_path), item))

    sajat_color = mpf.make_marketcolors(up='g', down='r')
    sajat_style = mpf.make_mpf_style(marketcolors=sajat_color)

    for TF in time_frames_list:
        for instrument in instruments:
            # print('Making chart: ' + instrument.name)
            fxdata = data.query('Instrument == "' + instrument.name + '" and Period == ' + str(TF.value)).tail(
                candle_count)
            fxdata['ma_20'] = ma(fxdata['Close'], 20)
            fxdata['ema_200'] = ema(fxdata['Close'], 200)

            fxdata = dimbesdombos_for_plotting(fxdata, True, instrument.name, TF)
            fxdata = dimbesdombos_for_plotting(fxdata, False, instrument.name, TF)

            # print(fxdata)
            instrument.add_idosik(Idosik(TF))
            instrument.add_data(TF, fxdata)
            num_of_charts = int(fxdata['Open'].size / candle_count)
            for i in range(0, num_of_charts):
                min = 0 + i * candle_count
                max = 0 + candle_count + i * candle_count
                t_fxdata = fxdata[min: max]
                print(str(num_of_charts) + ": " + str(min) + " - " + str(max))
                # print(t_fxdata)
                # print(len(t_fxdata['pv']))
                ma_20 = t_fxdata[['ma_20']]
                ema_200 = t_fxdata[['ema_200']]
                ma_1_high = t_fxdata[['High']]
                ma_1_low = t_fxdata[['Low']]

                trend_s_l = t_fxdata[['trend_s_l']]
                trend_s_s = t_fxdata[['trend_s_s']]
                trend_l_l = t_fxdata[['trend_l_l']]
                trend_l_s = t_fxdata[['trend_l_s']]

                # bb_1 = t_fxdata[['lower_bb_1', 'upper_bb_1']]
                # bb_2 = t_fxdata[['lower_bb_2', 'upper_bb_2']]
                # bollinger = [
                #     mpf.make_addplot(ma_20, color='blue', linestyle='--', width=0.8),
                #     mpf.make_addplot(bb_1, color='navy', linestyle='-.', width=0.8),
                #     mpf.make_addplot(bb_2, color='orange', linestyle='-.', width=0.8)
                # ]
                # ema_5 = fxdata[['ema_5']]
                # ema_2 = fxdata[['ema_2']]
                # colorgia = [
                #     mpf.make_addplot(ma_20, color='blue', linestyle='--', width=1),
                #     mpf.make_addplot(bb_2, color='orange', linestyle='-.', width=1),
                #     # mpf.make_addplot(ema_5, color='blue', linestyle='-', width=1),
                #     # mpf.make_addplot(ema_2, color='purple', linestyle='-', width=1),
                #     mpf.make_addplot(t_fxdata[['pv']], type='scatter')
                # ]
                dimbesd = [
                    mpf.make_addplot(ma_20, color='blue', linestyle='-', width=1.5),
                    mpf.make_addplot(ema_200, color='navy', linestyle='-', width=1.5),
                    mpf.make_addplot(ma_1_high, color='green', linestyle='-', width=1.5),
                    mpf.make_addplot(ma_1_low, color='red', linestyle='-', width=1.5),
                    mpf.make_addplot(t_fxdata[['domb']], type='scatter', markersize=200, color='blue'),
                    mpf.make_addplot(t_fxdata[['domb_m']], type='scatter', markersize=100, color='orange'),
                    mpf.make_addplot(t_fxdata[['volgy']], type='scatter', markersize=200, color='blue'),
                    mpf.make_addplot(t_fxdata[['volgy_m']], type='scatter', markersize=100, color='orange'),
                    mpf.make_addplot(t_fxdata[['trend_s_l']], type='scatter', marker="^", markersize=100,
                                     color='orange'),
                    mpf.make_addplot(t_fxdata[['trend_s_s']], type='scatter', marker="v", markersize=100,
                                     color='orange'),
                    mpf.make_addplot(t_fxdata[['trend_l_l']], type='scatter', marker="^", markersize=100,
                                     color='orange'),
                    mpf.make_addplot(t_fxdata[['trend_l_s']], type='scatter', marker="v", markersize=100,
                                     color='orange')
                ]

                # try:
                mpf.plot(t_fxdata, type='candle', style=sajat_style, addplot=dimbesd,
                         figratio=(picture_width, picture_height),
                         savefig=charts_path + instrument.name + "_" + TF.name + "_" + str(candle_count)
                                 + "_" + str(min) + "_" + str(max) + ".png")

                # except Exception as e:
                #    print(e)

                # mpf.plot(t_fxdata, type='candle', style=sajat_style, addplot=colorgia,
                #                   savefig=charts_path + instrument.name + "_" + TF.name + "_" + str(candle_count)
                #                           + "_" + str(min) + "_" + str(max) + ".png")

    cmd_output_end(start_time)


def dd_make_charts(time_frames_list):
    start_time = cmd_output_start('Initializing charts...')

    signals = []

    for TF in time_frames_list:
        for instrument in instruments:
            # print('Making chart: ' + instrument.name)
            fxdata = data.query('Instrument == "' + instrument.name + '" and Period == ' + str(TF.value)).tail(
                candle_count)
            fxdata['ma_20'] = ma(fxdata['Close'], 20)
            fxdata['ema_200'] = ema(fxdata['Close'], 200)

            signals.append(dimbesdombos(fxdata, True, instrument.name, TF))
            signals.append(dimbesdombos(fxdata, False, instrument.name, TF))

    cmd_output_end(start_time)

    return signals


def detection(signals_sum):
    start_time = cmd_output_start('Detecting...')

    trendirany = []
    korrekcio = []
    for signals in signals_sum:
        for signal in signals:
            if signal.orientation == signal.trend and signal.orientation == signal.sector_trend:
                trendirany.append(signal)
            else:
                korrekcio.append(signal)

    with open('previous_mail.txt', "r") as file:
        previous_mail = file.read()

    new_signal = False
    str_trendirany = "Trendiranyu dimbesdombos\n\n"
    str_not_changed_signals = str_trendirany
    for signal in trendirany:
        signal_str = signal.instrument + " - " + signal.timeframe.name + ": " \
                     + signal.orientation.name + "\t\t|\t\t" + str(signal.peak_timestamp) + " - " + str(signal.value) \
                     + "\n"
        if signal_str in previous_mail:
            str_not_changed_signals = str_not_changed_signals + signal_str
        else:
            str_not_changed_signals = str_not_changed_signals + signal_str
            str_trendirany = str_trendirany + signal_str
            new_signal = True

    print("\nMail content:\n\n" + str_trendirany)

    with open('previous_mail.txt', "w") as file:
        file.write(str_not_changed_signals)

    file.close()

    cmd_output_end(start_time)

    return str_trendirany, new_signal

    # str_korrekcio = "Korrekcios dimbesdombos\n\n"
    # for signal in korrekcio:
    #     str_korrekcio = str_korrekcio + signal.instrument + " - " + signal.timeframe.name + ": " \
    #                      + signal.orientation.name + " " + str(signal.peak_timestamp) + " " + str(signal.value) \
    #                      + "\n"
    # print(str_korrekcio)


def send_email(user, debug, mail_content):
    start_time = cmd_output_start('Sending email...')

    if debug:
        yes = input('Send email?(y): ')
    else:
        yes = 'y'
    if yes == 'y':

        # The mail addresses and password
        sender_address = 'db.mt.obd@gmail.com'
        sender_pass = 'xQiG158CD40uV7TXLeIC'
        receiver_address = [admin_email]

        # Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address
        if user:
            file = open('user_emails.txt', "r")
            emails = file.read().split("\n")
            file.close()
            receiver_address += emails

        print(receiver_address)
        message['To'] = ','.join(receiver_address)
        message['Subject'] = "MT dimbes-dombos"

        # The body and the attachments for the mail
        message.attach(MIMEText(mail_content, 'plain'))

        # Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
        session.starttls()  # enable security
        session.login(sender_address, sender_pass)  # login with mail_id and password
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()
        print('Mail Sent')

    cmd_output_end(start_time)


def check_chart_data(user, debug):
    last_update = 0
    update_time = 0
    off_time = dt.time(23, 0, 0)
    off_day = 'Friday'

    while True:
        current_time = datetime.now().time()
        current_day = datetime.today().strftime("%A")
        if (current_day == off_day) & (current_time > off_time):
            time.sleep(172800)  # Sleep for 2 day, if time is later then 23:00 and is Friday

        if current_time > off_time:
            time.sleep(3600)  # Sleep for 1 hour, if time is later then 23:00

        try:
            update_time = os.stat(path).st_mtime
        except:
            pass
        # print(str(last_update) + " --- " + str(update_time))
        if update_time > last_update:
            last_update = update_time
            dd_run(user, debug)

        time.sleep(15)


def dd_run(user, debug):
    start_time = time.time()

    global instruments
    instruments = sc_get_instruments()
    dd_import_data()
    # dd_make_charts_for_plotting(chart_time_frames)
    signals = dd_make_charts(chart_time_frames)
    message, new_signal = detection(signals)
    if new_signal: send_email(user, debug, message)

    print("--- Total runtime: %s seconds ---" % (time.time() - start_time))
