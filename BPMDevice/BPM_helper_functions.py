

class Accumulator:
    """Uses camonitor to accumulate a set number of data points from a PV 
    
        Args:
            pv (str): The process variable requested.
            count (int): the number of sample to accuire.
            
        Returns:
            A list of raw timestamp tuples and values
            """
    def __init__(self, pv, count):
        self.count = count
        self.accum = []
        self.done = cothread.Event()
        self.monitor = camonitor(pv, self.add_value, format=FORMAT_TIME, all_updates=True)

    def add_value(self, val):
        self.accum.append((val.raw_stamp, val))
        if len(self.accum) >= self.count:
            self.monitor.close()
            self.done.Signal()

    def wait(self):
        self.done.Wait()
        data = zip(*self.accum)
        raw_time_series = data[0]
        time_series = []
        for nd in range(len(raw_time_series)):
            time_series.append(raw_time_series[nd][0] + raw_time_series[nd][1] * 1e-9)
        return time_series, data[1]
