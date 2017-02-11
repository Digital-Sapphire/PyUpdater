from __future__ import print_function
import sys

from pyupdater.client import Client

import client_config

APPNAME = 'Acme'
VERSION = '4.1'


def cb(status):
    out = ''
    percent = status.get('percent_complete')
    time = status.get('time')
    if percent is not None:
        out += '{}%'.format(percent)
    if time is not None:
        out += ' - {}'.format(time)
    if len(out) == 0:
        out = 'Nothing yet...'
    sys.stdout.write('\r{}'.format(out))
    sys.stdout.flush()


def main():
    print(VERSION)
    data_dir= None
    config = client_config.ClientConfig()
    if getattr(config, 'USE_CUSTOM_DIR', False):
        data_dir = os.path.join(os.path.dirname(sys.executable), '.update')
    client = Client(config,
                    refresh=True, progress_hooks=[cb], data_dir=data_dir)
    update = client.update_check(APPNAME, VERSION)
    if update is not None:
        success = update.download()
        if success is True:
            print('Update download successful')
            print('Restarting')
            update.extract_restart()
        else:
            print('Failed to download update')
    return VERSION


if __name__ == '__main__':
    main()
