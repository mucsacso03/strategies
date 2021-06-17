import operator

from class_dimbesdombos import Dimbesdombos
from constants import *
from enum_classes import *
from indicators import *
from run_timer import *


def dimbesdombos(fxdata, long, instrument, timeframe, quiet):
    if not quiet: start_time = cmd_output_start('Calculating DimbesDombos for ' + instrument + '...')

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
        if len(peak_or_valleys) == 2:
            first = peak_or_valleys[i]
            second = peak_or_valleys[i + 1]
            if relation_operator(second.value, first.value):  # first.value > second.value:
                signals.append(second)

    if not quiet: cmd_output_end(start_time)
    # print(signals)
    return signals





def dd_make_charts(time_frames_list, instruments, data, quiet):
    start_time = cmd_output_start('Initializing charts...')

    signals = []

    for TF in time_frames_list:
        for instrument in instruments:
            # print('Making chart: ' + instrument.name)
            fxdata = data.query('Instrument == "' + instrument.name + '" and Period == ' + str(TF.value)).tail(
                CANDLE_COUNT)
            fxdata['ma_20'] = ma(fxdata['Close'], 20)
            fxdata['ema_200'] = ema(fxdata['Close'], 200)

            signals.append(dimbesdombos(fxdata, True, instrument.name, TF, quiet))
            signals.append(dimbesdombos(fxdata, False, instrument.name, TF, quiet))

    cmd_output_end(start_time)

    return signals
