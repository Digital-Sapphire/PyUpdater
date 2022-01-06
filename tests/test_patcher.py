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
from __future__ import unicode_literals, print_function
import json
import logging
import os

import pytest

from pyupdater.settings import UPDATES_KEY
from pyupdater.client.patcher import Patcher
from pyupdater.utils import PyuVersion


def cb1(status):
    pass


# Just throwing a monkey wrench into.
def cb2(status):
    raise IndexError


# noinspection PyStatementEffect,PyStatementEffect
@pytest.mark.usefixtures("cleandir")
class TestPatcher(object):
    @pytest.fixture
    def patcher_kwargs(self, shared_datadir):
        version_data_str = (shared_datadir / "version.json").read_text()
        kwargs = {
            "name": "Acme",
            "platform": "mac",
            "current_version": PyuVersion("4.1.0"),
            "latest_version": PyuVersion("4.4.0"),
            "version_data": json.loads(version_data_str),
            "update_folder": str(shared_datadir),
            "update_urls": ["https://pyu-tester.s3.amazonaws.com/"],
            "progress_hooks": [cb1, cb2],
        }
        return kwargs

    def test_fail_no_base_binary(self, patcher_kwargs, caplog):
        caplog.set_level(logging.DEBUG)
        assert os.listdir(os.getcwd()) == []
        patcher_kwargs["update_folder"] = os.getcwd()  # empty folder
        p = Patcher(**patcher_kwargs)
        assert p.start() is False
        assert "cannot find archive to patch" in caplog.text.lower()

    def test_fail_bad_hash_current_version(self, shared_datadir, patcher_kwargs, caplog):
        caplog.set_level(logging.DEBUG)
        patcher_kwargs["current_file_hash"] = "Thisisabadhash"
        p = Patcher(**patcher_kwargs)
        assert p.start() is False
        assert "binary hash mismatch" in caplog.text.lower()

    @pytest.mark.run(order=8)
    def test_fail_missing_version(self, shared_datadir, patcher_kwargs, caplog):
        caplog.set_level(logging.DEBUG)
        patcher_kwargs["latest_version"] = PyuVersion("5.0")
        p = Patcher(**patcher_kwargs)
        assert p.start() is False
        assert "filename missing in version file" in caplog.text.lower()

    @pytest.mark.run(order=7)
    def test_execution(self, shared_datadir, patcher_kwargs):
        p = Patcher(**patcher_kwargs)
        assert p.start() is True

    def test_execution_callback(self, shared_datadir, patcher_kwargs):
        def cb(status):
            assert "downloaded" in status.keys()
            assert "total" in status.keys()
            assert "status" in status.keys()
            assert "percent_complete" in status.keys()

        patcher_kwargs["progress_hooks"] = [cb]
        p = Patcher(**patcher_kwargs)
        assert p.start() is True


class TestPatcherInternals(object):
    @pytest.fixture
    def patcher_kwargs(self, version_manifest):
        kwargs = {
            "name": "Acme",
            "current_version": PyuVersion("1.0"),
            "latest_version": PyuVersion("1.2a0"),
            "version_data": version_manifest,
        }
        return kwargs

    def test__get_required_patches(self, patcher_kwargs):
        manifest = patcher_kwargs["version_data"]
        expected_versions = sorted(
            PyuVersion(key)
            for key in manifest[UPDATES_KEY]["Acme"]
            if PyuVersion(key) != patcher_kwargs["current_version"]
        )
        p = Patcher(**patcher_kwargs)
        assert p._get_required_patches() == expected_versions

    def test__get_patch_info(self, patcher_kwargs):
        p = Patcher(**patcher_kwargs)
        assert p._get_patch_info() is True

    def test__get_patch_info_no_versions(self, patcher_kwargs):
        patcher_kwargs["version_data"][UPDATES_KEY]["Acme"] = {}
        p = Patcher(**patcher_kwargs)
        assert p._get_patch_info() is False

    def test__get_patch_info_missing_patch(self, patcher_kwargs):
        for key in ["patch_hash", "patch_name", "patch_size"]:
            patcher_kwargs["version_data"][UPDATES_KEY]["Acme"]["1.1.0.1.0"]["win"].pop(key)
        p = Patcher(**patcher_kwargs)
        assert p._get_patch_info() is False

    @pytest.mark.parametrize("key", ["patch_size", "file_size"])
    def test__get_patch_info_fall_back(self, patcher_kwargs, key):
        patcher_kwargs["version_data"][UPDATES_KEY]["Acme"]["1.2.0.0.0"]["win"][key] = None
        p = Patcher(**patcher_kwargs)
        # should return False, as there are more than 4 required patches
        assert len(p._get_required_patches()) > 4
        assert p._get_patch_info() is False
