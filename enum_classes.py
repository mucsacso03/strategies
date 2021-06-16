import enum


class Signals(enum.IntEnum):
    Sell = 0
    Buy = 1


class TimeFrames(enum.IntEnum):
    # M1 = 1
    # M5 = 5
    # M15 = 15
    # M30 = 30
    H1 = 60
    H4 = 240
    D1 = 1440
    W1 = 10080
    MN = 43200
