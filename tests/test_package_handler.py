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

from dsdev_utils.paths import ChDir
import pytest

from pyupdater import settings
from pyupdater.package_handler import PackageHandler
from pyupdater.package_handler.package import Patch, Package
from pyupdater.utils.config import Config
from pyupdater.utils.exceptions import PackageHandlerError
from tconfig import TConfig

s_dir = settings.USER_DATA_FOLDER
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'test data',
                             'package-handler')


@pytest.mark.usefixtures('cleandir', 'pyu')
class TestUtils(object):

    def test_init(self):
        data_dir = os.getcwd()
        t_config = TConfig()
        t_config.DATA_DIR = data_dir
        config = Config()
        config.from_object(t_config)
        p = PackageHandler(config)
        assert p.files_dir == os.path.join(data_dir, s_dir, 'files')
        assert p.deploy_dir == os.path.join(data_dir, s_dir, 'deploy')

    def test_no_patch_support(self):
        data_dir = os.getcwd()
        t_config = TConfig()
        t_config.DATA_DIR = data_dir
        t_config.UPDATE_PATCHES = False
        config = Config()
        config.from_object(t_config)
        p = PackageHandler(config)
        p.process_packages()


@pytest.mark.usefixtures('cleandir', 'pyu')
class TestExecution(object):

    def test_process_packages(self):
        data_dir = os.getcwd()
        t_config = TConfig()
        t_config.DATA_DIR = data_dir
        t_config.UPDATE_PATCHES = False
        config = Config()
        config.from_object(t_config)
        p = PackageHandler(config)
        p.process_packages()

    def test_process_packages_fail(self):
        with pytest.raises(PackageHandlerError):
            p = PackageHandler()
            p.process_packages()


@pytest.mark.usefixtures('cleandir')
class TestPackage(object):

    def test_package_1(self):
        test_file = 'Acme-mac-4.1.tar.gz'
        with ChDir(TEST_DATA_DIR):
            p1 = Package(test_file)

        assert p1.name == 'Acme'
        assert p1.version == '4.1.0.2.0'
        assert p1.filename == test_file
        assert p1.platform == 'mac'
        assert p1.channel == 'stable'
        assert p1.info['status'] is True

    def test_package_name_with_spaces(self):
        test_file = 'with spaces-nix-0.0.1b1.zip'
        with ChDir(TEST_DATA_DIR):
            p1 = Package(test_file)

        assert p1.name == 'with spaces'
        assert p1.version == '0.0.1.1.1'
        assert p1.filename == test_file
        assert p1.platform == 'nix'
        assert p1.channel == 'beta'
        assert p1.info['status'] is True


    def test_package_alpha(self):
        test_file = 'with spaces-win-0.0.1a2.zip'
        with ChDir(TEST_DATA_DIR):
            p1 = Package(test_file)

        assert p1.name == 'with spaces'
        assert p1.version == '0.0.1.0.2'
        assert p1.filename == test_file
        assert p1.platform == 'win'
        assert p1.channel == 'alpha'
        assert p1.info['status'] is True

    def test_package_ignored_file(self):
        with io.open('.DS_Store', 'w', encoding='utf-8') as f:
            f.write('')
        p = Package('.DS_Store')
        assert p.info['status'] is False

    def test_package_bad_extension(self):
        test_file_2 = 'pyu-win-0.0.2.bzip2'
        with ChDir(TEST_DATA_DIR):
            p2 = Package(test_file_2)

        assert p2.filename == test_file_2
        assert p2.name is None
        assert p2.version is None
        assert p2.info['status'] is False
        assert p2.info['reason'] == ('Not a supported archive format: '
                                     '{}'.format(test_file_2))

    def test_package_bad_version(self):
        with ChDir(TEST_DATA_DIR):
            p = Package('pyu-win-1.tar.gz')
        assert p.info['reason'] == 'Package version not formatted correctly'

    def test_package_bad_platform(self):
        with ChDir(TEST_DATA_DIR):
            p = Package('pyu-wi-1.1.tar.gz')
        assert p.info['reason'] == 'Package platform not formatted correctly'

    def test_package_missing(self):
        test_file_4 = 'jms-nix-0.0.3.tar.gz'
        with ChDir(TEST_DATA_DIR):
            Package(test_file_4)


@pytest.mark.usefixtures('cleandir')
class TestPatch(object):

    def test_patch(self):
        with io.open('app.py', 'w', encoding='utf-8') as f:
            f.write('a = 0')

        info = {
            'dst': 'app.py',
            'patch_name': 'p-name-1',
            'package': 'filename-mac-0.1.1.tar.gz'
            }
        p = Patch(info)
        assert p.ready is True

    def test_patch_bad_info(self):
        info = {
            'dst': 'app.py',
            'patch_name': 'p-name-1',
            'package': 'filename-mac-0.1.1.tar.gz'
            }
        temp_dst = info['dst']
        info['dst'] = None
        p = Patch(info)
        assert p.ready is False

        info['dst'] = temp_dst
        temp_patch = info['patch_name']
        info['patch_name'] = None
        p = Patch(info)
        assert p.ready is False

        info['patch_name'] = temp_patch
        info['package'] = None
        p = Patch(info)
        assert p.ready is False
