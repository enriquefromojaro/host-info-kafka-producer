from producers import producers
from producers.settings import settings
from concurrency.producersthreads import Producer

if __name__ == '__main__':
    print('------------------------------------------------------')
    print('----------Welcome to kofku producers!!----------------')
    print('------------------------------------------------------')
    print('host_name: ', settings.get('host_name'))
    print('email: ', settings.get('email'))
    print('------------------------------------------------------')
    monitor_settings = settings.get('monitoring', {})
    monitors = producers.MonitoringProducer.__subclasses__()
    tasks = []
    for topic, settings in monitor_settings.items():
        klazz = None
        for m in monitors:
            print(m.topic, topic)
            if m.topic == topic:
                klazz = m
        print('Klazz: ', klazz)
        if klazz:
            print('Added monitor {} for topic {}'.format(klazz, topic))
            tasks.append(Producer(klazz, topic, settings))

    print('Print Running tasks...')
    for t in tasks:
        t.start()
    print('Tasks started !!!')