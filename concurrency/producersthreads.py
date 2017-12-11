import threading

class Producer(threading.Thread):
    def __init__(self, producer_class, *args, **kwargs):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.producer = producer_class(*args, **kwargs)

    def stop(self):
        self.stop_event.set()

    def run(self):
        self.producer.produce()