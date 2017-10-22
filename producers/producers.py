import json
import time

from monitors.cpu import CPUMonitor
from producers.settings import settings as global_settings
from kafka import  KafkaProducer


class MonitoringProducer():
    topic = 'general'

    def __init__(self):
        pass

    def produce(self):
        for i in self._generator:
            self.handle(i)

    def handle(self, element):
        raise NotImplementedError

    @property
    def _generator(self):
        raise NotImplementedError

    def handle(self, generated):
        raise NotImplementedError


class CPUProducer(MonitoringProducer):

    def __init__(self, topic='cpu', settings=global_settings['monitoring']['cpu']):
        self.topic = topic
        self.settings = settings
        self.monitor = CPUMonitor()
        self.kafka_producer = KafkaProducer(bootstrap_servers='192.168.1.49', client_id=global_settings['host_name'])

    @property
    def _generator(self):
        percpu = self.settings.get('percpu', True)
        cpu = self.settings.get('cpu', -1)
        interval = self.settings.get('interval', 20)
        monitor = self.monitor

        def generator():
            while True:
                yield monitor.get_percentage(cpu, percpu)
                time.sleep(interval -1)
        return generator()

    def handle(self, element):
        result = {
            'host_name': global_settings['host_name'],
            'email': global_settings['email'],
            'timestamp': int(time.time()),
            'data': [element] if isinstance(element, (int, float)) else element,
            'percpu': self.settings['percpu'],
            'cpu': self.settings['cpu']
        }
        result = json.dumps(result)
        print('CPU: ', result)
        self.kafka_producer.send('CPU', result.encode())
        print('Sent to kafka')


if __name__ == '__main__':
    print('Welcome to Kofku!!')

    CPUProducer().produce()
