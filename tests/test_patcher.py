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
from __future__ import unicode_literals, print_function

import io
import json
import os
import shutil

import pytest

from pyupdater.client.patcher import Patcher

TEST_DATA_DIR = os.path.join(os.getcwd(), 'tests', 'test-data',
                             'patcher')

VERSION_DATA_DIR = os.path.dirname(TEST_DATA_DIR)
with io.open(os.path.join(VERSION_DATA_DIR, 'version.json'),
             encoding='utf-8') as f:
    version_data_str = f.read()

json_data = json.loads(version_data_str)


def cb(status):
    pass


def cb2(status):
    raise IndexError

update_data = {
    'name': 'Acme',
    'json_data': json_data,
    'current_filename': 'Acme-mac-4.1.tar.gz',
    'current_version': '4.1.0.2.0',
    'latest_version': '4.4.0.2.0',
    'update_folder': None,
    'update_urls': ['https://pyu-tester.s3.amazonaws.com/'],
    'platform': 'mac',
    'progress_hooks': [cb, cb2]
    }


@pytest.mark.usefixtures("cleandir")
class TestFails(object):

    @pytest.fixture
    def setup(self):
        directory = os.getcwd()
        base_binary = os.path.join(TEST_DATA_DIR, 'Acme-mac-4.1.tar.gz')
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
        data['latest_version'] = '0.0.4.2.0'
        p = Patcher(**data)
        assert p.start() is False


@pytest.mark.usefixtures("cleandir")
class TestExecution(object):

    @pytest.fixture
    def setup(self):
        directory = os.getcwd()
        base_binary = os.path.join(TEST_DATA_DIR, 'Acme-mac-4.1.tar.gz')
        shutil.copy(base_binary, directory)
        return directory

    def test_execution(self, setup):
        data = update_data.copy()
        data['update_folder'] = setup
        p = Patcher(**data)
        assert p.start() is True

    def test_execution_callback(self, setup):

        def cb(status):
            assert 'downloaded' in status.keys()
            assert 'total' in status.keys()
            assert 'status' in status.keys()
            assert 'percent_complete' in status.keys()

        data = update_data.copy()
        data['update_folder'] = setup
        data['progress_hooks'] = [cb]
        p = Patcher(**data)
        assert p.start() is True
