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
from __future__ import print_function
from __future__ import unicode_literals

import json
import os
import time

from dsdev_utils.helpers import EasyAccessDict
from dsdev_utils.system import get_system
from dsdev_utils.paths import ChDir, remove_any
import pytest
import six

from pyupdater.client import Client
from pyupdater.client.updates import gen_user_friendly_version, get_highest_version
from tconfig import TConfig


@pytest.mark.usefixtures("cleandir", "client")
class TestSetup(object):
    def test_data_dir(self, client):
        assert os.path.exists(client.data_dir)

    def test_new_init(self, client):
        assert client.app_name == "Acme"
        assert client.update_urls[0] == (
            "https://s3-us-west-1.amazon" "aws.com/pyu-tester/"
        )

    def test_no_cert(self, client):
        client.verify = False
        assert client.app_name == "Acme"
        assert client.update_urls[0] == (
            "https://s3-us-west-1.amazon" "aws.com/pyu-tester/"
        )

    def test_bad_pub_key(self):
        t_config = TConfig()
        # If changed ensure it's a valid key format
        t_config.PUBLIC_KEY = "25RSdhJ+xCsxxTjY5jffilatipp29tnKp/D5BelSMJM"
        t_config.DATA_DIR = os.getcwd()
        client = Client(t_config, refresh=True, test=True)
        assert client.update_check(client.app_name, "0.0.0") is None

    def test_check_version(self, client):
        assert client.update_check(client.app_name, "6.0.0") is None
        assert client.update_check(client.app_name, "3.0") is not None
        client.ready = False
        assert client.update_check(client.app_name, "0.0.2") is None

    def test_callback(self):
        def cb(status):
            print(status)

        def cb2(status):
            raise IndexError

        t_config = TConfig()
        t_config.PUBLIC_KEY = "25RSdhJ+xCsxxTjY5jffilatipp29tnKp/D5BelSMJM"
        t_config.DATA_DIR = os.getcwd()
        client = Client(t_config, refresh=True, test=True, progress_hooks=[cb])
        client.add_progress_hook(cb2)
        assert client.update_check(client.app_name, "0.0.0") is None

    def test_manifest_filesystem(self):
        t_config = TConfig()
        t_config.DATA_DIR = os.getcwd()
        client = Client(t_config, refresh=True, test=True)
        filesystem_data = client._get_manifest_from_disk()
        assert filesystem_data is not None
        if six.PY3:
            filesystem_data = filesystem_data.decode()
        filesystem_data = json.loads(filesystem_data)
        del filesystem_data["signature"]
        assert client.json_data == filesystem_data

    def test_url_str_attr(self):
        t_config = TConfig()
        t_config.DATA_DIR = os.getcwd()
        t_config.UPDATE_URLS = "http://acme.com/update"
        client = Client(t_config, test=True)
        assert isinstance(client.update_urls, list)

    def test_url_list_attr(self):
        t_config = TConfig()
        t_config.DATA_DIR = os.getcwd()
        t_config.UPDATE_URLS = ["http://acme.com/update"]
        client = Client(t_config, test=True)
        assert isinstance(client.update_urls, list)

    def test_url_tuple_attr(self):
        t_config = TConfig()
        t_config.DATA_DIR = os.getcwd()
        t_config.UPDATE_URLS = ("http://acme.com/update",)
        client = Client(t_config, test=True)
        assert isinstance(client.update_urls, list)

    def test_urls_str_attr(self):
        t_config = TConfig()
        t_config.DATA_DIR = os.getcwd()
        t_config.UPDATE_URLS = "http://acme.com/update"
        client = Client(t_config, test=True)
        assert isinstance(client.update_urls, list)

    def test_urls_list_attr(self):
        t_config = TConfig()
        t_config.DATA_DIR = os.getcwd()
        t_config.UPDATE_URLS = ["http://acme.com/update"]
        client = Client(t_config, test=True)
        assert isinstance(client.update_urls, list)

    def test_urls_tuple_attr(self):
        t_config = TConfig()
        t_config.DATA_DIR = os.getcwd()
        t_config.UPDATE_URLS = ("http://acme.com/update",)
        client = Client(t_config, test=True)
        assert isinstance(client.update_urls, list)


@pytest.mark.usefixtures("cleandir", "client")
class TestDownload(object):
    def test_failed_refresh(self, client):
        client = Client(None, refresh=True, test=True)
        client.data_dir = os.getcwd()
        assert client.ready is False

    def test_http(self):
        t_config = TConfig()
        t_config.DATA_DIR = os.getcwd()
        client = Client(t_config, refresh=True, test=True)
        update = client.update_check(client.app_name, "0.0.1")
        assert update is not None
        assert update.app_name == "Acme"
        assert update.download() is True
        assert update.is_downloaded() is True

    @pytest.mark.run(order=5)
    def test_background_http(self):
        t_config = TConfig()
        t_config.DATA_DIR = os.getcwd()
        client = Client(t_config, refresh=True, test=True)
        update = client.update_check(client.app_name, "0.0.1")
        assert update is not None
        assert update.app_name == "Acme"
        update.download(background=True)
        count = 0
        while count < 61:
            if update.is_downloaded() is True:
                break
            time.sleep(1)
            count += 1
        assert update.is_downloaded() is True

    @pytest.mark.run(order=6)
    def test_multiple_background_calls(self, client):
        t_config = TConfig()
        t_config.DATA_DIR = os.getcwd()
        t_config.VERIFY_SERVER_CERT = False
        client = Client(t_config, refresh=True, test=True)
        update = client.update_check(client.app_name, "0.0.1")
        assert update is not None
        assert update.app_name == "Acme"
        update.download(background=True)
        count = 0
        assert update.download(background=True) is None
        assert update.download() is None
        while count < 61:
            if update.is_downloaded() is True:
                break
            time.sleep(1)
            count += 1
        assert update.is_downloaded() is True


@pytest.mark.usefixtures("cleandir", "client")
class TestExtract(object):
    def test_extract(self, client):
        update = client.update_check(client.app_name, "0.0.1")
        assert update is not None
        assert update.download() is True
        if get_system() != "win":
            assert update.extract() is True

    def test_extract_no_file(self, client):
        update = client.update_check(client.app_name, "0.0.1")
        assert update is not None
        assert update.download() is True
        with ChDir(update.update_folder):
            files = os.listdir(os.getcwd())
            for f in files:
                remove_any(f)
        if get_system() != "win":
            assert update.extract() is False


class TestGenVersion(object):
    def test1(self):
        assert gen_user_friendly_version("1.0.0.2.0") == "1.0"
        assert gen_user_friendly_version("1.2.2.2.0") == "1.2.2"
        assert gen_user_friendly_version("2.0.5.0.3") == "2.0.5 Alpha 3"
        assert gen_user_friendly_version("2.2.1.1.0") == "2.2.1 Beta"


class TestChannelStrict(object):

    version_data = {
        "latest": {
            "Acme": {
                "stable": {"mac": "4.4.3.2.0"},
                "beta": {"mac": "4.4.1.1.0"},
                "alpha": {"mac": "4.4.2.0.5"},
            }
        }
    }

    def test1(self):
        data = EasyAccessDict(self.version_data)
        assert (
            get_highest_version("Acme", "mac", "alpha", data, strict=True)
            == "4.4.2.0.5"
        )
        assert (
            get_highest_version("Acme", "mac", "beta", data, strict=True) == "4.4.1.1.0"
        )
        assert (
            get_highest_version("Acme", "mac", "stable", data, strict=True)
            == "4.4.3.2.0"
        )


class TestChannelLessStrict(object):

    version_data = {
        "latest": {
            "Acme": {
                "stable": {"mac": "4.4.3.2.0"},
                "beta": {"mac": "4.4.1.1.0"},
                "alpha": {"mac": "4.4.2.0.5"},
            }
        }
    }

    def test1(self):
        data = EasyAccessDict(self.version_data)
        assert (
            get_highest_version("Acme", "mac", "alpha", data, strict=False)
            == "4.4.3.2.0"
        )


class TestMissingStable(object):

    version_data = {
        "latest": {
            "Acme": {"beta": {"mac": "4.4.1.1.0"}, "alpha": {"mac": "4.4.2.0.5"}}
        }
    }

    def test1(self):
        data = EasyAccessDict(self.version_data)
        assert get_highest_version("Acme", "mac", "stable", data, strict=True) is None
