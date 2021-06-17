

def ma(data, window):
    ma = data.rolling(window=window).mean()
    return ma


def bb(data, ma, window, deviation):
    std = data.rolling(window=window).std()
    upper_bb = ma + std * deviation
    lower_bb = ma - std * deviation
    return upper_bb, lower_bb


# def bollingers():
#     # calculate and append bollinger data to database
#     data['ma_20'] = ma(data['Close'], 20)
#     for i in range(1, 4):
#         data['upper_bb_' + str(i)], data['lower_bb_' + str(i)] = bb(data['Close'], data['ma_20'], 20, i)
#
#
def ema(data, period):
        return data.ewm(span=period, adjust=False).mean()
