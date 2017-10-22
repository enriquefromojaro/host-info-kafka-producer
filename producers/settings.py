import os
import yaml

cwd = os.getcwd()

try:
    settings_file = open(os.path.join(cwd, 'producer-config.yml'), 'r')
    settings = yaml.load(settings_file)
except:
    settings = {
        'monitoring': {
            'cpu': {
                'interval': 20,
                'offline-interval': 0,
                'percpu': True,
                'cpu': -1
            }
        }
    }
del cwd
# del settings_file

if not settings.get('host_name'):
    settings['host_name'] = input('Enter your email, please: ')
if not settings.get('email'):
    settings['email'] = input('Enter your email, please: ')
