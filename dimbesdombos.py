import mplfinance as mpf
import numpy as np
import pandas as pd
from pandas._libs.tslibs.timestamps import Timestamp

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
class Dimbesdombos():

    def __init__(self, timestamp, value):
        self.timestamp = timestamp
        self.value = value


def dimbesdombos(long):
    global data
    peaks = []
    signals = []
    ma_20 = data['ma_20']
    # lt(a,b) = a < b
    # gt(a,b) = a > b
    nagy = ""
    kicsi = ""


    if long:
        ma_1 = data['High']
        relation_operator = operator.lt
        chart_operator = operator.add
        nagy = 'domb_m'
        kicsi = 'domb'

    else:
        ma_1 = data['Low']
        relation_operator = operator.gt
        chart_operator = operator.sub
        nagy = 'volgy_m'
        kicsi = 'volgy'

    tmp_peak = None
    tmp_value = None
    init = True
    for row_id, value in ma_1.iteritems():
        # Ha kezdésnek az ma_20 felett van akkor megvárjuk míg alá megy
        if init and relation_operator(value,ma_20[row_id]):    #(value < ma_20[row_id]):
            init = False

        elif relation_operator(ma_20[row_id], value):   #value > ma_20[row_id]:
            if tmp_peak is None:
                tmp_peak = row_id
                tmp_value = value
            elif tmp_peak is not None and relation_operator(ma_1[tmp_peak], value):      #(ma_1[tmp_peak] < value):
                tmp_peak = row_id
                tmp_value = value

        elif tmp_peak is not None and relation_operator(value, ma_20[row_id]):  #value < ma_20[row_id]:
            peaks.append(Dimbesdombos(tmp_peak, tmp_value))
            tmp_peak = None
            tmp_value = None
    # for i in peaks:
    #    print(str(i.timestamp) + " " + str(i.value))
    # print(peaks[len(peaks)-5:])

    for i in range(0, len(peaks)-1):
        first = peaks[i]
        second = peaks[i+1]
        if relation_operator(second.value, first.value):     #first.value > second.value:
            signals.append(second)
    # for i in signals:
    #    print(str(i.timestamp) + " " + str(i.value))

    jel = []
    dombdate = []
    for i in signals:
        dombdate.append(i.timestamp)
    for row_id, value in ma_1.iteritems():
        if row_id in dombdate:
            jel.append(chart_operator(value, 0.001020))
        else:
            jel.append(None)
    data[kicsi] = jel
    jel_m = []
    dombdate_m = []
    for i in peaks:
        dombdate_m.append(i.timestamp)
    for row_id, value in ma_1.iteritems():
        if row_id in dombdate_m:
            jel_m.append(chart_operator(value, 0.001020))
        else:
            jel_m.append(None)
    data[nagy] = jel_m


def dd_import_data():
    start_time = cmd_output_start('Importing data...')

    global data
    data = pd.read_csv(
        test_path, usecols=['Time', 'Open', 'High', 'Low', 'Close', 'Instrument', 'Period'], sep=';',
        index_col=0, parse_dates=True).query('Period == 60')
    data['ma_20'] = ma(data['Close'], 20)
    data['ema_200'] = ema(data['Close'], 200)

    # print(fxdata)

    # print(data)
    # print(data)
    cmd_output_end(start_time)




def dd_make_charts(time_frames_list):
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
                fxdata = data.query('Instrument == "' + instrument.name + '" and Period == ' + str(TF.value)).tail(1400)
                #print(fxdata)
                instrument.add_idosik(Idosik(TF))
                instrument.add_data(TF, fxdata)
                num_of_charts = int(fxdata['Open'].size / candle_count)
                for i in range(0, num_of_charts):

                    min = 0 + i * candle_count
                    max = 0 + candle_count + i * candle_count
                    t_fxdata = fxdata[min: max]
                    print(str(num_of_charts) + ": " + str(min) + " - " + str(max))
                    #print(t_fxdata)
                    #print(len(t_fxdata['pv']))
                    ma_20 = t_fxdata[['ma_20']]
                    ma_1_high = t_fxdata[['High']]
                    ma_1_low = t_fxdata[['Low']]
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
                        mpf.make_addplot(ma_1_high, color='green', linestyle='-', width=1.5),
                        mpf.make_addplot(ma_1_low, color='red', linestyle='-', width=1.5),
                        mpf.make_addplot(t_fxdata[['domb']], type='scatter', markersize=200, color='blue'),
                        mpf.make_addplot(t_fxdata[['domb_m']], type='scatter', markersize=100, color='orange'),
                        mpf.make_addplot(t_fxdata[['volgy']], type='scatter', markersize=200, color='blue'),
                        mpf.make_addplot(t_fxdata[['volgy_m']], type='scatter', markersize=100, color='orange')
                    ]

                    try:
                        mpf.plot(t_fxdata, type='candle', style=sajat_style, addplot=dimbesd,
                                 figratio=(picture_width, picture_height),
                             savefig=charts_path + instrument.name + "_" + TF.name + "_" + str(candle_count)
                                     + "_" + str(min) + "_" + str(max) + ".png")

                    except Exception as e:
                        print(e)

                    # mpf.plot(t_fxdata, type='candle', style=sajat_style, addplot=colorgia,
                    #                   savefig=charts_path + instrument.name + "_" + TF.name + "_" + str(candle_count)
                    #                           + "_" + str(min) + "_" + str(max) + ".png")

        cmd_output_end(start_time)

def dd_run():
    global instruments
    instruments = sc_get_instruments()
    dd_import_data()
    dimbesdombos(True)
    dimbesdombos(False)
    dd_make_charts(chart_time_frames)
