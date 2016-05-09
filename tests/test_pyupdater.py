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
import os

import pytest
from jms_utils.system import get_system

from pyupdater import PyUpdater
from pyupdater.utils.config import ConfigDict
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

    def test_dev_dir_none(self):
        myconfig = TConfig()
        myconfig.APP_NAME = None
        updater = ConfigDict()
        updater.from_object(myconfig)
        assert updater['APP_NAME'] == 'PyUpdater App'

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
