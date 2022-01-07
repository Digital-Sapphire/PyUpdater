# ------------------------------------------------------------------------------
# Copyright (c) 2015-2020 Digital Sapphire
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
import pathlib

from dsdev_utils.paths import ChDir
import pytest

from pyupdater import settings
from pyupdater.core.package_handler import PackageHandler
from pyupdater.core.package_handler.package import Package
from pyupdater.core.package_handler.patch import Patch


@pytest.mark.usefixtures("cleandir")
class TestPackageHandler(object):
    def test_init(self):
        p = PackageHandler(patch_support=True)
        data_dir = pathlib.Path.cwd() / settings.USER_DATA_FOLDER
        assert p.files_dir == str(data_dir / "files")
        assert p.deploy_dir == str(data_dir / "deploy")

    def test_no_patch_support(self):
        p = PackageHandler(patch_support=False)
        p.process_packages()

    def test_process_packages_empty(self):
        p = PackageHandler(patch_support=False)
        p.process_packages()

    def test_process_packages_new_stable(self):
        p = PackageHandler(patch_support=False)
        # create dummy archive file
        new_archive_version = "4.1"
        new_archive_name = f"Acme-mac-{new_archive_version}.tar.gz"
        new_archive_path = pathlib.Path(p.new_dir) / new_archive_name
        new_archive_path.touch()
        # process package
        p.process_packages()
        deploy_archive_path = pathlib.Path(p.deploy_dir) / new_archive_name
        assert deploy_archive_path.exists()
        assert new_archive_name in str(p.version_data[settings.UPDATES_KEY])
        assert new_archive_version in str(p.version_data[settings.LATEST_KEY])


@pytest.mark.usefixtures("cleandir")
class TestPackage(object):
    def test_package_1(self, shared_datadir):
        test_file = "Acme-mac-4.1.tar.gz"
        p1 = Package(shared_datadir / test_file)

        assert p1.name == "Acme"
        assert str(p1.version) == "4.1"
        assert p1.filename == test_file
        assert p1.platform == "mac"
        assert p1.channel == "stable"
        assert p1.info["status"] is True

    def test_package_name_with_spaces(self, shared_datadir):
        test_file = "with spaces-nix-0.0.1b1.zip"
        p1 = Package(shared_datadir / test_file)

        assert p1.name == "with spaces"
        assert str(p1.version) == "0.0.1b1"
        assert p1.filename == test_file
        assert p1.platform == "nix"
        assert p1.channel == "beta"
        assert p1.info["status"] is True

    def test_package_alpha(self, shared_datadir):
        test_file = "with spaces-win-0.0.1a2.zip"
        p1 = Package(shared_datadir / test_file)

        assert p1.name == "with spaces"
        assert str(p1.version) == "0.0.1a2"
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

    def test_package_only_major_version(self, shared_datadir):
        filename = "pyu-win-1.tar.gz"
        p = Package(shared_datadir / filename)
        assert p.info["reason"] == ""

    def test_package_bad_platform(self, shared_datadir):
        filename = "pyu-wi-1.1.tar.gz"
        p = Package(shared_datadir / filename)
        out = "failed to parse package filename"
        assert out in p.info["reason"].lower()


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
            "version_data": version_data,
            "pkg_info": pkg,
            "config": config,
            "test": True,
        }

        patch = Patch(**data)

        assert patch.ok
        assert config["patches"][pkg.name]

    def test_patch_fail(self):
        pass
