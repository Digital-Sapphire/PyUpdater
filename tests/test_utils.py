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
from __future__ import unicode_literals

import io
import os

import pytest

from pyupdater.utils import (check_repo,
                             create_asset_archive,
                             make_archive,
                             parse_platform,
                             remove_dot_files,
                             )
from pyupdater.utils.exceptions import UtilsError


@pytest.mark.usefixtures('cleandir')
class TestUtils(object):

    def test_make_archive(self):
        with io.open('hash-test1.txt', 'w', encoding='utf-8') as f:
            f.write('I should find some lorem text' * 11)

        with io.open('hash-test2.txt', 'w', encoding='utf-8') as f:
            f.write('I should find some lorem text' * 5)

        filename1 = make_archive('hash', 'hash-test1.txt', '0.2')
        filename2 = make_archive('hash', 'hash-test2.txt', '0.3')

        assert os.path.exists(filename1)
        assert os.path.exists(filename2)

    def test_create_asset_archive(self):
        with io.open('hash-test1.dll', 'w', encoding='utf-8') as f:
            f.write('I should find some lorem text' * 20)

        with io.open('hash-test2.so', 'w', encoding='utf-8') as f:
            f.write('I should find some lorem text' * 11)

        with io.open('binary', 'w', encoding='utf-8') as f:
            f.write('I should find some lorem text' * 5)

        filename = create_asset_archive('hash-test1.dll', '0.1')
        filename1 = create_asset_archive('hash-test2.so', '0.2')
        filename2 = create_asset_archive('binary', '0.3')

        assert os.path.exists(filename)
        assert os.path.exists(filename1)
        assert os.path.exists(filename2)

    def test_check_repo_fail(self):
        assert check_repo() is False


@pytest.mark.usefixtures('cleandir')
class TestUtils1(object):

    def test_parse_platform(self):
        assert parse_platform('app-mac-0.1.0.tar.gz') == 'mac'
        assert parse_platform('app-win-1.0.0.zip') == 'win'
        assert parse_platform('Email Parser-mac-0.2.0.tar.gz') == 'mac'
        assert parse_platform('Hangman-nix-0.0.1b1.zip') == 'nix'

    def test_parse_platform_fail(self):
        with pytest.raises(UtilsError):
            parse_platform('app-nex-1.0.0.tar.gz')

    def test_remove_dot_files(self):
        bad_list = ['.DS_Store', 'test', 'stuff', '.trash']
        good_list = ['test', 'stuff']
        for n in remove_dot_files(bad_list):
            assert n in good_list
