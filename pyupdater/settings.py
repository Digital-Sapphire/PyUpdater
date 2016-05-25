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

APP_NAME = 'PyUpdater'
APP_AUTHOR = 'Digital Sapphire'

# Used to hold PyUpdater config info for repo
CONFIG_DATA_FOLDER = '.pyupdater'

# User config file
CONFIG_FILE_USER = 'config.pyu'

CONFIG_DB_KEY_APP_CONFIG = 'app_config'
CONFIG_DB_KEY_KEYPACK = 'keypack'
CONFIG_DB_KEY_VERSION_META = 'version_meta'
CONFIG_DB_KEY_PY_REPO_CONFIG = 'py_repo_config'

DEFAULT_CLIENT_CONFIG = ['client_config.py']

GENERIC_APP_NAME = 'PyUpdater App'
GENERIC_COMPANY_NAME = 'PyUpdater'

# Log filename
LOG_FILENAME = 'pyu.log'
LOG_FILENAME_DEBUG = 'pyu-debug.log'

# KeyFile
KEYPACK_FILENAME = 'keypack.pyu'

# Main user visible data folder
USER_DATA_FOLDER = 'pyu-data'

# Name of env var to get users passwrod from
USER_PASS_ENV = 'PYUPDATER_PASS'

# Key in version file where value are update meta data
UPDATES_KEY = 'updates'

# Folder on client system where updates are stored
UPDATE_FOLDER = 'update'

# Name of version file place in online repo
VERSION_FILE = 'versions.gz'
KEY_FILE = 'keys.gz'
