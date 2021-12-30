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

from pyupdater.client.patcher import Patcher
from pyupdater.utils import PyuVersion


def cb1(status):
    pass


# Just throwing a monkey wrench into.
def cb2(status):
    raise IndexError


update_data = {
    "name": "Acme",
    "current_filename": "Acme-mac-4.1.tar.gz",
    "current_version": PyuVersion("4.1.0"),
    "latest_version": PyuVersion("4.4.0"),
    "channel": "stable",
    "update_folder": None,
    "update_urls": ["https://pyu-tester.s3.amazonaws.com/"],
    "platform": "mac",
    "progress_hooks": [cb1, cb2],
}


# noinspection PyStatementEffect,PyStatementEffect
@pytest.mark.usefixtures("cleandir")
class TestFails(object):

    base_binary = "Acme-mac-4.1.tar.gz"

    @pytest.fixture
    def version_data(self, shared_datadir):
        version_data_str = (shared_datadir / "version.json").read_text()
        return json.loads(version_data_str)

    def test_no_base_binary(self, version_data, caplog):
        caplog.set_level(logging.DEBUG)
        assert os.listdir(os.getcwd()) == []
        data = update_data.copy()
        data["update_folder"] = os.getcwd()
        data["version_data"] = version_data
        p = Patcher(**data)
        assert p.start() is False
        assert "cannot find archive to patch" in caplog.text.lower()

    def test_bad_hash_current_version(self, shared_datadir, version_data, caplog):
        caplog.set_level(logging.DEBUG)
        data = update_data.copy()
        data["update_folder"] = str(shared_datadir)
        data["version_data"] = version_data
        data["current_file_hash"] = "Thisisabadhash"
        p = Patcher(**data)
        assert p.start() is False
        assert "binary hash mismatch" in caplog.text.lower()

    @pytest.mark.run(order=8)
    def test_missing_version(self, shared_datadir, version_data, caplog):
        caplog.set_level(logging.DEBUG)
        data = update_data.copy()
        data["update_folder"] = str(shared_datadir)
        data["version_data"] = version_data
        data["latest_version"] = PyuVersion("0.0.4")
        p = Patcher(**data)
        assert p.start() is False
        assert "filename missing in version file" in caplog.text.lower()


# noinspection PyStatementEffect,PyStatementEffect
@pytest.mark.usefixtures("cleandir")
class TestExecution(object):

    base_binary = "Acme-mac-4.1.tar.gz"

    @pytest.fixture
    def version_data(self, shared_datadir):
        version_data_str = (shared_datadir / "version.json").read_text()
        return json.loads(version_data_str)

    @pytest.mark.run(order=7)
    def test_execution(self, shared_datadir, version_data):
        data = update_data.copy()
        data["update_folder"] = str(shared_datadir)
        data["version_data"] = version_data
        data["channel"] = "stable"
        p = Patcher(**data)
        assert p.start() is True

    def test_execution_callback(self, shared_datadir, version_data):
        def cb(status):
            assert "downloaded" in status.keys()
            assert "total" in status.keys()
            assert "status" in status.keys()
            assert "percent_complete" in status.keys()

        data = update_data.copy()
        data["update_folder"] = str(shared_datadir)
        data["version_data"] = version_data
        data["progress_hooks"] = [cb]
        p = Patcher(**data)
        assert p.start() is True
