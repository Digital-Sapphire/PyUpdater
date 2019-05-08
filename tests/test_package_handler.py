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

import io
import os

from dsdev_utils.paths import ChDir
import pytest

from pyupdater import settings
from pyupdater.core.package_handler import PackageHandler
from pyupdater.core.package_handler.package import Package, parse_platform
from pyupdater.core.package_handler.patch import Patch
from pyupdater.utils.config import Config
from pyupdater.utils.exceptions import PackageHandlerError

from tconfig import TConfig

user_data_dir = settings.USER_DATA_FOLDER


@pytest.mark.usefixtures("cleandir", "pyu")
class TestUtils(object):
    def test_init(self):
        data_dir = os.getcwd()
        t_config = TConfig()
        t_config.DATA_DIR = data_dir
        config = Config()
        config.from_object(t_config)
        p = PackageHandler(config)
        assert p.files_dir == os.path.join(data_dir, user_data_dir, "files")
        assert p.deploy_dir == os.path.join(data_dir, user_data_dir, "deploy")

    def test_no_patch_support(self):
        data_dir = os.getcwd()
        t_config = TConfig()
        t_config.DATA_DIR = data_dir
        t_config.UPDATE_PATCHES = False
        config = Config()
        config.from_object(t_config)
        p = PackageHandler(config)
        p.process_packages()

    def test_parse_platform(self):
        assert parse_platform("app-mac-0.1.0.tar.gz") == "mac"
        assert parse_platform("app-win-1.0.0.zip") == "win"
        assert parse_platform("Email Parser-mac-0.2.0.tar.gz") == "mac"
        assert parse_platform("Hangman-nix-0.0.1b1.zip") == "nix"

    def test_parse_platform_fail(self):
        with pytest.raises(PackageHandlerError):
            parse_platform("app-nex-1.0.0.tar.gz")


@pytest.mark.usefixtures("cleandir", "pyu")
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


@pytest.mark.usefixtures("cleandir")
class TestPackage(object):
    def test_package_1(self, shared_datadir):
        test_file = "Acme-mac-4.1.tar.gz"
        p1 = Package(shared_datadir / test_file)

        assert p1.name == "Acme"
        assert p1.version == "4.1.0.2.0"
        assert p1.filename == test_file
        assert p1.platform == "mac"
        assert p1.channel == "stable"
        assert p1.info["status"] is True

    def test_package_name_with_spaces(self, shared_datadir):
        test_file = "with spaces-nix-0.0.1b1.zip"
        p1 = Package(shared_datadir / test_file)

        assert p1.name == "with spaces"
        assert p1.version == "0.0.1.1.1"
        assert p1.filename == test_file
        assert p1.platform == "nix"
        assert p1.channel == "beta"
        assert p1.info["status"] is True

    def test_package_alpha(self, shared_datadir):
        test_file = "with spaces-win-0.0.1a2.zip"
        p1 = Package(shared_datadir / test_file)

        assert p1.name == "with spaces"
        assert p1.version == "0.0.1.0.2"
        assert p1.filename == test_file
        assert p1.platform == "win"
        assert p1.channel == "alpha"
        assert p1.info["status"] is True

    def test_package_ignored_file(self):
        with io.open(".DS_Store", "w", encoding="utf-8") as f:
            f.write("")
        p = Package(".DS_Store")
        assert p.info["status"] is False

    def test_package_bad_extension(self, shared_datadir):
        test_file_2 = "pyu-win-0.0.2.xz"
        p2 = Package(shared_datadir / test_file_2)

        assert p2.filename == test_file_2
        assert p2.name is None
        assert p2.version is None
        assert p2.info["status"] is False
        assert p2.info["reason"] == (
            "Not a supported archive format: " "{}".format(test_file_2)
        )

    def test_package_bad_version(self, shared_datadir):
        filename = "pyu-win-1.tar.gz"
        p = Package(shared_datadir / filename)
        out = "Package version not formatted correctly: {}"
        assert p.info["reason"] == out.format(filename)

    def test_package_bad_platform(self, shared_datadir):
        filename = "pyu-wi-1.1.tar.gz"
        p = Package(shared_datadir / filename)
        out = "Package platform not formatted correctly"
        assert p.info["reason"] == out


@pytest.mark.usefixtures("cleandir")
class TestPatch(object):
    new_dir = "pyu-data/new"
    files_dir = "pyu-data/files"

    @pytest.fixture
    def patch_setup(self):
        os.makedirs(self.new_dir)
        os.makedirs(self.files_dir)

        with open(os.path.join(self.new_dir, "Acme-mac-4.2.tar.gz"), "w") as f:
            f.write("v2")

        with open(os.path.join(self.files_dir, "Acme-mac-4.1.tar.gz"), "w") as f:
            f.write("v1")

    def test_patch(self, patch_setup):
        filename = "Acme-mac-4.2.tar.gz"

        with ChDir(self.new_dir):
            full_path = os.path.abspath(filename)
            pkg = Package(full_path)

        config = {}
        version_data = {}
        data = {
            "filename": full_path,
            "files_dir": self.files_dir,
            "new_dir": self.new_dir,
            "json_data": version_data,
            "pkg_info": pkg,
            "config": config,
            "test": True,
        }

        patch = Patch(**data)

        assert patch.ok
        assert config["patches"][pkg.name]

    def test_patch_fail(self):
        pass
