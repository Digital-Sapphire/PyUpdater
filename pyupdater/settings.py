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
import struct
import sys

from dsdev_utils import system


APP_NAME = "PyUpdater"
APP_AUTHOR = "Digital Sapphire"

# Used to hold PyUpdater config info for repo
CONFIG_DATA_FOLDER = ".pyupdater"

# User config file
CONFIG_FILE_USER = "config.pyu"

CONFIG_DB_KEY_APP_CONFIG = "app_config"
CONFIG_DB_KEY_KEYPACK = "keypack"
CONFIG_DB_KEY_VERSION_META = "version_meta"
CONFIG_DB_KEY_PY_REPO_CONFIG = "py_repo_config"

DEFAULT_CLIENT_CONFIG = ["client_config.py"]

GENERIC_APP_NAME = "PyUpdater App"
GENERIC_COMPANY_NAME = "PyUpdater"

# Log filename
LOG_FILENAME_DEBUG = "pyu-debug.log"

# KeyFile
KEYPACK_FILENAME = "keypack.pyu"

# Main user visible data folder
USER_DATA_FOLDER = "pyu-data"

# Key in version file where value are update meta data
UPDATES_KEY = "updates"

# Folder on client system where updates are stored
UPDATE_FOLDER = "update"

# Name of version file in online repo
VERSION_FILE_FILENAME = "versions-{}.gz".format(system.get_system())
VERSION_FILE_FILENAME_COMPAT = "versions.gz"
KEY_FILE_FILENAME = "keys.gz"
