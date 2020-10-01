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
import gzip
import json
import logging
import os
import tempfile
import warnings

import appdirs
from dsdev_utils.app import app_cwd, FROZEN
from dsdev_utils.helpers import (
    EasyAccessDict as _EAD,
    gzip_decompress as _gzip_decompress,
    Version as _Version,
)
from dsdev_utils.logger import logging_formatter
from dsdev_utils.paths import ChDir as _ChDir
from dsdev_utils.system import get_system as _get_system
from nacl.signing import VerifyKey

from pyupdater import settings, __version__
from pyupdater.client.downloader import FileDownloader
from pyupdater.client.updates import (
    AppUpdate,
    get_highest_version,
    LibUpdate,
    UpdateStrategy,
)
from pyupdater.utils.config import Config as _Config
from pyupdater.utils.encoding import UnpaddedBase64Encoder
from pyupdater.utils.exceptions import ClientError


warnings.simplefilter("always", DeprecationWarning)


log = logging.getLogger(__name__)
log_path = os.path.join(app_cwd, "pyu.log")
if os.path.exists(log_path):  # pragma: no cover
    ch = logging.FileHandler(os.path.join(app_cwd, "pyu.log"))
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(logging_formatter)
    log.addHandler(ch)
log.debug("PyUpdater Version %s", __version__)


# Mostly used for testing purposes
class DefaultClientConfig(object):
    DATA_DIR = tempfile.gettempdir()


class Client(object):
    """Used to check for updates & returns an updateobject if there
    is an update.

    ######Args:

    obj (instance): config object

    ######Kwargs:

    refresh (bool): True - Refresh update manifest on init
                    False - Don't refresh update manifest on init

    progress_hooks (list): List of callbacks

    data_dir (str): Path to custom update folder

    headers (dict): A dictionary of generic and/or urllib3.utils.make_headers compatible headers

    strategy (str): The update strategy to use (default: overwrite).  See the UpdateStrategy enum for options.

    test (bool): Used to initialize a test client

    """

    def __init__(self, obj, **kwargs):
        if obj is None:
            obj = DefaultClientConfig()

        refresh = kwargs.get("refresh", False)
        progress_hooks = kwargs.get("progress_hooks")
        test = kwargs.get("test", False)
        data_dir = kwargs.get("data_dir")
        headers = kwargs.get("headers")

        # 3rd Party downloader
        self.downloader = kwargs.get("downloader")

        if headers is not None:
            if not isinstance(headers, dict):
                raise ClientError("headers argument must be a dict", expected=True)

        # String: Name of binary to update
        self.name = None

        # String: Version of the binary to update
        self.version = None

        # String: Update manifest as json string - set in _get_update_manifest
        self.json_data = None

        # Boolean: Version file verification
        self.verified = False

        # Boolean: Json being loaded to dict
        self.ready = False

        # LIst: Progress hooks to be called
        self.progress_hooks = []
        if progress_hooks is not None:
            if not isinstance(progress_hooks, list):
                raise SyntaxError("progress_hooks must be provided as a list.")
            self.progress_hooks += progress_hooks

        # A super dict used to save config info & be dot accessed
        config = _Config()
        config.from_object(obj)

        # Boolean: If executing frozen
        self.FROZEN = FROZEN

        # Grabbing config information
        update_urls = config.get("UPDATE_URLS", [])

        # List of URL to check for update data
        self.update_urls = Client._sanitize_update_url(update_urls)

        # Name of the running application
        self.app_name = config.get("APP_NAME", "PyUpdater")

        # Name of the app author
        self.company_name = config.get("COMPANY_NAME", "Digital Sapphire")

        # Used in testing to force use of the mac archive
        if test:
            # Making platform deterministic for tests.
            self.data_dir = obj.DATA_DIR
            self.platform = "mac"
        else:  # pragma: no cover
            if data_dir is None:
                # Getting platform specific user data directory
                self.data_dir = appdirs.user_data_dir(self.app_name, self.company_name)
            else:
                self.data_dir = data_dir

            # Used when parsing the update manifest
            self.platform = _get_system()

        # Folder to house update archives
        self.update_folder = os.path.join(self.data_dir, settings.UPDATE_FOLDER)

        # The root public key to verify the app signing private key
        self.root_key = config.get("PUBLIC_KEY", "")

        # We'll get the app_key later in _get_signing_key
        # That's if we verify the keys manifest
        self.app_key = None

        # Used to disable TLS cert verification
        self.verify = config.get("VERIFY_SERVER_CERT", True)

        # Max number of download retries
        self.max_download_retries = config.get("MAX_DOWNLOAD_RETRIES", 3)

        # HTTP Timeout
        self.http_timeout = config.get("HTTP_TIMEOUT", 30)

        # The name of the version file to download
        self.version_file = settings.VERSION_FILE_FILENAME

        # The name of the original version of the version file.
        # Basically the version.gz vs vesion-<platform>.gz
        self.version_file_compat = settings.VERSION_FILE_FILENAME_COMPAT

        # The name of the key file to download
        self.key_file = settings.KEY_FILE_FILENAME

        # headers
        self.headers = headers

        # Creating data & update directories
        self._setup()

        # The update strategy to use
        self.strategy = kwargs.get("strategy", UpdateStrategy.DEFAULT)

        if refresh is True:
            self.refresh()

    def refresh(self):
        """Will download and verify the version manifest."""
        self._get_signing_key()
        self._get_update_manifest()

    def update_check(self, name, version, channel="stable", strict=True):
        """Checks for available updates

        ######Args:

        name (str): Name of file to update

        version (str): Current version number of file to update

        channel (str): Release channel

        strict (bool):
            True - Only look for updates on specified channel.
            False - Look for updates on all channels

        ######Returns:

        (updateobject):

            AppUpdate - Used to update current binary

            LibUpdate - Used to update external assets

            None - No Updates available
        """
        return self._update_check(name, version, channel, strict)

    def _gen_file_downloader_options(self):
        return {
            "http_timeout": self.http_timeout,
            "max_download_retries": self.max_download_retries,
            "progress_hooks": self.progress_hooks,
            "headers": self.headers,
            "verify": self.verify,
        }

    def _update_check(self, name, version, channel, strict):
        valid_channels = ["alpha", "beta", "stable"]
        if channel not in valid_channels:
            log.debug("Invalid channel. May need to check spelling")
            channel = "stable"
        self.name = name

        # Version object used for comparison
        version = _Version(version)
        self.version = str(version)

        # Will be set to true if we are updating the currently
        # running app and not an app's asset
        app = False

        if self.ready is False:
            # No json data is loaded.
            # User may need to call refresh
            log.debug("No update manifest found")
            return None

        # Checking if version file is verified before
        # processing data contained in the version file.
        # This was done by self._get_update_manifest
        if self.verified is False:
            log.debug("Failed version file verification")
            return None

        # If we are an app we will need restart functionality, so we'll
        # user AppUpdate instead of LibUpdate
        if self.FROZEN is True and self.name == self.app_name:
            app = True

        log.debug("Checking for %s updates...", name)
        latest = get_highest_version(
            name, self.platform, channel, self.easy_data, strict
        )
        if latest is None:
            # If None is returned get_highest_version could
            # not find the supplied name in the version file
            log.debug("Could not find the latest version")
            return None

        # Change str to version object for easy comparison
        latest = _Version(latest)
        log.debug("Current version: %s", str(version))
        log.debug("Latest version: %s", str(latest))

        update_needed = latest > version
        log.debug("Update Needed: %s", update_needed)
        if latest <= version:
            log.debug("%s already updated to the latest version", name)
            return None

        # Config data to initialize update object
        data = {
            "strict": strict,
            "update_urls": self.update_urls,
            "name": self.name,
            "version": self.version,
            "easy_data": self.easy_data,
            "json_data": self.json_data,
            "data_dir": self.data_dir,
            "platform": self.platform,
            "channel": channel,
            "app_name": self.app_name,
            "verify": self.verify,
            "max_download_retries": self.max_download_retries,
            "progress_hooks": list(set(self.progress_hooks)),
            "headers": self.headers,
            "downloader": self.downloader,
            "strategy": self.strategy,
        }

        data.update(self._gen_file_downloader_options())

        # Return update object with which handles downloading,
        # extracting updates
        if app is True:
            # AppUpdate is a subclass of LibUpdate that add methods
            # to restart the application
            return AppUpdate(data)
        else:
            return LibUpdate(data)

    def add_progress_hook(self, cb):
        """Add a download progress callback function to the list of progress
        hooks.

        total:  Total size of the file to download

        downloaded: The amount of bytes that have been downloaded so far.

        percent_complete: The percentage downloaded so far

        status: Status of download

        Args:

        cb (function): Function which takes a dict as its first argument
        """
        self.progress_hooks.append(cb)

    def _get_signing_key(self):

        # Here we will download the keys.gz file, decompress it then return
        # its contents. If an error happens you'll get None.
        key_data_str = self._get_key_data()
        if key_data_str is None:
            return

        # Key data dict
        key_data = json.loads(key_data_str.decode("utf-8"))

        # Get the public key so we can verify it's authenticity with the
        # root public key.
        pub_key = key_data["app_public"]

        if not isinstance(pub_key, bytes):
            pub_key = bytes(pub_key, encoding="utf-8")

        # The signature that we'll validate
        sig = key_data["signature"]

        # Let's generate our signing key.
        signing_key = VerifyKey(self.root_key, UnpaddedBase64Encoder)

        try:
            sig = UnpaddedBase64Encoder.decode(sig)
            signing_key.verify(pub_key, sig)
        except Exception as err:
            # This is bad. Very bad.
            # Create another keypack.pyu & import it not your repo.
            log.debug("Key file not verified")
            log.debug(err, exc_info=True)
        else:
            # Everything checks out
            log.debug("Key file verified")
            self.app_key = pub_key

    # Here we attempt to read the manifest from the filesystem
    # in case of no Internet connection. Useful when an update
    # needs to be installed without an network connection
    def _get_manifest_from_disk(self):
        with _ChDir(self.data_dir):
            # This could be the first run or an accidental deletion of the
            # cached version manifest.
            if os.path.exists(self.version_file):
                filename = self.version_file
            elif os.path.exists(self.version_file_compat):
                filename = self.version_file_compat
            else:
                return None

            log.debug("Found version file on file system")
            # Attempt to open the cached version file
            try:
                with open(filename, "rb") as f:
                    data = f.read()
                log.debug("Loaded version file from file system")
            except Exception as err:
                log.debug("Failed to load version file from file " "system")
                log.debug(err, exc_info=True)
                return None

            # Attempt the decompress
            try:
                decompressed_data = _gzip_decompress(data)
            except Exception as err:
                log.debug(err)
                return None

            return decompressed_data

    # Downloading the manifest. If successful also writes it to file-system
    def _get_manifest_from_http(self):
        log.debug("Downloading online version file")
        version_files = [self.version_file, self.version_file_compat]

        for vf in version_files:
            try:
                if self.downloader:
                    fd = self.downloader(vf, self.update_urls)
                else:
                    fd = FileDownloader(
                        vf,
                        self.update_urls,
                        verify=self.verify,
                        max_download_retries=self.max_download_retries,
                        headers=self.headers,
                        http_timeout=self.http_timeout,
                    )
                data = fd.download_verify_return()
                try:
                    decompressed_data = _gzip_decompress(data)
                except IOError:
                    log.debug("Failed to decompress gzip file")
                    # Will be caught down below.
                    # Just logging the error
                    raise
                log.debug("Version file download successful")
                # Writing version file to application data directory
                self._write_manifest_to_filesystem(decompressed_data, vf)
                return decompressed_data
            except Exception as err:
                log.debug(err, exc_info=True)
                continue

        log.debug("Version file download failed")
        return None

    # Downloading the key file.
    def _get_key_data(self):
        log.debug("Downloading key file")
        try:
            if self.downloader:
                fd = self.downloader(self.key_file, self.update_urls)
            else:
                fd = FileDownloader(
                    self.key_file,
                    self.update_urls,
                    verify=self.verify,
                    max_download_retries=self.max_download_retries,
                    headers=self.headers,
                    http_timeout=self.http_timeout,
                )
            data = fd.download_verify_return()
            try:
                decompressed_data = _gzip_decompress(data)
            except IOError:
                log.debug("Failed to decompress gzip file")
                raise
            log.debug("Key file download successful")
            # Writing version file to application data directory
            self._write_manifest_to_filesystem(decompressed_data, self.key_file)
            return decompressed_data
        except Exception as err:
            log.debug("Version file download failed")
            log.debug(err, exc_info=True)
            return None

    # Adds the ability to apply updates when there isn't an
    # Internet connection.
    def _write_manifest_to_filesystem(self, data, filename):
        with _ChDir(self.data_dir):
            log.debug("Writing %s file to disk", filename)
            with gzip.open(filename, "wb") as f:
                f.write(data)

    # We first attempt to download the version manifest. If that fails
    # we try to load a cached version manifest from disk. Once we have
    # the data in memory we'll verify it's signature.
    def _get_update_manifest(self):
        log.debug("Loading version file...")

        data = self._get_manifest_from_http()
        if data is None:
            data = self._get_manifest_from_disk()

        if data is not None:
            try:
                log.debug("Data type: %s", type(data))
                # If json fails to load self.ready will stay false
                # which will cause _update_check to exit early
                self.json_data = json.loads(data.decode("utf-8"))

                # Ready to check for updates.
                self.ready = True
            except ValueError as err:
                # Malformed json???
                log.debug("Json failed to load: ValueError")
                log.debug(err, exc_info=True)
            except Exception as err:
                # Catch all for debugging purposes.
                # If seeing this line come up a lot in debug logs
                # please open an issue on github or submit a pull request
                log.debug(err, exc_info=True)
        else:
            log.debug(
                "Failed to download version file & no " "version file on filesystem"
            )
            self.json_data = {}

        # If verified we set self.verified to True.
        self._verify_sig(self.json_data)

        self.easy_data = _EAD(self.json_data)

    # Verify the signature of the version manifest.
    def _verify_sig(self, data):
        if self.app_key is None:
            log.debug("App key is None")
            return

        # Checking to see if there is a signature key in the version file.
        if "signature" in data.keys():
            signature = data["signature"]
            log.debug("Deleting signature from update data")
            # We are removing the signature to prepare the data
            # for verification.
            del data["signature"]

            update_data = json.dumps(data, sort_keys=True)

            pub_key = VerifyKey(self.app_key, UnpaddedBase64Encoder)

            if not isinstance(update_data, bytes):
                update_data = bytes(update_data, encoding="utf-8")

            try:
                signature = UnpaddedBase64Encoder.decode(signature)
                pub_key.verify(update_data, signature)
            except Exception as err:
                log.debug("Version file not verified")
                log.debug(err, exc_info=True)
            else:
                log.debug("Version file verified")
                self.verified = True
        else:
            log.debug("Signature not in update data")

    def _setup(self):
        # Create required directories on end-users computer
        # to place verified update data
        # Very safe director maker :)
        log.debug("Setting up directories...")
        dirs = [self.data_dir, self.update_folder]
        for d in dirs:
            if not os.path.exists(d):
                log.debug("Creating directory: %s", d)
                os.makedirs(d)

    @staticmethod
    def _sanitize_update_url(urls):
        sanitized_urls = []
        # Adds trailing slash to end of url if not already provided.
        # Doing this so when requesting online resources we only
        # need to add the resource name to the end of the request.
        for u in urls:
            if not u.endswith("/"):
                sanitized_urls.append(u + "/")
            else:
                sanitized_urls.append(u)
        # Removing duplicates
        return list(set(sanitized_urls))
