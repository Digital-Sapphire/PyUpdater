# --------------------------------------------------------------------------
# Copyright 2014-2016 Digital Sapphire Development Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# --------------------------------------------------------------------------
from __future__ import unicode_literals

import os

from pyupdater.utils.config import ConfigDict, Loader


class DevConfig(object):
    TESTING = True
    TEST_LOVE = True
    MORE_INFO = 'No Thanks'
    Bad_Attr = True


class ProdConfig(object):
    TESTING = False
    DEBUG = False
    MORE_INFO = 'Yes Please'


class BasicCofig(object):
    APP_NAME = 'Tester'
    COMPANY_NAME = 'Test App LLC'
    UPDATE_URLS = 'http://acme.com/updates'
    PUBLIC_KEYS = '838d88df8adkld8s9s'


def test_dev_config():
    config = ConfigDict()
    test_config = DevConfig()
    config.from_object(test_config)
    assert config['TESTING'] is True


def test_dev_config_bad_attr():
    config = ConfigDict()
    test_config = DevConfig()
    config.from_object(test_config)
    assert config.get('BAD_ATTR', None) is None


def test_prod_config():
    config = ConfigDict()
    prod_config = ProdConfig()
    config.from_object(prod_config)
    assert config['MORE_INFO'] == 'Yes Please'


def test_prod_bad_atter():
    config = ConfigDict()
    prod_config = ProdConfig()
    config.from_object(prod_config)
    assert config.get('DEBUG', None) is not None


def test_write_config(cleandir):
    config = ConfigDict()
    prod_config = ProdConfig()
    config.from_object(prod_config)
    l = Loader()
    l._write_config_py(config)
    assert 'client_config.py' in os.listdir(os.getcwd())
