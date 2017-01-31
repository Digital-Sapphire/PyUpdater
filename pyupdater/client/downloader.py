# --------------------------------------------------------------------------
# Copyright (c) 2015-2017 Digital Sapphire
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

import hashlib
import logging
import time

import certifi
import six
import urllib3

from pyupdater.compat import url_quote
from pyupdater.utils.exceptions import FileDownloaderError
log = logging.getLogger(__name__)


def get_hash(data):
    """Get hash of object

    Args:

        data (object): Object you want hash of.

    Returns:

        (str): sha256 hash
    """
    if six.PY3:
        if not isinstance(data, bytes):
            data = bytes(data, 'utf-8')
    hash_ = hashlib.sha256(data).hexdigest()
    log.debug('Hash for binary data: %s', hash_)
    return hash_


def get_http_pool(secure=True):
    if secure is True:
        return urllib3.PoolManager(cert_reqs=str('CERT_REQUIRED'),
                                   ca_certs=certifi.where())
    else:
        return urllib3.PoolManager()


# The FileDownloader object downloads files to memory and
# verifies their hash.  If hash is verified data is either
# written to disk to returned to calling object
#
# Args:
#
#     filename (str): The name of file to download
#
#     urls (list): List of urls to use for file download
#
# Kwargs:
#
#     hexdigest (str): The hash of the file to download
#
#     verify (bool) Meaning:
#
#         True: Verify https connection
#
#         False: Don't verify https connection
class FileDownloader(object):

    def __init__(self, *args, **kwargs):
        # We'll append the filename to one of the provided urls
        # to create the download link
        try:
            self.filename = args[0]
        except IndexError:
            raise FileDownloaderError('No filename provided', expected=True)

        try:
            self.urls = args[1]
        except IndexError:
            raise FileDownloaderError('No urls provided', expected=True)
        # User may have accidentally passed a
        # string to the urls parameter
        if isinstance(self.urls, list) is False:
            raise FileDownloaderError('Must pass list of urls', expected=True)

        try:
            self.hexdigest = args[2]
        except IndexError:
            self.hexdigest = kwargs.get('hexdigest')

        # Specify if we want to verify TLS connections
        self.verify = kwargs.get('verify', True)

        # Max attempts to download resource
        self.max_download_retries = kwargs.get('max_download_retries')

        # Progress hooks to be called
        self.progress_hooks = kwargs.get('progress_hooks', [])

        # Initial block size for each read
        self.block_size = 4096 * 4

        # Hold all binary data once file has been downloaded
        self.file_binary_data = None

        # Total length of data to download.
        self.content_length = None

        if self.verify is True:
            self.http_pool = get_http_pool()
        else:
            self.http_pool = get_http_pool(secure=False)

    # Downloads file then verifies against provided hash
    # If hash verfies then writes data to disk
    #
    # Returns:
    #
    #     (bool) Meanings:
    #
    #         True - Hashes match or no hash was given during initialization.
    #
    #         False - Hashes don't match
    def download_verify_write(self):
        # Downloading data internally
        self._download_to_memory()
        check = self._check_hash()
        # If no hash is passed just write the file
        if check is True or check is None:
            self._write_to_file()
            return True
        else:
            del self.file_binary_data
            return False

    def download_verify_return(self):
        """
        Downloads file to memory, checks against provided hash
        If matched returns binary data

        Returns:

            (data) Meanings:

                Binary data - If hashes match or no hash was given during
                initialization.

                None - If any verification didn't pass
        """
        self._download_to_memory()
        check = self._check_hash()
        if check is True or check is None:
            return self.file_binary_data
        else:
            return None

    @staticmethod
    def _best_block_size(elapsed_time, _bytes):
        # Returns best block size for current Internet connection speed
        new_min = max(_bytes / 2.0, 1.0)
        new_max = min(max(_bytes * 2.0, 1.0), 4194304)  # Do not surpass 4 MB
        if elapsed_time < 0.001:
            return int(new_max)
        rate = _bytes / elapsed_time
        if rate > new_max:
            return int(new_max)
        if rate < new_min:
            return int(new_min)
        return int(rate)

    def _download_to_memory(self):
        data = self._create_response()

        if data is None:
            return None

        # Getting length of file to show progress
        self.content_length = self._get_content_length(data)
        if self.content_length is None:
            log.debug('Content-Length not in headers')
            log.debug('Callbacks will not show time left '
                      'or percent downloaded.')
        # Setting start point to show progress
        recieved_data = 0

        start_download = time.time()
        block = data.read(1)
        recieved_data += len(block)
        self.file_binary_data = block
        while 1:
            # Grabbing start time for use with best block size
            start_block = time.time()

            # Get data from connection
            block = data.read(self.block_size)

            # Grabbing end time for use with best block size
            end_block = time.time()

            if len(block) == 0:
                # No more data, get out of this never ending loop!
                break

            # Calculating the best block size for the
            # current connection speed
            self.block_size = self._best_block_size(end_block - start_block,
                                                    len(block))
            log.debug('Block size: %s', self.block_size)
            self.file_binary_data += block

            # Total data we've received so far
            recieved_data += len(block)

            # If content length is None we will return a static percent
            # -.-%
            percent = self._calc_progress_percent(recieved_data,
                                                  self.content_length)

            # If content length is None we will return a static time remaining
            # --:--
            time_left = FileDownloader._calc_eta(start_download, time.time(),
                                                 self.content_length,
                                                 recieved_data)

            status = {'total': self.content_length,
                      'downloaded': recieved_data,
                      'status': 'downloading',
                      'percent_complete': percent,
                      'time': time_left}

            # Call all progress hooks with status data
            self._call_progress_hooks(status)

        status = {'total': self.content_length,
                  'downloaded': recieved_data,
                  'status': 'finished',
                  'percent_complete': percent,
                  'time': '00:00'}
        self._call_progress_hooks(status)
        log.debug('Download Complete')

    # Calling all progress hooks
    def _call_progress_hooks(self, data):
        log.debug(data)
        for ph in self.progress_hooks:
            try:
                ph(data)
            except Exception as err:
                log.debug('Exception in callback: %s', ph.__name__)
                log.debug(err, exc_info=True)

    # Creating response object to start download
    # Attempting to do some error correction for aws s3 urls
    def _create_response(self):
        data = None
        max_download_retries = self.max_download_retries
        for url in self.urls:

            # Create url for resource
            file_url = url + url_quote(self.filename)
            log.debug('Url for request: %s', file_url)
            try:
                data = self.http_pool.urlopen('GET', file_url,
                                              preload_content=False,
                                              retries=max_download_retries)
            except urllib3.exceptions.SSLError:
                log.debug('SSL cert not verified')
                continue
            except urllib3.exceptions.MaxRetryError:
                log.debug('MaxRetryError')
                continue
            except Exception as e:
                # Catch whatever else comes up and log it
                # to help fix other http related issues
                log.debug(str(e), exc_info=True)
            else:
                break

        if data is not None:
            log.debug('Resource URL: %s', file_url)
        else:
            log.debug('Could not create resource URL.')
        return data

    def _write_to_file(self):
        # Writes download data in memory to disk
        with open(self.filename, 'wb') as f:
            f.write(self.file_binary_data)

    def _check_hash(self):
        # Checks hash of downloaded file
        if self.hexdigest is None:
            # No hash provided to check.
            # So just return any data recieved
            log.debug('No hash to verify')
            return None
        if self.file_binary_data is None:
            # Exit quickly if we got nohting to compare
            # Also I'm sure we'll get an exception trying to
            # pass None to get hash :)
            log.debug('Cannot verify file hash - No Data')
            return False
        log.debug('Checking file hash')
        log.debug('Update hash: %s', self.hexdigest)

        file_hash = get_hash(self.file_binary_data)
        if file_hash == self.hexdigest:
            log.debug('File hash verified')
            return True
        log.debug('Cannot verify file hash')
        return False

    def _get_content_length(self, data):
        content_length = data.headers.get("Content-Length")
        if content_length is not None:
            content_length = int(content_length)
        log.debug('Got content length of: %s', content_length)
        return content_length

    @staticmethod
    def _calc_eta(start, now, total, current):
        # Calculates remaining time of download
        if total is None:
            return '--:--'
        dif = now - start
        if current == 0 or dif < 0.001:  # One millisecond
            return '--:--'
        rate = float(current) / dif
        eta = int((float(total) - float(current)) / rate)
        (eta_mins, eta_secs) = divmod(eta, 60)
        if eta_mins > 99:
            return '--:--'
        return '%02d:%02d' % (eta_mins, eta_secs)

    def _calc_progress_percent(self, recieved, total):
        if total is None:
            return '-.-%'
        percent = float(recieved) / total * 100
        percent = '%.1f' % percent
        return percent
