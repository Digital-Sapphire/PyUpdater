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
import sys

from dsdev_utils.system import get_system
import pytest

from pyupdater.utils.builder import ExternalLib
from pyupdater.utils.config import ConfigManager


CONFIG = {"APP_NAME": "PyUpdater Test", "COMPANY_NAME": "ACME", "UPDATE_PATCHES": True}

if sys.platform == "win32":
    EXT = ".zip"
else:
    EXT = ".tar.gz"


@pytest.mark.usefixtures("cleandir")
class TestBuilder(object):
    def test_build(self):
        cm = ConfigManager()
        config = cm.load_config()
        config.update(CONFIG)
        cm.save_config(config)


@pytest.mark.usefixtures("cleandir")
class TestExternalLib(object):
    def test_archive(self):
        with io.open("test", "w", encoding="utf-8") as f:
            f.write("this is a test")
        ex = ExternalLib("test", "0.1")
        ex.archive()
        assert os.path.exists("test-{}-0.1{}".format(get_system(), EXT))
