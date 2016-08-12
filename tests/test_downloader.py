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
from __future__ import unicode_literals

import pytest

from pyupdater.client.downloader import FileDownloader
from pyupdater.utils.exceptions import FileDownloaderError


FILENAME = 'dont delete pyu test.txt'
FILE_HASH = '82719546b992ef81f4544fb2690c6a05b300a0216eeaa8f3616b3b107a311629'
URLS = ['https://pyu-tester.s3.amazonaws.com/']


@pytest.mark.usefixtue("cleandir")
class TestData(object):

    def test_return(self):
        fd = FileDownloader(FILENAME, URLS, FILE_HASH, verify=True)
        binary_data = fd.download_verify_return()
        assert binary_data is not None

    def test_cb(self):
        def cb(status):
            pass
        fd = FileDownloader(FILENAME, URLS, hexdigest=FILE_HASH,
                            progress_hooks=[cb], verify=True)
        binary_data = fd.download_verify_return()
        assert binary_data is not None

    def test_return_fail(self):
        fd = FileDownloader(FILENAME, URLS,
                            'JKFEIFJILEFJ983NKFNKL', verify=True)
        binary_data = fd.download_verify_return()
        assert binary_data is None


@pytest.mark.usefixtue("cleandir")
class TestUrl(object):

    def test_bad_url(self):
        fd = FileDownloader(FILENAME, ['bad url'], hexdigest='bad hash',
                            verify=True)
        binary_data = fd.download_verify_return()
        assert binary_data is None

    def test_url_as_string(self):
        with pytest.raises(FileDownloaderError):
            FileDownloader(FILENAME, URLS[0])


@pytest.mark.usefixtue("cleandir")
class TestContentLength(object):

    def test_bad_content_length(self):
        class FakeHeaders(object):
            headers = {}

        fd = FileDownloader(FILENAME, URLS, hexdigest=FILE_HASH, verify=True)
        data = FakeHeaders()
        assert fd._get_content_length(data) is None

    def test_good_conent_length(self):
        fd = FileDownloader(FILENAME, URLS, hexdigest=FILE_HASH, verify=True)
        fd.download_verify_return()
        assert fd.content_length == 2387
