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

import pytest
import six

from pyupdater.utils.config import Config
from pyupdater.utils import (
    check_repo,
    create_asset_archive,
    make_archive,
    PluginManager,
    remove_dot_files,
    run,
)


@pytest.mark.usefixtures("cleandir")
class TestUtils(object):
    def test_make_archive(self):
        with io.open("hash-test1.txt", "w", encoding="utf-8") as f:
            f.write("I should find some lorem text" * 11)

        with io.open("hash-test2.txt", "w", encoding="utf-8") as f:
            f.write("I should find some lorem text" * 5)

        filename1 = make_archive("hash", "hash-test1.txt", "0.2", "default")
        filename2 = make_archive("hash", "hash-test2.txt", "0.3", "default")

        assert os.path.exists(filename1)
        assert os.path.exists(filename2)

    def test_create_asset_archive(self):
        with io.open("hash-test1.dll", "w", encoding="utf-8") as f:
            f.write("I should find some lorem text" * 20)

        with io.open("hash-test2.so", "w", encoding="utf-8") as f:
            f.write("I should find some lorem text" * 11)

        with io.open("binary", "w", encoding="utf-8") as f:
            f.write("I should find some lorem text" * 5)

        filename = create_asset_archive("hash-test1.dll", "0.1")
        filename1 = create_asset_archive("hash-test2.so", "0.2")
        filename2 = create_asset_archive("binary", "0.3")

        assert os.path.exists(filename)
        assert os.path.exists(filename1)
        assert os.path.exists(filename2)

    def test_check_repo_fail(self):
        assert check_repo() is False

    def test_remove_dot_files(self):
        bad_list = [".DS_Store", "test", "stuff", ".trash"]
        good_list = ["test", "stuff"]
        for n in remove_dot_files(bad_list):
            assert n in good_list

    def test_run(self):
        assert run('echo "hello world!"') == 0

    @pytest.mark.parametrize(
        "n, a",
        [("test", None), (None, "test"), (1, "test"), ("test", 1), ("test", "test")],
    )
    def test_plugin_manager_load(self, n, a):
        class Plugin(object):
            name = n
            author = a

        pm = PluginManager(Config(), plugins=[Plugin()])

        if isinstance(n, six.string_types) and isinstance(a, six.string_types):
            assert len(pm.plugins) == 1
        else:
            assert len(pm.plugins) == 0

    def test_default_plugin_detection_s3(self):
        pm = PluginManager(Config())

        plugin_names = [n["name"] for n in pm.plugins]
        assert "s3" in plugin_names

    def test_default_plugin_detection_scp(self):
        pm = PluginManager(Config())

        plugin_names = [n["name"] for n in pm.plugins]
        assert "scp" in plugin_names

    def test_plugin_unique_names(self):
        class Plugin1(object):
            name = "test"
            author = "test1"

        class Plugin2(object):
            name = "test"
            author = "test2"

        pm = PluginManager(Config(), plugins=[Plugin1(), Plugin2()])

        plugin_names = [n["name"] for n in pm.plugins]

        assert "test" in plugin_names
        assert "test2" in plugin_names

    def test_plugin_config(self):
        class TPlugin(object):
            name = "test"
            author = "test1"
            bucket = ""

            def init_config(self, config):
                self.bucket = config.get("bucket", "bad")

        master_config = Config()

        master_config["PLUGIN_CONFIGS"] = {"test-test1": {"bucket": "test_bucket"}}

        pm = PluginManager(master_config, plugins=[TPlugin()])

        p = pm.get_plugin("test", False)
        assert p.bucket == ""

        p = pm.get_plugin("test", True)
        assert p.bucket == "test_bucket"
