import json
import time

from monitors.cpu import CPUMonitor
from monitors.proccess import ProccessMonitor
from producers.settings import settings as global_settings
from kafka import KafkaProducer


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
    topic = 'cpu'
    def __init__(self, topic='cpu', settings=global_settings.get('monitoring', {}).get('cpu', {})):
        self.topic = topic
        self.settings = settings
        self.monitor = CPUMonitor()
        print('Kafka', global_settings['kafka'])
        self.kafka_producer = KafkaProducer(bootstrap_servers=global_settings['kafka'] , client_id=global_settings['host_name'])

    @property
    def _generator(self):
        percpu = self.settings.get('percpu', True)
        cpu = self.settings.get('cpu', -1)
        interval = self.settings.get('interval', 20)
        monitor = self.monitor

        def generator():
            while True:
                yield monitor.get_percentage(cpu, percpu)
                time.sleep(interval - 1)
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
        self.kafka_producer.send('cpu', result.encode())


class ProccessMonitorProducer(MonitoringProducer):
    topic = 'processes'

    def __init__(self, topic='processes', processes=global_settings['monitoring']['processes']):
        self.processes_m_data = processes['watch']
        self.processes_m_data = [dict(p, strikes=0) for p in self.processes_m_data]
        self.watched_list = []
        self.topic = topic
        self.interval = processes['interval']
        self.states_producer = KafkaProducer(bootstrap_servers=global_settings['kafka'],
                                            client_id=global_settings['host_name'], acks='all', retries=2)
        # self.soft_states_producer = KafkaProducer(bootstrap_servers=global_settings['kafka'],
        #                                           client_id=global_settings['host_name'])
        self.monitor = ProccessMonitor()
        self.monitoring = self.monitor.associate_to_list(self.processes_m_data.copy())
        for m in self.monitoring:
            self.handle(m)

    def handle(self, element):
        state_runing = {
            True: 'UP',
            False: 'DOWN'
        }
        event_type = 'SOFT'
        now = time.time()
        # 1st time
        # By default, we assume that the initial hard state is the opposite to the given one,
        #  so we can assure the change when it is confirmed
        if 'hard_state' not in element:
            element['hard_state'] = state_runing[not element['running']]
            element['strikes'] = 0
            element['hard_state_timestamp'] = now
        # if current state is the same that the hard, we reset the strikes
        if element['hard_state'] == state_runing[element['running']]:
            element['strikes'] = 0
        else:
            n = element['strikes']
            element['strikes'] = (n+1) % (element['notification-attempts']+1)
            print('different: {hard_state} --> {running} ({strikes} attempts)'.format(**element))
            # hard state change!!
            if element['strikes'] == 0:
                print('HARD!!!!!!!!!!!!!!!')
                event_type = 'HARD'
                element['hard_state_timestamp'] = now
                element['hard_state'] = state_runing[element['running']]
        data = {
            'type': event_type,
            'state': state_runing[element['running']],
            'hard_state': element['hard_state'],
            'hard_state_timestamp': element['hard_state_timestamp'],
            'process': element['command'],
            'display_name': element['display_name'],
            'timestamp': now,
            'host_name': global_settings['host_name'],
            'email': global_settings['email']
        }

        print("Data: ", data)
        self.states_producer.send('processes', json.dumps(data).encode('utf-8'), partition=int(data['type'] == 'HARD'))

    @property
    def _generator(self):
        while True:
            for i in range(len(self.monitoring)):
                if self.monitoring[i].get('process'):
                    del self.monitoring[i]['process']
            self.monitoring = self.monitor.associate_to_list(self.monitoring)
            for m in self.monitoring:
                yield m
            time.sleep(self.interval)