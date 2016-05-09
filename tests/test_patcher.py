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

import json
import os
import shutil
try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen

import pytest
import six

from pyupdater.client.patcher import Patcher

TEST_DATA_DIR = os.path.join(os.getcwd(), 'tests', 'test data',
                             'patcher-test-data')

version_file_url = ('https://s3-us-west-1.amazonaws.com/pyupdater-test'
                    '/version.json')

version_data_str = urlopen(version_file_url).read()
if six.PY3:
    version_data_str = version_data_str.decode()

json_data = json.loads(version_data_str)


def cb(status):
    pass


def cb2(status):
    raise IndexError

update_data = {
    'name': 'jms',
    'json_data': json_data,
    'current_version': '0.0.1',
    'highest_version': '0.0.3',
    'update_folder': None,
    'update_urls': ['https://s3-us-west-1.amazonaws.com/pyupdater-test/'],
    'platform': 'mac',
    'progress_hooks': [cb, cb2]
    }


@pytest.mark.usefixtures("cleandir")
class TestPatcher(object):

    @pytest.fixture
    def setup(self):
        directory = os.getcwd()
        base_binary = os.path.join(TEST_DATA_DIR, 'jms-mac-0.0.1.zip')
        shutil.copy(base_binary, directory)
        return directory

    def test_no_base_binary(self):
        assert os.listdir(os.getcwd()) == []
        data = update_data.copy()
        data['update_folder'] = os.getcwd()
        p = Patcher(**data)
        assert p.start() is False

    def test_bad_hash_current_version(self, setup):
        data = update_data.copy()
        data['update_folder'] = setup
        data['current_file_hash'] = 'Thisisabadhash'
        p = Patcher(**data)
        assert p.start() is False

    def test_missing_version(self, setup):
        data = update_data.copy()
        data['update_folder'] = setup
        data['highest_version'] = '0.0.4'
        p = Patcher(**data)
        assert p.start() is False

    # def test_execution(self, setup):
    #     data = update_data.copy()
    #     data['update_folder'] = setup
    #     p = Patcher(**data)
    #     assert p.start() is True
