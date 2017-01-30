from __future__ import print_function
import logging

from pyupdater.client import Client

import client_config

APPNAME = 'Acme'
VERSION = '4.2'

log = logging.getLogger()


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
