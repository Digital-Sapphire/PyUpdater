# ------------------------------------------------------------------------------
# Copyright (c) 2015-2019 Digital Sapphire
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the
# following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
# ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR
# ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.
# ------------------------------------------------------------------------------
import os
import tempfile
import threading

try:
    from http.server import SimpleHTTPRequestHandler as RequestHandler
except ImportError:
    from SimpleHTTPServer import SimpleHTTPRequestHandler as RequestHandler
try:
    import socketserver as SocketServer
except ImportError:
    import SocketServer

import pytest

from pyupdater import PyUpdater
from pyupdater.cli.options import make_parser
from pyupdater.client import Client
from pyupdater.core.key_handler.keys import Keys
from pyupdater.utils.config import ConfigManager
from pyupdater.utils.storage import Storage
from tconfig import TConfig


@pytest.fixture
def cleandir():
    new_path = tempfile.mkdtemp()
    os.chdir(new_path)


@pytest.fixture
def client():
    t_config = TConfig()
    t_config.DATA_DIR = os.getcwd()
    client = Client(t_config, refresh=True, test=True)
    client.FROZEN = True
    return client


@pytest.fixture
def create_keypack():
    keys = Keys(test=True)
    keys.make_keypack("test")


@pytest.fixture
def db():
    db = Storage()
    return db


@pytest.fixture
def loader():
    default_config = {
        "APP_NAME": "PyUpdater Test",
        "COMPANY_NAME": "ACME",
        "UPDATE_PATCHES": True,
    }

    cm = ConfigManager()
    config = cm.load_config()
    config.update(default_config)
    cm.save_config(config)
    return config


@pytest.fixture
def parser():
    parser = make_parser()
    return parser


@pytest.fixture
def pyu():
    t_config = TConfig()
    t_config.DATA_DIR = os.getcwd()
    pyu = PyUpdater(t_config)
    return pyu


@pytest.fixture
def simpleserver():
    class Server(object):
        def __init__(self):
            self.count = 0
            self._server = None

        def start(self, port=None):
            if port is None:
                raise ValueError("Port cannot be None.")
            self.count += 1
            if self._server is not None:
                return
            SocketServer.TCPServer.allow_reuse_address = True
            httpd = SocketServer.TCPServer(("", port), RequestHandler)

            self._server = threading.Thread(target=httpd.serve_forever)
            self._server.daemon = True
            self._server.start()

        def stop(self):
            self.count -= 1
            if self._server is not None and self.count == 0:
                self._server.alive = False
                self._server = None

    return Server()
