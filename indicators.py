def moving_average(data, period):
    ma = data.rolling(window=period).mean()
    return ma


def bollinger_band(data, period, deviation):
    std = data.rolling(window=period).std()
    ma = moving_average(data, period)
    upper_bb = ma + std * deviation
    lower_bb = ma - std * deviation
    return upper_bb, lower_bb, ma


def exponential_moving_average(data, period):
    return data.ewm(span=period, adjust=False).mean()
