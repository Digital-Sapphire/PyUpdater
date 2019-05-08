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
from __future__ import unicode_literals

import os

from pyupdater.utils.config import Config, ConfigManager


class DevConfig(object):
    TESTING = True
    TEST_LOVE = True
    MORE_INFO = "No Thanks"
    Bad_Attr = True


class ProdConfig(object):
    TESTING = False
    DEBUG = False
    MORE_INFO = "Yes Please"


class BasicCofig(object):
    APP_NAME = "Tester"
    COMPANY_NAME = "Test App LLC"
    UPDATE_URLS = "http://acme.com/updates"
    PUBLIC_KEYS = "838d88df8adkld8s9s"


def test_dev_config():
    config = Config()
    test_config = DevConfig()
    config.from_object(test_config)
    assert config["TESTING"] is True


def test_dev_config_bad_attr():
    config = Config()
    test_config = DevConfig()
    config.from_object(test_config)
    assert config.get("BAD_ATTR", None) is None


def test_prod_config():
    config = Config()
    prod_config = ProdConfig()
    config.from_object(prod_config)
    assert config["MORE_INFO"] == "Yes Please"


def test_prod_bad_atter():
    config = Config()
    prod_config = ProdConfig()
    config.from_object(prod_config)
    assert config.get("DEBUG", None) is not None


def test_write_config(cleandir):
    config = Config()
    prod_config = ProdConfig()
    config.from_object(prod_config)
    cm = ConfigManager()
    cm.write_config_py(config)
    assert "client_config.py" in os.listdir(os.getcwd())
