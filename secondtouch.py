import mplfinance as mpf
import numpy as np
import pandas as pd

from Instrument import *
from enum_classes import *
from indicators import *
from run_timer import *

path = 'C:\\Users\\David\\AppData\\Roaming\\MetaQuotes\\Terminal\\9A88166CEDA39D24B9AAA705731B4583\\MQL4\\Files\\fxprimus_data_simple.csv'
test_path = 'C:\\Users\\David\\AppData\\Roaming\\MetaQuotes\\Terminal\\9A88166CEDA39D24B9AAA705731B4583\\MQL4\\Files\\fxprimus_data_GBPUSD_h1.csv'
charts_path = 'C:\\Users\\David\\PycharmProjects\\mt_r\\robotcharts\\'
cropped_charts_path = 'C:\\Users\\David\\PycharmProjects\\mt_r\\cropped_charts\\'
data = ""
instruments = []
candle_count = 70
chart_time_frames = [TimeFrames.H1
                     # , TimeFrames.H1, TimeFrames.D1, TimeFrames.M30
                     ]
emails = [
    'davidbardos97@gmail.com'
    , 'bardosrichard99@gmail.com'
]


def sc_get_instruments():
    start_time = cmd_output_start('Importing instruments...')

    file = open('instruments.txt', "r")
    content = file.read().split("\n")

    content = ["GBPUSD"]

    global instruments
    for inst in content:
        instruments.append(Instrument(inst))

    file.close()

    cmd_output_end(start_time)


def second_touch_upper(data):
    signal = []
    previous = -1.0
    bb_2_touch = data['above_bb_2']
    high = data['High']
    low = data['Low']
    above_sma_20 = data['above_sma_20']

    first_touch = None
    valley = None
    valley_inc = 0
    inc = 0
    for row_id, value in bb_2_touch.iteritems():
        #print(str(inc) + " - " + str(valley_inc) + " - " + str(len(signal)))

        # Ha a van olyan gyertya ami a sma_20 alá zár akkor már nem lehet second touch
        if not above_sma_20[row_id]:
            first_touch = None
            valley = None
            signal.append(None)

        # Ha bb_20_2 felett van és az sma_20 felett is
        elif value and above_sma_20[row_id]:
            # ha még nincs first touch akkor beírjuk
            if first_touch is None:
                first_touch = row_id
                signal.append(None)

            # ha van second touch és van völgyünk akkor beírjuk a jelzést és a second toucht first touchnak regisztráljuk
            elif valley is not None:
                # print(valley, end=" ")
                # print(valley_inc)
                #signal.append(low[valley] * 0.9999)
                signal[valley_inc] = (low[valley] * 0.9999)
                valley = None
                valley_inc = 0
                first_touch = row_id
                signal.append(None)
            else:
                signal.append(None)

        # völgy gyűjtés: ha van first touch és a bb_20_2 és az sma_20 között vagyunk
        elif first_touch is not None and not value and above_sma_20[row_id]:
            # ha még nincs völgy akkor beírjuk a gyertyat
            if valley is None:
                valley = row_id
                valley_inc = inc
                signal.append(None)

            # ha az elöző völgy magasabb mint ez a gyertya akkor frissitjük ezzel
            elif valley is not None and low[row_id] < low[valley]:
                valley = row_id
                valley_inc = inc
                signal.append(None)
            else:
                signal.append(None)
            #signal.append(low[row_id] * 0.9999)

        else:
            #signal.append(high[coloumn] / 0.9999)
            signal.append(None)
        inc += 1

    # for date,value in percentB.iteritems():
    #     if value < 0 and previous >= 0:
    #         signal.append(price[date]*0.99)
    #     else:
    #         signal.append(np.nan)
    #     previous = value
    #print(len(signal))
    return signal


def sc_import_data():
    start_time = cmd_output_start('Importing data...')

    global data
    data = pd.read_csv(
        test_path, usecols=['Time', 'Open', 'High', 'Low', 'Close', 'Instrument', 'Period'], sep=';',
        index_col=0, parse_dates=True).query('Period == 60')
    data['sma_20'] = ma(data['Close'], 20)
    for i in range(1, 4):
        data['upper_bb_' + str(i)], data['lower_bb_' + str(i)] = bb(data['Close'], data['sma_20'], 20, i)

    ema_slow = 5
    ema_fast = 10

    data['ema_2'] = data['Close'].ewm(span=ema_slow, adjust=False).mean()
    data['ema_5'] = data['Close'].ewm(span=ema_fast, adjust=False).mean()

    # true: alatta van, false: felette
    below_bb_2 = np.where(data['Low'] <= data['lower_bb_2'], True, False)
    above_bb_2 = np.where(data['High'] >= data['upper_bb_2'], True, False)
    above_sma_20 = np.where((data['Close'] >= data['sma_20']) & (data['Open'] >= data['sma_20']), True, False)
    below_sma_20 = np.where((data['Close'] <= data['sma_20']) & (data['Open'] <= data['sma_20']), True, False)


    #print(data)
    data["below_bb_2"] = below_bb_2
    data["above_bb_2"] = above_bb_2
    data["below_sma_20"] = below_sma_20
    data["above_sma_20"] = above_sma_20

    # fxdata = data.query('equal == False')

    # print(fxdata)

    # print(data)
    data['pv'] = second_touch_upper(data)
    print(data)
    cmd_output_end(start_time)


def sc_make_charts(time_frames_list):
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
            instrument.add_idosik(Idosik(TF))
            instrument.add_data(TF, fxdata)

            sma = fxdata[['sma_20']]
            bb_1 = fxdata[['lower_bb_1', 'upper_bb_1']]
            bb_2 = fxdata[['lower_bb_2', 'upper_bb_2']]
            bollinger = [
                mpf.make_addplot(sma, color='blue', linestyle='--', width=1),
                mpf.make_addplot(bb_1, color='blue', linestyle='-.', width=1),
                # mpf.make_addplot(bb_2, color = 'orange', linestyle = '-.', width = 1)
            ]
            ema_5 = fxdata[['ema_5']]
            ema_2 = fxdata[['ema_2']]
            colorgia = [
                mpf.make_addplot(sma, color='blue', linestyle='--', width=1),
                mpf.make_addplot(bb_2, color='orange', linestyle='-.', width=1),
                # mpf.make_addplot(ema_5, color='blue', linestyle='-', width=1),
                # mpf.make_addplot(ema_2, color='purple', linestyle='-', width=1),
                mpf.make_addplot(fxdata[['pv']], type='scatter')
            ]

            try:
                mpf.plot(fxdata, type='candle', style=sajat_style, addplot=colorgia,
                         savefig=charts_path + instrument.name + "_" + TF.name + "_" + str(candle_count))

            except Exception as e:
                print(e)
    cmd_output_end(start_time)

def sc_c_make_charts(time_frames_list):
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
                print(fxdata)
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
                    sma = t_fxdata[['sma_20']]
                    bb_1 = t_fxdata[['lower_bb_1', 'upper_bb_1']]
                    bb_2 = t_fxdata[['lower_bb_2', 'upper_bb_2']]
                    bollinger = [
                        mpf.make_addplot(sma, color='blue', linestyle='--', width=0.8),
                        mpf.make_addplot(bb_1, color='navy', linestyle='-.', width=0.8),
                        mpf.make_addplot(bb_2, color='orange', linestyle='-.', width=0.8)
                    ]
                    ema_5 = fxdata[['ema_5']]
                    ema_2 = fxdata[['ema_2']]
                    colorgia = [
                        mpf.make_addplot(sma, color='blue', linestyle='--', width=1),
                        mpf.make_addplot(bb_2, color='orange', linestyle='-.', width=1),
                        # mpf.make_addplot(ema_5, color='blue', linestyle='-', width=1),
                        # mpf.make_addplot(ema_2, color='purple', linestyle='-', width=1),
                        mpf.make_addplot(t_fxdata[['pv']], type='scatter')
                    ]

                    try:
                        mpf.plot(t_fxdata, type='candle', style=sajat_style, addplot=colorgia,
                             savefig=charts_path + instrument.name + "_" + TF.name + "_" + str(candle_count)
                                     + "_" + str(min) + "_" + str(max) + ".png")

                    except Exception as e:
                        print(e)

                    # mpf.plot(t_fxdata, type='candle', style=sajat_style, addplot=colorgia,
                    #                   savefig=charts_path + instrument.name + "_" + TF.name + "_" + str(candle_count)
                    #                           + "_" + str(min) + "_" + str(max) + ".png")

        cmd_output_end(start_time)

def sc_run():
    sc_get_instruments()
    sc_import_data()

    sc_c_make_charts(chart_time_frames)
