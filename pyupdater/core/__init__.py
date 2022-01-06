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
from typing import Optional

from .key_handler import KeyHandler
from .key_handler.keys import KeyImporter
from .package_handler import PackageHandler
from .uploader import Uploader


class PyUpdater(object):
    """Processes, signs & uploads updates

    Kwargs:

        patch_support (bool): whether or not to support patch updates
        plugin_configs (dict): plugin configuration
    """

    def __init__(self, patch_support: Optional[bool] = None, plugin_configs: Optional[dict] = None):
        if patch_support is None:
            patch_support = True
        if plugin_configs is None:
            plugin_configs = {}
        self.kh = KeyHandler()
        self.key_importer = KeyImporter()
        self.ph = PackageHandler(patch_support=patch_support)
        self.up = Uploader(plugin_configs=plugin_configs)

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
