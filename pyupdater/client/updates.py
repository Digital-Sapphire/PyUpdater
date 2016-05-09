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
import threading

from jms_utils.paths import get_mac_dot_app_dir, remove_any

from pyupdater import settings
from pyupdater.client.downloader import FileDownloader
from pyupdater.client.patcher import Patcher
from pyupdater.package_handler.package import cleanup_old_archives
from pyupdater.utils import (get_filename,
                             get_hash,
                             get_highest_version,
                             lazy_import,
                             Restarter)
from pyupdater.utils.exceptions import ClientError


@lazy_import
def io():
    import io
    return io


@lazy_import
def logging():
    import logging
    return logging


@lazy_import
def os():
    import os
    return os


@lazy_import
def shutil():
    import shutil
    return shutil


@lazy_import
def sys():
    import sys
    return sys


@lazy_import
def tarfile():
    import tarfile
    return tarfile


@lazy_import
def warnings():
    import warnings
    return warnings


@lazy_import
def zipfile():
    import zipfile
    return zipfile


@lazy_import
def jms_utils():
    import jms_utils
    import jms_utils.paths
    import jms_utils.system
    return jms_utils


log = logging.getLogger(__name__)


class LibUpdate(object):
    """Used to update library files used by an application

    Args:

        data (dict): Info dict
    """

    def __init__(self, data):
        self.updates_key = settings.UPDATES_KEY
        self.update_urls = data.get('update_urls')
        self.name = data.get('name')
        self.version = data.get('version')
        self.easy_data = data.get('easy_data')
        # Raw form of easy_data
        self.json_data = data.get('json_data')
        self.data_dir = data.get('data_dir')
        self.platform = data.get('platform')
        self.app_name = data.get('app_name')
        self.channel = data.get('channel', 'stable')
        self.progress_hooks = data.get('progress_hooks')
        self.update_folder = os.path.join(self.data_dir,
                                          settings.UPDATE_FOLDER)
        self.verify = data.get('verify', True)
        self.current_app_dir = os.path.dirname(sys.executable)
        self.status = False
        # If user is using async download this will be True.
        # Future calls to an download methods will not run
        # until the current download is complete. Which will
        # set this back to False.
        self._is_downloading = False

        # Used to generate file name of archive
        latest = get_highest_version(self.name, self.platform,
                                     self.channel, self.easy_data)
        # Get full filename of latest update archive
        self.filename = get_filename(self.name, latest, self.platform,
                                     self.easy_data)
        assert self.filename is not None
        self.abspath = os.path.join(self.update_folder, self.filename)
        # Removes old versions, of update being checked, from
        # updates folder.  Since we only start patching from
        # the current binary this shouldn't be a problem.
        self.cleanup()

    def is_downloaded(self):
        """Returns (bool):

            True: File is already downloaded.

            False: File hasn't already been downloaded.
        """
        if self.name is None or self._is_downloading is True:
            return False
        return self._is_downloaded(self.name)

    def download(self, async=False):
        if async is True:
            if self._is_downloading is False:
                self._is_downloading = True
                threading.Thread(target=self._download).start()
        else:
            if self._is_downloading is False:
                self._is_downloading = True
                return self._download()

    def _download(self):
        """Will download the package update that was referenced
        with check update.

        Proxy method for :meth:`_patch_update` & :meth:`_full_update`.

        Returns:

            (bool) Meanings:

                True - Download successful

                False - Download failed
        """
        if self.name is not None:
            # Tested elsewhere
            if self._is_downloaded(self.name) is True:  # pragma: no cover
                self.status = True
            else:
                log.info('Starting patch download')
                patch_success = False
                if self.channel == 'stable':
                    patch_success = self._patch_update(self.name, self.version)
                # Tested elsewhere
                if patch_success:  # pragma: no cover
                    self.status = True
                    log.info('Patch download successful')
                else:
                    log.error('Patch update failed')
                    log.info('Starting full download')
                    update_success = self._full_update(self.name)
                    if update_success:
                        self.status = True
                        log.info('Full download successful')
                    else:  # pragma: no cover
                        log.error('Full download failed')

            self._is_downloading = False
            return self.status

    def extract(self):
        """Will extract archived update and leave in update folder.
        If updating a lib you can take over from there. If updating
        an app this call should be followed by :meth:`restart` to
        complete update.

        Returns:

            (bool) Meanings:

                True - Install successful

                False - Install failed
        """
        if jms_utils.system.get_system() == 'win':  # Tested elsewhere
            log.warning('Only supported on Unix like systems')
            return False
        try:
            self._extract_update()
        except ClientError as err:
            log.error(err)
            log.debug(err, exc_info=True)
            return False
        return True

    def _extract_update(self):
        with jms_utils.paths.ChDir(self.update_folder):
            if not os.path.exists(self.filename):
                log.error('File does not exists')
                raise ClientError('File does not exists', expected=True)

            log.info('Extracting Update')
            archive_ext = os.path.splitext(self.filename)[1].lower()
            # Handles extracting gzip or zip archives
            if archive_ext == '.gz':
                try:
                    with tarfile.open(self.filename, 'r:gz') as tfile:
                        # Extract file update to current
                        # directory.
                        tfile.extractall()
                except Exception as err:  # pragma: no cover
                    log.error(err)
                    log.debug(err, exc_info=True)
                    raise ClientError('Error reading gzip file')
            elif archive_ext == '.zip':
                try:
                    with zipfile.ZipFile(self.filename, 'r') as zfile:
                        # Extract update file to current
                        # directory.
                        zfile.extractall()
                except Exception as err:  # pragma: no cover
                    log.error(err)
                    log.debug(err, exc_info=True)
                    raise ClientError('Error reading zip file')
            else:
                raise ClientError('Unknown filetype')

    # Checks if latest update is already downloaded
    def _is_downloaded(self, name):
        latest = get_highest_version(name, self.platform,
                                     self.channel, self.easy_data)

        filename = get_filename(name, latest, self.platform, self.easy_data)

        hash_key = '{}*{}*{}*{}*{}'.format(self.updates_key, name,
                                           latest, self.platform,
                                           'file_hash')
        _hash = self.easy_data.get(hash_key)
        # Comparing file hashes to ensure security
        with jms_utils.paths.ChDir(self.update_folder):
            if not os.path.exists(filename):
                return False
            try:
                with open(filename, 'rb') as f:
                    data = f.read()
            except Exception as err:
                log.debug(err, exc_info=True)
                return False
            if _hash == get_hash(data):
                return True
            else:
                return False

    # Handles patch updates
    def _patch_update(self, name, version):  # pragma: no cover
        log.info('Starting patch update')
        filename = get_filename(name, version, self.platform, self.easy_data)
        log.debug('Archive filename: %s', filename)
        if filename is None:
            log.warning('Make sure version numbers are correct. '
                        'Possible TRAP!')
            return False
        latest = get_highest_version(name, self.platform,
                                     self.channel, self.easy_data)
        # Just checking to see if the zip for the current version is
        # available to patch If not we'll just do a full binary download
        if not os.path.exists(os.path.join(self.update_folder, filename)):
            log.warning('%s got deleted. No base binary to start patching '
                        'form', filename)
            return False

        # Initilize Patch object with all required information
        p = Patcher(name=name, json_data=self.json_data,
                    current_version=version, latest_version=latest,
                    update_folder=self.update_folder,
                    update_urls=self.update_urls, verify=self.verify,
                    progress_hooks=self.progress_hooks)

        # Returns True if everything went well
        # If False is returned then we will just do the full
        # update.
        return p.start()

    # Starting full update
    def _full_update(self, name):
        log.info('Starting full update')
        latest = get_highest_version(name, self.platform,
                                     self.channel, self.easy_data)

        filename = get_filename(name, latest, self.platform, self.easy_data)

        hash_key = '{}*{}*{}*{}*{}'.format(self.updates_key, name,
                                           latest, self.platform,
                                           'file_hash')
        file_hash = self.easy_data.get(hash_key)

        with jms_utils.paths.ChDir(self.update_folder):
            log.info('Downloading update...')
            fd = FileDownloader(filename, self.update_urls,
                                file_hash, self.verify, self.progress_hooks)
            result = fd.download_verify_write()
            if result:
                log.info('Download Complete')
                return True
            else:  # pragma: no cover
                log.error('Failed To Download Latest Version')
                return False

    def cleanup(self):
        log.debug('Beginning removal of old updates')

        filename = get_filename(self.name, self.version,
                                self.platform, self.easy_data)

        cleanup_old_archives(filename, self.update_folder)


class AppUpdate(LibUpdate):
    """Used to update library files used by an application

    Args:

        data (dict): Info dict
    """

    def __init__(self, data):
        super(AppUpdate, self).__init__(data)

    def extract_restart(self):  # pragma: no cover
        """Will extract the update, overwrite the current app,
        then restart the app using the updated binary."""
        try:
            self._extract_update()

            if jms_utils.system.get_system() == 'win':
                self._win_overwrite_app_restart()
            else:
                self._overwrite_app()
                self._restart()
        except ClientError as err:
            log.error(err)
            log.debug(err, exc_info=True)

    def restart(self):  # pragma: no cover
        """Will overwrite old binary with updated binary and
        restart using the updated binary. Not supported on windows.

        Proxy method for :meth:`_overwrite_app` & :meth:`_restart`.
        """
        # On windows we write a batch file to move the update
        # binary to the correct location and restart app.
        if jms_utils.system.get_system() == 'win':
            log.warning('Only supported on Unix like systems')
            return
        try:
            self._overwrite_app()
            self._restart()
        except ClientError as err:
            log.error(err)
            log.debug(err, exc_info=True)

    def _overwrite_app(self):  # pragma: no cover
        # Unix: Overwrites the running applications binary
        if jms_utils.system.get_system() == 'mac':
            if self.current_app_dir.endswith('MacOS') is True:
                log.debug('Looks like we\'re dealing with a Mac Gui')
                # Temp var used for pep 8 compliance
                temp_dir = get_mac_dot_app_dir(self.current_app_dir)
                self.current_app_dir = temp_dir

        app_update = os.path.join(self.update_folder, self.name)
        # Must be dealing with Mac .app application
        if not os.path.exists(app_update):
            app_update += '.app'
        log.debug('Update Location:\n%s', os.path.dirname(app_update))
        log.debug('Update Name: %s', os.path.basename(app_update))

        current_app = os.path.join(self.current_app_dir, self.name)
        # Must be dealing with Mac .app application
        if not os.path.exists(current_app):
            current_app += '.app'
        log.debug('Current App location:\n\n%s', current_app)
        # Remove current app to prevent errors when moving
        # update to new location
        if os.path.exists(current_app):
            remove_any(current_app)

        log.debug('Moving app to new location:\n\n%s', self.current_app_dir)
        shutil.move(app_update, self.current_app_dir)

    def _restart(self):  # pragma: no cover
        # Oh yes i did just pull that new binary into
        # the currently running process and kept it pushing
        # like nobody's business. Windows what???
        log.info('Restarting')
        current_app = os.path.join(self.current_app_dir, self.name)
        if jms_utils.system.get_system() == 'mac':
            # Must be dealing with Mac .app application
            if not os.path.exists(current_app):
                log.debug('Must be a .app bundle')
                current_app += '.app'
                mac_app_binary_dir = os.path.join(current_app, 'Contents',
                                                  'MacOS')
                file_ = os.listdir(mac_app_binary_dir)
                # We are making an assumption here that only 1
                # executable will be in the MacOS folder.
                current_app = os.path.join(mac_app_binary_dir, file_[0])

        r = Restarter(current_app)
        r.restart()

    def _win_overwrite_app_restart(self):  # pragma: no cover
        # Windows: Moves update to current directory of running
        #          application then restarts application using
        #          new update.
        exe_name = self.name + '.exe'
        current_app = os.path.join(self.current_app_dir, exe_name)
        updated_app = os.path.join(self.update_folder, exe_name)

        update_info = dict(data_dir=self.data_dir, updated_app=updated_app)
        r = Restarter(current_app, **update_info)
        r.restart()
