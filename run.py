from producers import producers

if __name__ == '__main__':
    prod = producers.CPUProducer()
    producers.ProccessMonitorProducer().produce()