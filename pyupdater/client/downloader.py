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
import hashlib
import inspect
import logging
import os
import time
from urllib.parse import quote as url_quote

import certifi
import urllib3
from pyupdater.utils.exceptions import FileDownloaderError

log = logging.getLogger(__name__)


def get_hash(data):
    """Get hash of object

    Args:

        data (object): Object you want hash of.

    Returns:

        (str): sha256 hash
    """
    if not isinstance(data, bytes):
        data = bytes(data, "utf-8")
    hash_ = hashlib.sha256(data).hexdigest()
    log.debug("Hash for binary data: %s", hash_)
    return hash_


class FileDownloader(object):
    """The FileDownloader object downloads files to memory and
    verifies their hash.  If hash is verified data is either
    written to disk to returned to calling object

    ######Args:

    filename (str): The name of file to download

    urls (list): List of urls to use for file download

    hexdigest (str): The hash of the file to download

    ######Kwargs:

    headers (str):

    hexdigest (str): The hash of the file to download

    verify (bool):

        True: Verify https connection

        False: Do not verify https connection

    """

    def __init__(self, *args, **kwargs):
        # We'll append the filename to one of the provided urls
        # to create the download link
        try:
            self.filename = args[0]
        except IndexError:
            raise FileDownloaderError("No filename provided", expected=True)

        try:
            self.urls = args[1]
        except IndexError:
            raise FileDownloaderError("No urls provided", expected=True)
        # User may have accidentally passed a
        # string to the urls parameter
        if isinstance(self.urls, list) is False:
            raise FileDownloaderError("Must pass list of urls", expected=True)

        try:
            self.hexdigest = args[2]
        except IndexError:
            self.hexdigest = kwargs.get("hexdigest")

        # Specify if we want to verify TLS connections
        self.verify = kwargs.get("verify", True)

        # Max attempts to download resource
        self.max_download_retries = kwargs.get("max_download_retries")

        # Progress hooks to be called
        self.progress_hooks = kwargs.get("progress_hooks", [])

        # Initial block size for each read
        self.block_size = 4096 * 4

        # Storage type, 'memory' or 'file'
        self.file_binary_type = "memory"
        # Max size of download to memory, larger file will be stored to file
        self.download_max_size = 16 * 1024 * 1024
        # Hold all binary data once file has been downloaded
        self.file_binary_data = []
        # Temporary file to hold large download data
        self.file_binary_path = self.filename + ".part"

        # Total length of data to download.
        self.content_length = None

        # Extra headers
        self.headers = kwargs.get("headers")

        self.http_timeout = kwargs.get("http_timeout")

        if self.verify is True:
            self.http_pool = self._get_http_pool()
        else:
            self.http_pool = self._get_http_pool(secure=False)

    def _get_http_pool(self, secure=True):
        if secure:
            _http = urllib3.PoolManager(
                cert_reqs=str("CERT_REQUIRED"),
                ca_certs=certifi.where(),
                timeout=self.http_timeout,
            )
        else:
            _http = urllib3.PoolManager(timeout=self.http_timeout)

        if self.headers:
            urllib_keys = inspect.getfullargspec(urllib3.util.make_headers).args
            urllib_headers = {
                header: value
                for header, value in self.headers.items()
                if header in urllib_keys
            }
            other_headers = {
                header: value
                for header, value in self.headers.items()
                if header not in urllib_keys
            }
            _headers = urllib3.util.make_headers(**urllib_headers)
            _headers.update(other_headers)
            _http.headers.update(_headers)
        log.debug("HTTP Timeout is " + str(self.http_timeout))
        return _http

    def download_verify_write(self):
        """
        Downloads file then verifies against provided hash
        If hash verfies then writes data to disk

        Returns:

             (bool):

                 True - Hashes match or no hash was given during initialization.

                 False - Hashes don't match
        """

        # Downloading data internally
        check = self._download_to_storage(check_hash=True)
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

            (data):

                Binary data - If hashes match or no hash was given during
                initialization.

                None - If any verification didn't pass
        """
        check = self._download_to_storage(check_hash=True)
        if check is True or check is None:
            if self.file_binary_type == "memory":
                if self.file_binary_data:
                    return b"".join(self.file_binary_data)
                else:
                    return None
            else:
                log.warning(
                    "Downloaded file is very large, reading it"
                    " in to memory may crash the app"
                )
                return open(self.file_binary_path, "rb").read()
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

    def _download_to_storage(self, check_hash=True):
        data = self._create_response()

        if data is None:
            return None
        hash_ = hashlib.sha256()

        # Getting length of file to show progress
        self.content_length = FileDownloader._get_content_length(data)
        if self.content_length is None:
            log.debug("Content-Length not in headers")
            log.debug("Callbacks will not show time left " "or percent downloaded.")
        if self.content_length is None or self.content_length > self.download_max_size:
            log.debug("Using file as storage since the file is too large")
            self.file_binary_type = "file"
        else:
            self.file_binary_type = "memory"

        # Setting start point to show progress
        received_data = 0

        start_download = time.time()
        block = data.read(1)
        received_data += len(block)
        if self.file_binary_type == "memory":
            self.file_binary_data = [block]
        else:
            binary_file = open(self.file_binary_path, "wb")
            binary_file.write(block)
        hash_.update(block)
        while 1:
            # Grabbing start time for use with best block size
            start_block = time.time()

            # Get data from connection
            block = data.read(self.block_size)

            # Grabbing end time for use with best block size
            end_block = time.time()

            if len(block) == 0:
                # No more data, get out of this never ending loop!
                if self.file_binary_type == "file":
                    binary_file.close()
                break

            # Calculating the best block size for the
            # current connection speed
            self.block_size = self._best_block_size(end_block - start_block, len(block))
            log.debug("Block size: %s", self.block_size)
            if self.file_binary_type == "memory":
                self.file_binary_data.append(block)
            else:
                binary_file.write(block)
            hash_.update(block)

            # Total data we've received so far

            received_data += len(block)

            # If content length is None we will return a static percent
            # -.-%
            percent = FileDownloader._calc_progress_percent(
                received_data, self.content_length
            )

            # If content length is None we will return a static time remaining
            # --:--
            time_left = FileDownloader._calc_eta(
                start_download, time.time(), self.content_length, received_data
            )

            status = {
                "total": self.content_length,
                "downloaded": received_data,
                "status": "downloading",
                "percent_complete": percent,
                "time": time_left,
            }

            # Call all progress hooks with status data
            self._call_progress_hooks(status)

        status = {
            "total": self.content_length,
            "downloaded": received_data,
            "status": "finished",
            "percent_complete": percent,
            "time": "00:00",
        }
        self._call_progress_hooks(status)
        log.debug("Download Complete")

        if check_hash:
            # Checks hash of downloaded file
            if self.hexdigest is None:
                # No hash provided to check.
                # So just return any data received
                log.debug("No hash to verify")
                return None
            if self.file_binary_data is None:
                # Exit quickly if we got nothing to compare
                # Also I'm sure we'll get an exception trying to
                # pass None to get hash :)
                log.debug("Cannot verify file hash - No Data")
                return False
            log.debug("Checking file hash")
            log.debug("Update hash: %s", self.hexdigest)

            file_hash = hash_.hexdigest()
            if file_hash == self.hexdigest:
                log.debug("File hash verified")
                return True
            log.debug("Cannot verify file hash")
            return False

    # Calling all progress hooks
    def _call_progress_hooks(self, data):
        log.debug(data)
        for ph in self.progress_hooks:
            try:
                ph(data)
            except Exception as err:
                log.debug("Exception in callback: %s", ph.__name__)
                log.debug(err, exc_info=True)

    # Creating response object to start download
    # Attempting to do some error correction for aws s3 urls
    def _create_response(self):
        data = None
        max_download_retries = self.max_download_retries
        for url in self.urls:
            # Create url for resource
            file_url = url + url_quote(self.filename)
            log.debug("Url for request: %s", file_url)
            try:
                data = self.http_pool.urlopen(
                    "GET",
                    file_url,
                    preload_content=False,
                    retries=max_download_retries,
                    decode_content=False,
                )
            except urllib3.exceptions.SSLError:
                log.debug("SSL cert not verified")
                continue
            except urllib3.exceptions.MaxRetryError:
                log.debug("MaxRetryError")
                continue
            except Exception as e:
                # Catch whatever else comes up and log it
                # to help fix other http related issues
                log.debug(str(e), exc_info=True)
            else:
                if data.status != 200:
                    log.debug("Received a non-200 response %d", data.status)
                    data = None
                else:
                    break

        if data is not None:
            log.debug("Resource URL: %s", file_url)
        else:
            log.debug("Could not create resource URL.")
        return data

    def _write_to_file(self):
        # Writes download data to disk
        if self.file_binary_type == "memory":
            with open(self.filename, "wb") as f:
                for block in self.file_binary_data:
                    f.write(block)
        else:
            if os.path.exists(self.filename):
                os.unlink(self.filename)
            os.rename(self.file_binary_path, self.filename)

    @staticmethod
    def _get_content_length(data):
        content_length = data.headers.get("Content-Length")
        if content_length is not None:
            content_length = int(content_length)
        log.debug("Got content length of: %s", content_length)
        return content_length

    @staticmethod
    def _calc_eta(start, now, total, current):
        # Calculates remaining time of download
        if total is None:
            return "--:--"
        dif = now - start
        if current == 0 or dif < 0.001:  # One millisecond
            return "--:--"
        rate = float(current) / dif
        eta = int((float(total) - float(current)) / rate)
        (eta_mins, eta_secs) = divmod(eta, 60)
        if eta_mins > 99:
            return "--:--"
        return "%02d:%02d" % (eta_mins, eta_secs)

    @staticmethod
    def _calc_progress_percent(received, total):
        if total is None:
            return "-.-%"
        percent = float(received) / total * 100
        percent = "%.1f" % percent
        return percent
