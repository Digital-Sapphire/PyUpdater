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
from pyupdater.utils import lazy_import

__all__ = ['PyUpdater']


@lazy_import
def pyupdater():
    import pyupdater.core
    import pyupdater.settings
    return pyupdater


@lazy_import
def logging():
    import logging
    import logging.handlers
    return logging


@lazy_import
def os():
    import os
    return os


@lazy_import
def sys():
    import sys
    return sys


@lazy_import
def appdirs():
    import appdirs
    return appdirs


@lazy_import
def jms_utils():
    import jms_utils
    import jms_utils.logger
    return jms_utils


PyUpdater = pyupdater.core.PyUpdater


log = logging.getLogger()
log.setLevel(logging.DEBUG)
nh = logging.NullHandler()
nh.setLevel(logging.DEBUG)
log.addHandler(nh)
LOG_DIR = appdirs.user_log_dir(pyupdater.settings.APP_NAME,
                               pyupdater.settings.APP_AUTHOR)
if not os.path.exists(LOG_DIR):  # pragma: no cover
    os.makedirs(LOG_DIR)
LOG_FILENAME_DEBUG = os.path.join(LOG_DIR,
                                  pyupdater.settings.LOG_FILENAME_DEBUG)
rh = logging.handlers.RotatingFileHandler(LOG_FILENAME_DEBUG, backupCount=1,
                                          maxBytes=10293049)
rh.setLevel(logging.DEBUG)
rh.setFormatter(jms_utils.logger.logging_formatter)
log.addHandler(rh)

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
log.debug('Version - %s', __version__)
