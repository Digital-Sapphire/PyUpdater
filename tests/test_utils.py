# --------------------------------------------------------------------------
# Copyright 2014 Digital Sapphire Development Team
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

import io
import os

import pytest

from pyupdater.utils import (check_repo,
                             EasyAccessDict,
                             get_hash,
                             get_mac_dot_app_dir,
                             get_package_hashes,
                             make_archive,
                             parse_platform,
                             remove_dot_files,
                             Version
                             )
from pyupdater.utils.exceptions import UtilsError, VersionError


@pytest.mark.usefixtures('cleandir')
class TestUtils(object):

    def test_archive(self):
        with io.open('hash-test1.txt', 'w', encoding='utf-8') as f:
            f.write('I should find some lorem text' * 20)
        with io.open('hash-test2.txt', 'w', encoding='utf-8') as f:
            f.write('I should find some lorem text' * 11)
        with io.open('hash-test3.txt', 'w', encoding='utf-8') as f:
            f.write('I should find some lorem text' * 5)
        filename = make_archive('hash', 'hash-test1.txt', '0.1', external=True)
        filename1 = make_archive('hash', 'hash-test2.txt', '0.2',
                                 external=True)
        filename2 = make_archive('hash', 'hash-test3.txt', '0.3',
                                 external=True)
        assert os.path.exists(filename)
        assert os.path.exists(filename1)
        assert os.path.exists(filename2)

    def test_check_repo_fail(self):
        assert check_repo() is False

    def test_package_hash(self):
        with io.open('hash-test.txt', 'w', encoding='utf-8') as f:
            f.write('I should find some lorem text' * 123)

        digest = ('cb44ec613a594f3b20e46b768c5ee780e0a9b66ac'
                  '6d5ac1468ca4d3635c4aa9b')
        assert digest == get_package_hashes('hash-test.txt')

    def test_get_hash(self):
        digest = ('380fd2bf3d78bb411e4c1801ce3ce7804bf5a22d79'
                  '405d950e5d5c8f3169fca0')
        assert digest == get_hash('Get this hash please')

    def test_get_mac_app_dir(self):
        main = 'Main'
        path = os.path.join(main, 'Contents', 'MacOS', 'app')
        assert get_mac_dot_app_dir(path) == main


@pytest.mark.usefixtures('cleandir')
class TestUtils1(object):

    def test_easy_access_dict(self):
        good_data = {'test': True}
        easy = EasyAccessDict()
        assert easy('bad-key') is None
        good_easy = EasyAccessDict(good_data)
        assert good_easy.get('test') is True
        assert good_easy.get('no-test') is None

    def test_parse_platform(self):
        assert parse_platform('app-mac-0.1.0.tar.gz') == 'mac'
        assert parse_platform('app-win-1.0.0.zip') == 'win'
        assert parse_platform('Email Parser-mac-0.2.0.tar.gz') == 'mac'

    def test_parse_platform_fail(self):
        with pytest.raises(UtilsError):
            parse_platform('app-nex-1.0.0.tar.gz')

    def test_remove_dot_files(self):
        bad_list = ['.DS_Store', 'test', 'stuff', '.trash']
        good_list = ['test', 'stuff']
        for n in remove_dot_files(bad_list):
            assert n in good_list

    def test_version_short(self):
        assert Version('1.1') > Version('1.1beta1')
        assert Version('1.2.1beta1') < Version('1.2.1')
        assert Version('1.2.1alpha1') < Version('1.2.1alpha2')

    def test_version_full(self):
        assert Version('1.1') > Version('1.1b1')
        assert Version('1.2.1b1') < Version('1.2.1')
        assert Version('1.2.1a1') < Version('1.2.1a2')

    def test_version(self):
        assert Version('5.0') == Version('5.0')
        assert Version('4.5') != Version('5.1')
        with pytest.raises(VersionError):
            Version('1')
        with pytest.raises(VersionError):
            Version('1.1.1.1')
