import psutil

class CPUMonitor:

    def __init__(self):
        pass

    def get_percentage(self, cpu:int=None, per_cpu:bool=True, interval:int=1):
        result = psutil.cpu_times_percent(interval, per_cpu)
        return result if cpu is None else result[cpu]