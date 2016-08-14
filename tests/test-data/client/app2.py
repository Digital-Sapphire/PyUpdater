from __future__ import print_function
import logging
import sys

from pyupdater.client import Client

import client_config

APPNAME = 'Acme'
VERSION = '4.2'

log = logging.getLogger()


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
    client = Client(client_config.ClientConfig(), refresh=True)
    update = client.update_check(APPNAME, VERSION)
    if update is not None:
        update.download()
        update.extract_overwrite()

    return VERSION


if __name__ == '__main__':
    main()
