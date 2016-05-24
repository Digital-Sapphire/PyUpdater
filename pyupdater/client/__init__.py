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
import warnings

from jms_utils.helpers import EasyAccessDict, gzip_decompress, Version

from pyupdater import settings, __version__
from pyupdater.client.downloader import FileDownloader
from pyupdater.client.updates import AppUpdate, LibUpdate
from pyupdater.utils import (get_highest_version,
                             lazy_import)
from pyupdater.utils.config import Config


warnings.simplefilter('always', DeprecationWarning)


@lazy_import
def gzip():
    import gzip
    return gzip


@lazy_import
def io():
    import io
    return io


@lazy_import
def json():
    import json
    return json


@lazy_import
def logging():
    import logging
    return logging


@lazy_import
def os():
    import os
    return os


@lazy_import
def appdirs():
    import appdirs
    return appdirs


@lazy_import
def ed25519():
    import ed25519
    return ed25519


@lazy_import
def jms_utils():
    import jms_utils
    import jms_utils.app
    import jms_utils.logger
    import jms_utils.paths
    import jms_utils.system
    return jms_utils


@lazy_import
def six():
    import six
    return six


log = logging.getLogger(__name__)

log_path = os.path.join(jms_utils.paths.app_cwd, 'pyu.log')
if os.path.exists(log_path):  # pragma: no cover
    ch = logging.FileHandler(os.path.join(jms_utils.paths.app_cwd,
                             'pyu.log'))
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(jms_utils.logger.logging_formatter)
    log.addHandler(ch)
log.debug('PyUpdater Version %s', __version__)


class Client(object):
    """Used on client side to update files

    Kwargs:

        obj (instance): config object

        refresh (bool) Meaning:

            True: Refresh update manifest on object initialization

            False: Don't refresh update manifest on object initialization

        call_back (func): Used for download progress
    """
    def __init__(self, obj=None, refresh=False,
                 progress_hooks=None, test=False):
        self.name = None
        self.version = None
        self.json_data = None
        self.verified = False
        self.ready = False
        self.progress_hooks = []
        if progress_hooks is not None:
            assert isinstance(progress_hooks, list) is True
            self.progress_hooks += progress_hooks
        if obj is not None:
            self.init_app(obj, refresh, test)

    def init_app(self, obj, refresh=False, test=False):
        """Sets up client with config values from obj

        Args:

            obj (instance): config object

        Kwargs:

            refresh (bool) Meaning:

            True: Refresh update manifest on object initialization

            False: Don't refresh update manifest on object initialization

        """
        # Used to add missing required information
        # i.e. APP_NAME
        config = Config()
        config.from_object(obj)

        self.FROZEN = jms_utils.app.FROZEN
        # Grabbing config information
        update_urls = config.get('UPDATE_URLS')
        # Here we combine all urls & add trailing / if one isn't present
        self.update_urls = self._sanatize_update_url(update_urls)
        self.app_name = config.get('APP_NAME', 'PyUpdater')
        self.company_name = config.get('COMPANY_NAME', 'Digital Sapphire')
        if test:
            # Making platform deterministic for tests.
            # No need to test for other platforms at the moment
            self.data_dir = obj.DATA_DIR
            self.platform = 'mac'
        else:  # pragma: no cover
            # Getting platform specific application directory
            self.data_dir = appdirs.user_data_dir(self.app_name,
                                                  self.company_name,
                                                  roaming=True)
            # Setting the platform to pass when requesting updates
            self.platform = jms_utils.system.get_system()
        # Creating update folder. Using settings to ease change in future
        self.update_folder = os.path.join(self.data_dir,
                                          settings.UPDATE_FOLDER)
        # Attempting to sanitize incorrect inputs types
        self.root_key = config.get('PUBLIC_KEY', '')
        self.app_key = None

        # Config option to disable tls cert verification
        self.verify = config.get('VERIFY_SERVER_CERT', True)
        self.version_file = settings.VERSION_FILE
        self.key_file = settings.KEY_FILE

        self._setup()
        if refresh is True:
            self.refresh()

    def refresh(self):
        "Will download and verify your version file."
        self._get_signing_key()
        self._get_update_manifest()

    def update_check(self, name, version, channel='stable'):
        """
        Will try to patch binary if all check pass.  IE hash verified
        signature verified.  If any check doesn't pass then falls back to
        full update

        Args:

            name (str): Name of file to update

            version (str): Current version number of file to update

            channel (str): Release channel

        Returns:

            (bool) Meanings:

                True - Update Successful

                False - Update Failed
        """
        return self._update_check(name, version, channel)

    def _update_check(self, name, version, channel):
        valid_channels = ['alpha', 'beta', 'stable']
        if channel not in valid_channels:
            log.error('Invalid channel. May need to check spelling')
            channel = 'stable'
        self.name = name
        version = Version(version)
        self.version = str(version)

        # Will be set to true if we are updating an app and not a lib
        app = False

        # No json data is loaded.
        # User may need to call refresh
        if self.ready is False:
            log.warning('No update manifest found')
            return None

        # If we are an app we will need restart functionality.
        # AppUpdate instead of LibUpdate
        if self.FROZEN is True and self.name == self.app_name:
            app = True
        # Checking if version file is verified before
        # processing data contained in the version file.
        # This was done by self._get_update_manifest()
        if self.verified is False:
            log.error('Failed version file verification')
            return None
        log.info('Checking for %s updates...', name)

        # If None is returned get_highest_version could
        # not find the supplied name in the version file
        latest = get_highest_version(name, self.platform,
                                     channel, self.easy_data)
        if latest is None:
            log.debug('Could not find the latest version')
            return None
        latest = Version(latest)
        log.debug('Current vesion: %s', str(version))
        log.debug('Latest version: %s', str(latest))
        needed = latest > version
        log.debug('Update Needed: %s', needed)
        if latest <= version:
            log.info('%s already updated to the latest version', name)
            return None
        # Hey, finally made it to the bottom!
        # Looks like its time to do some updating
        data = {
            'update_urls': self.update_urls,
            'name': self.name,
            'version': self.version,
            'easy_data': self.easy_data,
            'json_data': self.json_data,
            'data_dir': self.data_dir,
            'platform': self.platform,
            'channel': channel,
            'app_name': self.app_name,
            'verify': self.verify,
            # Ensure single occurrence of each callbackc
            'progress_hooks': list(set(self.progress_hooks)),
            }
        # Return update object with which handles downloading,
        # extracting updates
        if app is True:
            # AppUpdate objects also has methods to restart
            # the app with the new version
            return AppUpdate(data)
        else:
            return LibUpdate(data)

    # Adding callbacks to be passed to client.downloader.FileDownloader
    def add_progress_hook(self, cb):
        self.progress_hooks.append(cb)

    def _get_signing_key(self):
        key_data_str = self._download_key()
        if key_data_str is None:
            return

        key_data = json.loads(key_data_str.decode('utf-8'))
        pub_key = key_data['app_public']
        if six.PY3:
            if not isinstance(pub_key, bytes):
                pub_key = bytes(pub_key, encoding='utf-8')
        else:
            pub_key = str(pub_key)

        sig = key_data['signature']
        signing_key = ed25519.VerifyingKey(self.root_key, encoding='base64')

        try:
            signing_key.verify(sig, pub_key, encoding='base64')
        except Exception as err:
            log.warning('Key file not verified')
            log.error(err)
            log.debug(err, exc_info=True)
        else:
            log.info('Key file verified')
            self.app_key = pub_key

    # Here we attempt to read the manifest from the filesystem
    # in case of no Internet connection. Useful for an update
    # needs to be installed without an network connection
    def _get_manifest_filesystem(self):
        data = None
        with jms_utils.paths.ChDir(self.data_dir):
            if not os.path.exists(self.version_file):
                log.warning('No version file on file system')
                return data
            else:
                log.info('Found version file on file system')
                try:
                    with open(self.version_file, 'rb') as f:
                        data = f.read()
                    log.info('Loaded version file from file system')
                except Exception as err:
                    # Whatever the error data is already set to None
                    log.error('Failed to load version file from file '
                              'system')
                    log.debug(err, exc_info=True)
                # In case we don't have any data to pass
                # Catch the error here and just return None
                try:
                    decompressed_data = gzip_decompress(data)
                except Exception as err:
                    decompressed_data = None

                return decompressed_data

    # Downloading the manifest. If successful also writes it to file-system
    def _download_manifest(self):
        log.info('Downloading online version file')
        try:
            fd = FileDownloader(self.version_file, self.update_urls,
                                verify=self.verify)
            data = fd.download_verify_return()
            try:
                decompressed_data = gzip_decompress(data)
            except IOError:
                log.error('Failed to decompress gzip file')
                # Will be caught down below.
                # Just logging the error
                raise
            log.info('Version file download successful')
            # Writing version file to application data directory
            self._write_manifest_2_filesystem(decompressed_data)
            return decompressed_data
        except Exception as err:
            log.error('Version file download failed')
            log.debug(err, exc_info=True)
            return None

    # Downloading the key file.
    def _download_key(self):
        log.info('Downloading key file')
        try:
            fd = FileDownloader(self.key_file, self.update_urls,
                                verify=self.verify)
            data = fd.download_verify_return()
            try:
                decompressed_data = gzip_decompress(data)
            except IOError:
                log.error('Failed to decompress gzip file')
                # Will be caught down below. Just logging the error
                raise
            log.info('Key file download successful')
            # Writing version file to application data directory
            self._write_manifest_2_filesystem(decompressed_data)
            return decompressed_data
        except Exception as err:
            log.error('Version file download failed')
            log.debug(err, exc_info=True)
            return None

    def _write_manifest_2_filesystem(self, data):
        with jms_utils.paths.ChDir(self.data_dir):
            log.debug('Writing version file to disk')
            with gzip.open(self.version_file, 'wb') as f:
                f.write(data)

    def _get_update_manifest(self):
        #  Downloads & Verifies version file signature.
        log.info('Loading version file...')

        data = self._download_manifest()
        if data is None:
            # Its ok if this is None. If any exceptions are raised
            # that we can't handle we will just return an empty
            # dictionary.
            data = self._get_manifest_filesystem()

        if data is not None:
            try:
                log.debug('Data type: %s', type(data))
                self.json_data = json.loads(data.decode('utf-8'))
                # Ready to check for updates.
                # If json fails to load self.ready will stay false
                # which will cause _update_check to exit early
                self.ready = True
            except ValueError as err:
                # Malformed json???
                log.debug(err, exc_info=True)
                log.error('Json failed to load: ValueError')
            except Exception as err:
                # Catch all for debugging purposes.
                # If seeing this line come up a lot in debug logs
                # please open an issue on github or submit a pull request
                log.error(err)
                log.debug(err, exc_info=True)
        else:
            # Setting to default dict to not raise any errors
            # in _verify_sig
            log.debug('Failed to download version file & no '
                      'version file on filesystem')
            self.json_data = {}

        # If verified we set self.verified to True.
        # We return the data either way
        self._verify_sig(self.json_data)

        self.easy_data = EasyAccessDict(self.json_data)
        log.debug('Version Data:\n%s', str(self.easy_data))

    def _verify_sig(self, data):
        if self.app_key is None:
            log.debug('App key is None')
            return

        # Checking to see if there is a signature key in the version file.
        if 'signature' in data.keys():
            signature = data['signature']
            log.debug('Deleting signature from update data')
            del data['signature']

            # After removing the signatures we turn the json data back
            # into a string to use as data to verify the sig.
            update_data = json.dumps(data, sort_keys=True)

            pub_key = ed25519.VerifyingKey(self.app_key, encoding='base64')
            if six.PY3:
                if not isinstance(update_data, bytes):
                    update_data = bytes(update_data, encoding='utf-8')
            try:
                pub_key.verify(signature, update_data, encoding='base64')
            except Exception as err:
                log.warning('Version file not verified')
                log.error(err)
                log.debug(err, exc_info=True)
            else:
                log.info('Version file verified')
                self.verified = True
        else:
            log.debug('Signature not in update data')

    def _setup(self):
        # Sets up required directories on end-users computer
        # to place verified update data
        # Very safe director maker :)
        log.info('Setting up directories...')
        dirs = [self.data_dir, self.update_folder]
        for d in dirs:
            if not os.path.exists(d):
                log.info('Creating directory: %s', d)
                os.makedirs(d)

    # Legacy code used when migrating from single urls to
    # A list of urls
    def _sanatize_update_url(self, urls):
        _urls = []
        # Making sure final output is a list
        if isinstance(urls, list):
            _urls += urls
        elif isinstance(urls, six.string_types):
            log.warning('UPDATE_URLS value should only be a list.')
            _urls.append(urls)
        elif isinstance(urls, tuple):
            _urls += list(urls)

        sanatized_urls = []
        # Adds trailing slash to end of url if not already provided.
        # Doing this so when requesting online resources we only
        # need to add the resouce name to the end of the request.
        for u in _urls:
            if not u.endswith('/'):
                sanatized_urls.append(u + '/')
            else:
                sanatized_urls.append(u)
        # Removing duplicates
        return list(set(sanatized_urls))
