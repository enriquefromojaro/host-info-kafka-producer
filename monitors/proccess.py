import psutil
from collections import defaultdict

import time


class ProccessMonitor(object):

    def associate_to_list(self, lst):
        def is_proccess(proc, data):
            comparators = {
                'command': lambda x, y: x.get('command') and x['command'] == y.info['name'],
                'username': lambda x, y: x.get('username') and x['username'] == y.info['username'],
                'cmd_arguments': lambda x, y: x.get('cmd_arguments') and all(x in y.cmdline() for x in x['cmd_arguments'])
            }
            matches = all(comparators.get(k, lambda x,y:True)(data, proc) for k in data.keys() if k in comparators)
            if matches:
                lst.remove(data)
            return matches

        candidates = [
            dict(next((el for el in lst if is_proccess(p, el)), {}), proccess=p)
            for p in psutil.process_iter(['username', 'pid', 'cmdline', 'name', 'status'])
        ]
        print('Candidates : ', len(candidates))
        candidates = [c for c in candidates if len(c.keys()) > 1]
        print('Candidates : ', len(candidates))
        for p in candidates:
            print(p['proccess'].info)
        result = candidates + lst #matching processes + non matching processes
        result = [
            dict(r,
                 running=bool(r.get('proccess') and r['proccess'].is_running()
                         and r['proccess'].status() != psutil.STATUS_ZOMBIE),
             )
            for r in result
        ]
        return result