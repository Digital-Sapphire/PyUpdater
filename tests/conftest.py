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
