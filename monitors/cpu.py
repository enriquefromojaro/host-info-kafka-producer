import psutil


class CPUMonitor:

    def __init__(self):
        self.num_cpus = psutil.cpu_count()

    def get_percentage(self, cpu:int=None, per_cpu:bool=True, interval:int=1):
        result = psutil.cpu_percent(interval, per_cpu)
        return result if not per_cpu or cpu is None or cpu < 0 or self.num_cpus <= cpu else result[cpu]