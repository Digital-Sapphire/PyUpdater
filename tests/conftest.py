# --------------------------------------------------------------------------
# Copyright (c) 2016 Digital Sapphire
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
# --------------------------------------------------------------------------
import os
import tempfile

import pytest

from pyupdater import PyUpdater
from pyupdater.cli.options import make_parser
from pyupdater.client import Client
from pyupdater.key_handler.keys import Keys
from pyupdater.utils.config import Loader
from pyupdater.utils.storage import Storage
from tconfig import TConfig


@pytest.fixture
def cleandir():
    newpath = tempfile.mkdtemp()
    os.chdir(newpath)


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
    keys.make_keypack('test')


@pytest.fixture
def db():
    db = Storage()
    return db


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
def loader():
    CONFIG = {
        'APP_NAME': 'PyUpdater Test',
        'COMPANY_NAME': 'ACME',
        'UPDATE_PATCHES': True,
        }

    l = Loader()
    config = l.load_config()
    config.update(CONFIG)
    l.save_config(config)
    return config
