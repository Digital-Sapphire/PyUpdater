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
import os
import sys

from dsdev_utils.paths import ChDir
import pytest
import six

from pyupdater.core.uploader import BaseUploader, Uploader
from pyupdater.utils.config import Config


class BaseTestUploader(BaseUploader):
    def init_config(self, config):
        pass

    def set_config(self, config):
        pass


class TestUploaderPass(BaseTestUploader):

    name = "success"
    author = "Digital Sapphire"

    def upload_file(self, filename):
        print(filename)
        return True


class TestUploaderFail(BaseTestUploader):

    name = "fail"
    author = "Digital Sapphire"

    def upload_file(self, filename):
        print(filename)
        return False


class TestUploaderRetryPass(BaseTestUploader):

    name = "retry-success"
    author = "Digital Sapphire"
    first_pass = False

    def upload_file(self, filename):
        print(filename)
        out = self.first_pass
        self.first_pass = True
        return out


class TestUploaderRetryFail(BaseTestUploader):

    name = "retry-fail"
    author = "Digital Sapphire"

    def upload_file(self, filename):
        print(filename)
        return False


class TestUploader(object):
    @pytest.mark.parametrize(
        "upload_plugin_type", ["success", "fail", "retry-success", "retry-fail"]
    )
    def test_uploader(self, cleandir, shared_datadir, upload_plugin_type):

        uploaders = [
            TestUploaderPass(),
            TestUploaderFail(),
            TestUploaderRetryPass(),
            TestUploaderRetryFail(),
        ]

        # Don't mind the name, should only contain 1 plugin
        upload_plugins = [u for u in uploaders if u.name == upload_plugin_type]

        if six.PY2 or sys.version_info[1] in [4, 5]:
            data_dir = str(shared_datadir)
        else:
            data_dir = shared_datadir

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        with ChDir(data_dir):
            uploader = Uploader(config=Config(), plugins=upload_plugins)

            upload_plugin = upload_plugins[0]

            uploader.set_uploader(upload_plugin_type)
            assert uploader.uploader.name == upload_plugin_type

            if "success" in upload_plugin.name:
                assert uploader.upload(["/file1"]) is True
            elif "fail" in upload_plugin.name:
                assert uploader.upload(["/file2"]) is False
