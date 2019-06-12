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
import logging
from logging.handlers import RotatingFileHandler
import os

from appdirs import user_log_dir
from dsdev_utils.logger import logging_formatter

from pyupdater import settings
from pyupdater.core import PyUpdater

__all__ = ["PyUpdater"]


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Console logger
fmt = logging.Formatter("[%(levelname)s] %(message)s")
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
sh.setFormatter(fmt)
log.addHandler(sh)

# Log to pyu.log if available
local_debug_file_path = os.path.join(os.getcwd(), "pyu.log")
if os.path.exists(local_debug_file_path):  # pragma: no cover
    fh = logging.FileHandler(local_debug_file_path)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging_formatter)
    log.addHandler(fh)

# Default log directory
LOG_DIR = user_log_dir(settings.APP_NAME, settings.APP_AUTHOR)
if not os.path.exists(LOG_DIR):  # pragma: no cover
    os.makedirs(LOG_DIR)

log_file = os.path.join(LOG_DIR, settings.LOG_FILENAME_DEBUG)
rfh = RotatingFileHandler(log_file, maxBytes=1048576, backupCount=2)
rfh.setLevel(logging.DEBUG)
rfh.setFormatter(logging_formatter)
log.addHandler(rfh)

# noinspection PyPep8
from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions
log.debug("Version - %s", __version__)
