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
import os

import pytest
from dsdev_utils.system import get_system

from pyupdater import PyUpdater
from pyupdater.utils.config import Config
from tconfig import TConfig


def create_build_cmd(version):
    cmd = ['build', '--app-name', 'myapp', '--app-version',
           '0.1.{}'.format(version), 'app.py', '-F']
    return cmd

if get_system() == 'win':
    ext = '.zip'
else:
    ext = '.tar.gz'


@pytest.mark.usefixtures('cleandir', 'create_keypack', 'pyu')
class TestUtils(object):

    def test_setup(self):
        data_dir = os.getcwd()
        pyu_data_dir = os.path.join(data_dir, 'pyu-data')
        t_config = TConfig()
        t_config.DATA_DIR = data_dir
        pyu = PyUpdater(t_config)
        pyu.setup()
        assert os.path.exists(pyu_data_dir)
        assert os.path.exists(os.path.join(pyu_data_dir, 'deploy'))
        assert os.path.exists(os.path.join(pyu_data_dir, 'files'))
        assert os.path.exists(os.path.join(pyu_data_dir, 'new'))


@pytest.mark.usefixtures('cleandir', 'create_keypack', 'pyu')
class TestExecution(object):

    def test_execution_patch(self, pyu):

        def gen_archive_name(version):
            archive_name = 'myapp-{}-0.1.{}{}'.format(get_system(),
                                                      version, ext)
            return archive_name

        # ToDo: Add pre-generated archives to test with
        pass
