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
import sys

from dsdev_utils.system import get_system
import pytest

from pyupdater.builder import ExternalLib
from pyupdater.utils.config import Loader


CONFIG = {
    'APP_NAME': 'PyUpdater Test',
    'COMPANY_NAME': 'ACME',
    'UPDATE_PATCHES': True,

}

if sys.platform == 'win32':
    EXT = '.zip'
else:
    EXT = '.tar.gz'


@pytest.mark.usefixtures("cleandir",)
class TestBuilder(object):

    def test_build(self):
        l = Loader()
        config = l.load_config()
        config.update(CONFIG)
        l.save_config(config)


@pytest.mark.usefixtures("cleandir",)
class TestExternalLib(object):

    def test_archive(self):
        with io.open('test', 'w', encoding='utf-8') as f:
            f.write('this is a test')
        ex = ExternalLib('test', '0.1')
        ex.archive()
        assert os.path.exists('test-{}-0.1{}'.format(get_system(), EXT))
