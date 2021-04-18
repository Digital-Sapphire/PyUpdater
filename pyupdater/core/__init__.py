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
import os

from .key_handler import KeyHandler
from .key_handler.keys import KeyImporter
from .package_handler import PackageHandler
from .uploader import Uploader
from pyupdater.utils.config import Config


class PyUpdater(object):
    """Processes, signs & uploads updates

    Kwargs:

        config (obj): config object
    """

    def __init__(self, config=None):
        self.config = Config()
        # Important to keep this before updating config
        if config is not None:
            self.update_config(config)

    def update_config(self, config):
        """Updates internal config

        Args:

            config (obj): config object
        """
        if not hasattr(config, "DATA_DIR"):
            config.DATA_DIR = None
        if config.DATA_DIR is None:
            config.DATA_DIR = os.getcwd()
        self.config.from_object(config)
        self._update(self.config)

    def _update(self, config):
        self.kh = KeyHandler()
        self.key_importer = KeyImporter()
        self.ph = PackageHandler(config)
        self.up = Uploader(config)

    def setup(self):
        """Sets up root dir with required PyUpdater folders"""
        self.ph.setup()

    def process_packages(self, report_errors=False):
        """Creates hash for updates & adds information about update to
        version file
        """
        self.ph.process_packages(report_errors)

    def set_uploader(self, requested_uploader, keep=False):
        """Sets upload destination

        Args:

            requested_uploader (str): upload service. i.e. s3, scp

            keep (bool): False to delete files after upload.
                         True to keep files. Default False.

        """
        self.up.set_uploader(requested_uploader, keep)

    def upload(self):
        """Uploads files in deploy folder"""
        return self.up.upload()

    def get_plugin_names(self):
        return self.up.get_plugin_names()

    def import_keypack(self):
        """Creates signing keys"""
        return self.key_importer.start()

    def sign_update(self, split_version):
        """Signs version file with signing key"""
        self.kh.sign_update(split_version)
