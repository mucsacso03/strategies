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
