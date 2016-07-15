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

import sys
import traceback


class STDError(Exception):
    """Extends exceptions to show added message if error isn't expected.

    Args:

        msg (str): error message

    Kwargs:

        tb (obj): is the original traceback so that it can be printed.

        expected (bool):

            Meaning:

                True - Report issue msg not shown

                False - Report issue msg shown
    """
    def __init__(self, msg, tb=None, expected=False):
        if expected is False:
            msg = msg + ('; please report this issue on https://github.com'
                         '/JMSwag/PyUpdater/issues')
        super(STDError, self).__init__(msg)

        self.traceback = tb
        self.exc_info = sys.exc_info()  # preserve original exception

    def format_traceback(self):
        if self.traceback is None:
            return None
        return ''.join(traceback.format_tb(self.traceback))


class ClientError(STDError):
    """Raised for Client exceptions"""
    def __init__(self, *args, **kwargs):
        super(ClientError, self).__init__(*args, **kwargs)


class FileDownloaderError(STDError):
    def __init__(self, *args, **kwargs):
        super(FileDownloaderError, self).__init__(*args, **kwargs)


class PackageHandlerError(STDError):
    """Raised for PackageHandler exceptions"""
    def __init__(self, *args, **kwargs):
        super(PackageHandlerError, self).__init__(*args, **kwargs)


class PatcherError(STDError):
    """Raised for Patcher exceptions"""
    def __init__(self, *args, **kwargs):
        super(PatcherError, self).__init__(*args, **kwargs)


class UploaderError(STDError):
    """Raised for Uploader exceptions"""
    def __init__(self, *args, **kwargs):
        super(UploaderError, self).__init__(*args, **kwargs)


class UploaderPluginError(STDError):
    """Raised for Uploader exceptions"""
    def __init__(self, *args, **kwargs):
        super(UploaderPluginError, self).__init__(*args, **kwargs)


class UtilsError(STDError):
    """Raised for Utils exceptions"""
    def __init__(self, *args, **kwargs):
        super(UtilsError, self).__init__(*args, **kwargs)
