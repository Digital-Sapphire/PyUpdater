# --------------------------------------------------------------------------
# Copyright 2014-2016 Digital Sapphire Development Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# --------------------------------------------------------------------------
from __future__ import unicode_literals

import os

from pyupdater.key_handler import KeyHandler
from pyupdater.key_handler.keys import KeyImporter
from pyupdater.package_handler import PackageHandler
from pyupdater.uploader import Uploader
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
        if not hasattr(config, 'DATA_DIR'):
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
        "Sets up root dir with required PyUpdater folders"
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
        """
        self.up.set_uploader(requested_uploader, keep)

    def upload(self):
        "Uploads files in deploy folder"
        self.up.upload()

    def get_plugin_names(self):
        return self.up.get_plugin_names()

    def import_keypack(self):
        "Creates signing keys"
        self.key_importer.start()

    def sign_update(self):
        "Signs version file with signing key"
        self.kh.sign_update()
