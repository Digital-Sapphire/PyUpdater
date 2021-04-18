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
            msg = msg + (
                "; please report this issue on https://github.com"
                "/Digital-Sapphire/PyUpdater/issues"
            )
        super(STDError, self).__init__(msg)

        self.traceback = tb
        self.exc_info = sys.exc_info()  # preserve original exception

    def format_traceback(self):  # pragma: no cover
        if self.traceback is None:
            return None
        return "".join(traceback.format_tb(self.traceback))


class ClientError(STDError):
    """Raised for Client exceptions"""

    def __init__(self, *args, **kwargs):
        super(ClientError, self).__init__(*args, **kwargs)


class FileDownloaderError(STDError):
    def __init__(self, *args, **kwargs):
        super(FileDownloaderError, self).__init__(*args, **kwargs)


class KeyHandlerError(STDError):
    def __init__(self, *args, **kwargs):
        super(KeyHandlerError, self).__init__(*args, **kwargs)


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
