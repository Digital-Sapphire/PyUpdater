# --------------------------------------------------------------------------
# Copyright (c) 2016 Digital Sapphire
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
def dsdev_utils():
    import dsdev_utils
    import dsdev_utils.logger
    return dsdev_utils


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
rh.setFormatter(dsdev_utils.logger.logging_formatter)
log.addHandler(rh)

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
log.debug('Version - %s', __version__)
