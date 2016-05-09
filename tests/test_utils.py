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

import io
import os

import pytest

from pyupdater.utils import (check_repo,
                             get_hash,
                             make_archive,
                             parse_platform,
                             remove_dot_files,
                             )
from pyupdater.utils.exceptions import UtilsError


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

    def test_get_hash(self):
        digest = ('380fd2bf3d78bb411e4c1801ce3ce7804bf5a22d79'
                  '405d950e5d5c8f3169fca0')
        assert digest == get_hash('Get this hash please')


@pytest.mark.usefixtures('cleandir')
class TestUtils1(object):

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
