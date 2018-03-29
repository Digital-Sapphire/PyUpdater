# ------------------------------------------------------------------------------
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
# ------------------------------------------------------------------------------
from __future__ import unicode_literals
import io
import logging
import os
import shutil
import subprocess
import sys
import tarfile
import threading
import zipfile

from dsdev_utils.helpers import Version
from dsdev_utils.paths import ChDir, get_mac_dot_app_dir, remove_any
from dsdev_utils.system import get_system

from pyupdater import settings
from pyupdater.client.downloader import FileDownloader, get_hash
from pyupdater.client.patcher import Patcher
from pyupdater.package_handler.package import remove_previous_versions
from pyupdater.utils.exceptions import ClientError


log = logging.getLogger(__name__)


def _get_highest_version(name, plat, channel, easy_data, strict):
    # Parses version file and returns the highest version number.
    #
    #   Args:
    #
    #      name (str): name of file to search for updates
    #
    #      plat (str): the platform we are requesting for
    #
    #      channel (str): the release channel
    #
    #      easy_data (dict): data file to search
    #
    #      strict (bool): specify whether or not to take the channel
    #                     into consideration
    #
    #   Returns:
    #
    #      (str) Highest version number

    # We grab all keys and return the version corresponding to the
    # channel passed to this function
    version_key_alpha = '{}*{}*{}*{}'.format('latest', name, 'alpha', plat)
    version_key_beta = '{}*{}*{}*{}'.format('latest', name, 'beta', plat)
    version_key_stable = '{}*{}*{}*{}'.format('latest', name, 'stable', plat)
    version = None

    version_options = []

    alpha_available = False
    alpha_str = easy_data.get(version_key_alpha)
    if alpha_str is not None:
        log.debug('Alpha str: %s', alpha_str)
        alpha = Version(alpha_str)
        version_options.append(alpha)
        alpha_available = True

    beta_available = False
    beta_str = easy_data.get(version_key_beta)
    if beta_str is not None:
        log.debug('Beta str: %s', beta_str)
        beta = Version(beta_str)
        version_options.append(beta)
        beta_available = True

    stable_str = easy_data.get(version_key_stable)
    stable_available = False
    if stable_str is not None:
        log.debug('Stable str: %s', stable_str)
        stable = Version(stable_str)
        version_options.append(stable)
        stable_available = True

    if strict is False:
        return str(max(version_options))

    if alpha_available is True and channel == 'alpha':
        version = alpha

    if beta_available is True and channel == 'beta':
        version = beta

    if stable_available is True and channel == 'stable':
        version = stable

    if version is not None:
        log.debug('Highest version: %s', version)
        return str(version)
    else:
        log.info('No updates for "%s" on %s exists', name, plat)
        return version


def gen_user_friendly_version(internal_version):
    channel = {0: 'Alpha', 1: 'Beta'}
    v = list(map(int, internal_version.split('.')))

    # 1.2
    version = '{}.{}'.format(v[0], v[1])
    if v[2] != 0:
        # 1.2.1
        version += '.{}'.format(v[2])
    if v[3] != 2:
        # 1.2.1 Alpha
        version += ' {}'.format(channel[v[3]])
        if v[4] != 0:
            version += ' {}'.format(v[4])

    return version


class Restarter(object):

    def __init__(self, current_app, **kwargs):
        self.current_app = current_app
        self.name = kwargs.get('name', "")
        log.debug('Current App: %s', self.current_app)
        self.is_win = sys.platform == 'win32'
        if self.is_win is True:
            self.data_dir = kwargs.get('data_dir')
            self.bat_file = os.path.join(self.data_dir, 'update.bat')
            self.vbs_file = os.path.join(self.data_dir, 'invis.vbs')
            self.updated_app = kwargs.get('updated_app')
            log.debug('Restart script dir: %s', self.data_dir)
            log.debug('Update path: %s', self.updated_app)

    def process(self, win_restart=True):
        if self.is_win:
            if win_restart is True:
                self._win_overwrite_restart()
            else:
                self._win_overwrite()
        else:
            self._restart()

    def _restart(self):
        os.execl(self.current_app, self.name)

    def _win_overwrite(self):
        isFolder = os.path.isdir(self.updated_app)
        with io.open(self.bat_file, 'w') as bat:
            if isFolder:
                bat.write("""
@echo off
echo Updating to latest version...
ping 127.0.0.1 -n 5 -w 1000 > NUL
robocopy "{}" "{}" /e /move /V /PURGE > NUL
DEL "{}"
DEL "%~f0"
""".format(self.updated_app, self.current_app, self.vbs_file))
            else:
                bat.write("""
@echo off
echo Updating to latest version...
ping 127.0.0.1 -n 5 -w 1000 > NUL
move /Y "{}" "{}" > NUL
DEL "{}"
DEL "%~f0"
""".format(self.updated_app, self.current_app, self.vbs_file))

        with io.open(self.vbs_file, 'w') as vbs:
            # http://www.howtogeek.com/131597/can-i-run-a-windows-batch-
            # file-without-a-visible-command-prompt/
            vbs.write('CreateObject("Wscript.Shell").Run """" '
                      '& WScript.Arguments(0) & """", 0, False')
        log.debug('Starting update batch file')
        args = ['wscript.exe', self.vbs_file, self.bat_file]
        subprocess.Popen(args)
        os._exit(0)

    def _win_overwrite_restart(self):
        isFolder = os.path.isdir(self.updated_app)
        with io.open(self.bat_file, 'w') as bat:
            if isFolder:
                bat.write("""
@echo off
echo Updating to latest version...
ping 127.0.0.1 -n 5 -w 1000 > NUL
robocopy "{}" "{}" /e /move /V > NUL
echo restarting...
start "" "{}"
DEL "{}"
DEL "%~f0"
""".format(self.updated_app, self.current_app,
                    os.path.join(self.current_app,
                                 '.'.join([self.name, 'exe'])),
                    self.vbs_file))
            else:
                bat.write("""
@echo off
echo Updating to latest version...
ping 127.0.0.1 -n 5 -w 1000 > NUL
move /Y "{}" "{}" > NUL
echo restarting...
start "" "{}"
DEL "{}"
DEL "%~f0"
""".format(self.updated_app, self.current_app,
                    self.current_app, self.vbs_file))
        with io.open(self.vbs_file, 'w') as vbs:
            # http://www.howtogeek.com/131597/can-i-run-a-windows-batch-
            # file-without-a-visible-command-prompt/
            vbs.write('CreateObject("Wscript.Shell").Run """" '
                      '& WScript.Arguments(0) & """", 0, False')
        log.debug('Starting update batch file')
        args = ['wscript.exe', self.vbs_file, self.bat_file]
        subprocess.Popen(args)
        os._exit(0)


class LibUpdate(object):
    """Used to update library files used by an application. This object is
    returned by pyupdater.client.Client.update_check

    ######Args:

    data (dict): Info dict
    """

    def __init__(self, data=None):
        if data is None:
            return
        # A key used in the version meta data dictionary
        self._updates_key = settings.UPDATES_KEY

        # The current directory of the running executable
        self._current_app_dir = os.path.dirname(sys.executable)

        # The status of the download. Once downloaded this will be True
        self._download_status = False

        # If user is using async download this will be True.
        # Future calls to an download methods will not run
        # until the current download is complete. Which will
        # set this back to False.
        self._is_downloading = False

        # Used with the version property.
        # Returns a user friendly version string
        self._version = ""

        # Dictionary of config variables
        self.init_data = data

        # List of urls used to look for meta data & updates
        self.update_urls = data.get('update_urls')

        # The name of the asset we are targeting. Provided by user
        # in update_check
        self.name = data.get('name')

        # The APP_NAME  specified in the client_config.py
        self.app_name = data.get('app_name')

        # The version of the current asset
        self.current_version = data.get('version')

        # A special dictionary that allows getting nested values by
        # providing a key in the form of "this*is*a*deep*key".
        self.easy_data = data.get('easy_data')

        # Raw form of easy_data
        self.json_data = data.get('json_data')

        # The directory used to store files needed for the restart process
        # on windows
        self.data_dir = data.get('data_dir')

        # The platform we are targeting
        self.platform = data.get('platform')

        # The channel we are targeting
        self.channel = data.get('channel', 'stable')

        # How strict to treat the channel requirement
        self.strict = data.get('strict')

        # Progress callbacks
        self.progress_hooks = data.get('progress_hooks')

        # The folder on the end users system which hold meta data & updates
        self.update_folder = os.path.join(self.data_dir,
                                          settings.UPDATE_FOLDER)

        # Weather or not the verify the https connection
        self.verify = data.get('verify', True)

        # Extra headers to pass to urllib3
        self.urllib3_headers = data.get('urllib3_headers')

        # The amount of times to retry a url before giving up
        self.max_download_retries = data.get('max_download_retries')

        # The latest version available
        self.latest = _get_highest_version(self.name, self.platform,
                                           self.channel, self.easy_data,
                                           self.strict)

        # The name of the current versions update archive.
        # Will be used to check if the current archive is available for a
        # patch update
        cv = self.current_version
        self._current_archive_name = LibUpdate._get_filename(self.name,
                                                             # PEP8
                                                             cv,
                                                             self.platform,
                                                             self.easy_data)

        # Get filename of latest versions update archive
        self.filename = LibUpdate._get_filename(self.name, self.latest,
                                                self.platform, self.easy_data)
        assert self.filename is not None

        # Used to remove version earlier than the current.
        # ToDo: Run in background thread
        self.cleanup()
        # End ToDo

    @property
    def version(self):
        """Generates a user friendly version string

        ######Returns (str): User friendly version string
        """
        if self._version == "":
            self._version = gen_user_friendly_version(self.latest)
        return self._version

    def is_downloaded(self):
        """Used to check if update has been downloaded.

        ######Returns (bool):

            True - File is already downloaded.

            False - File has not been downloaded.
        """
        if self._is_downloading is True:
            return False
        return self._is_downloaded()

    def download(self, async=False):
        """Downloads update

        ######Args:

            async (bool): Perform download in background thread
        """
        if async is True:
            if self._is_downloading is False:
                self._is_downloading = True
                threading.Thread(target=self._download).start()
        else:
            if self._is_downloading is False:
                self._is_downloading = True
                return self._download()

    def extract(self):
        """Will extract the update from its archive to the update folder.
        If updating a lib you can take over from there. If updating
        an app this call should be followed by method "restart" to
        complete update.

        ######Returns:

            (bool) True - Extract successful. False - Extract failed.
        """
        if get_system() == 'win':  # Tested elsewhere
            log.debug('Only supported on Unix like systems')
            return False
        try:
            self._extract_update()
        except ClientError as err:
            log.debug(err, exc_info=True)
            return False
        return True

    @staticmethod
    def _get_filename(name, version, platform, easy_data):
        """Gets full filename for given name & version combo

            Args:

                name (str): Name of file

                version (str): Version of file to get full filename for

                easy_data (dict): Data file to search

            Returns:

                (str) Filename with extension
        """
        filename_key = '{}*{}*{}*{}*{}'.format(settings.UPDATES_KEY, name,
                                               version, platform, 'filename')
        filename = easy_data.get(filename_key)

        log.debug("Filename for %s-%s: %s", name, version, filename)
        return filename

    def _download(self):
        if self.name is not None:
            if self._is_downloaded() is True:  # pragma: no cover
                self._download_status = True
            else:
                log.debug('Starting patch download')
                patch_success = False
                if self.channel == 'stable':
                    patch_success = self._patch_update()
                # Tested elsewhere
                if patch_success:  # pragma: no cover
                    self._download_status = True
                    log.debug('Patch download successful')
                else:
                    log.debug('Patch update failed')
                    log.debug('Starting full download')
                    update_success = self._full_update()
                    if update_success:
                        self._download_status = True
                        log.debug('Full download successful')
                    else:  # pragma: no cover
                        log.debug('Full download failed')

        self._is_downloading = False
        return self._download_status

    def _extract_update(self):
        with ChDir(self.update_folder):
            if not os.path.exists(self.filename):
                log.debug('File does not exists')
                raise ClientError('File does not exists', expected=True)

            if not os.access(self.filename, os.R_OK):
                raise ClientError('Permissions Error', expected=True)

            if self._verify_file_hash():
                log.debug('Extracting Update')
                archive_ext = os.path.splitext(self.filename)[1].lower()

                if archive_ext == '.gz':
                    try:
                        with tarfile.open(self.filename, 'r:gz') as tfile:
                            # Extract file update to current
                            # directory.
                            tfile.extractall()
                    except Exception as err:  # pragma: no cover
                        log.debug(err, exc_info=True)
                        raise ClientError('Error reading gzip file',
                                          expected=True)
                elif archive_ext == '.zip':
                    try:
                        with zipfile.ZipFile(self.filename, 'r') as zfile:
                            # Extract update file to current
                            # directory.
                            zfile.extractall()
                    except Exception as err:  # pragma: no cover
                        log.debug(err, exc_info=True)
                        raise ClientError('Error reading zip file',
                                          expected=True)
                else:
                    raise ClientError('Unknown filetype')
            else:
                raise ClientError('Update archive is corrupt')

    def _get_file_hash_from_manifest(self):
        hash_key = '{}*{}*{}*{}*{}'.format(self._updates_key,
                                           self.name, self.latest,
                                           self.platform, 'file_hash')
        return self.easy_data.get(hash_key)

    # Must be called from directory where file is located
    def _verify_file_hash(self):
        if not os.path.exists(self.filename):
            log.debug('File does not exist')
            return False

        file_hash = self._get_file_hash_from_manifest()
        try:
            with open(self.filename, 'rb') as f:
                data = f.read()
        except Exception as err:
            log.debug(err, exc_info=True)
            return False

        if file_hash == get_hash(data):
            return True
        else:
            return False

    # Checks if latest update is already downloaded
    def _is_downloaded(self):
        # Comparing file hashes to ensure security
        with ChDir(self.update_folder):
            verified = self._verify_file_hash()

        return verified

    # Handles patch updates
    def _patch_update(self):  # pragma: no cover
        log.debug('Starting patch update')
        # The current version is not in the version manifest
        if self._current_archive_name is None:
            return False

        # Just checking to see if the zip for the current version is
        # available to patch If not we'll fall back to a full binary download
        if not os.path.exists(os.path.join(self.update_folder,
                                           self._current_archive_name)):
            log.debug('%s got deleted. No base binary to start patching '
                      'form', self._current_archive_name)
            return False

        # Initilize Patch object with all required information
        p = Patcher(current_version=self.current_version,
                    latest_version=self.latest,
                    update_folder=self.update_folder,
                    **self.init_data)

        # Returns True if everything went well
        # If False, fall back to a full update
        return p.start()

    def _full_update(self):
        log.debug('Starting full update')
        file_hash = self._get_file_hash_from_manifest()

        with ChDir(self.update_folder):
            log.debug('Downloading update...')
            fd = FileDownloader(self.filename, self.update_urls,
                                hexdigest=file_hash, verify=self.verify,
                                progress_hooks=self.progress_hooks,
                                max_download_retries=self.max_download_retries,
                                urllb3_headers=self.urllib3_headers)
            result = fd.download_verify_write()
            if result:
                log.debug('Download Complete')
                return True
            else:  # pragma: no cover
                log.debug('Failed To Download Latest Version')
                return False

    def cleanup(self):
        """Cleans up old update archives for this app or asset"""
        log.debug('Beginning removal of old updates')
        rpv = remove_previous_versions
        t = threading.Thread(target=rpv, args=(self.update_folder,
                                               self._current_archive_name))
        t.start()


class AppUpdate(LibUpdate):
    """Used to update an application. This object is returned by
    pyupdater.client.Client.update_check

    Args:

        data (dict): Info dict
    """

    def __init__(self, data):
        self._is_win = get_system() == 'win'
        super(AppUpdate, self).__init__(data)

    def extract_restart(self):
        """Will extract the update, overwrite the current binary,
        then restart the application using the updated binary."""
        try:
            self._extract_update()

            if self._is_win:
                self._win_overwrite_restart()
            else:
                self._overwrite()
                self._restart()
        except ClientError as err:
            log.debug(err, exc_info=True)

    def extract_overwrite(self):
        """Will extract the update then overwrite the current binary"""
        try:
            self._extract_update()
            if self._is_win:
                self._win_overwrite()
            else:
                self._overwrite()
        except ClientError as err:
            log.debug(err, exc_info=True)

    # ToDo: Remove in v3.0
    def win_extract_overwrite(self):
        """Overwrite current binary with update binary on windows.

        Deprecated: Use extract_overwrite instead.
        """
        self._win_overwrite()
    # End ToDo

    # ToDo: Remove in v3.0
    def restart(self):  # pragma: no cover
        """Will overwrite old binary with updated binary and
        restart the application using the updated binary.
        Not supported on windows.

        Deprecated: Used extract_restart instead.
        """
        # On windows we write a batch file to move the update
        # binary to the correct location and restart app.
        if get_system() == 'win':
            log.debug('Only supported on Unix like systems')
            return
        try:
            self._overwrite()
            self._restart()
        except ClientError as err:
            log.debug(err, exc_info=True)
    # End ToDo

    def _overwrite(self):
        # Unix: Overwrites the running applications binary
        if get_system() == 'mac':
            if self._current_app_dir.endswith('MacOS') is True:
                log.debug('Looks like we\'re dealing with a Mac Gui')
                temp_dir = get_mac_dot_app_dir(self._current_app_dir)
                self._current_app_dir = temp_dir

        app_update = os.path.join(self.update_folder, self.name)

        # Must be dealing with Mac .app application
        if not os.path.exists(app_update) and sys.platform == "darwin":
            app_update += '.app'

        log.debug('Update Location:\n%s', os.path.dirname(app_update))
        log.debug('Update Name: %s', os.path.basename(app_update))

        current_app = os.path.join(self._current_app_dir, self.name)

        # Must be dealing with Mac .app application
        if not os.path.exists(current_app):
            current_app += '.app'

        log.debug('Current App location:\n\n%s', current_app)

        # Remove current app to prevent errors when moving
        # update to new location
        # if update_app is a directory, then we are updating a directory
        if os.path.isdir(app_update):
            if (os.path.isdir(current_app)):
                shutil.rmtree(current_app)
            else:
                shutil.rmtree(os.path.dirname(current_app))

        if os.path.exists(current_app):
            remove_any(current_app)

        log.debug('Moving app to new location:\n\n%s', self._current_app_dir)
        shutil.move(app_update, self._current_app_dir)

    def _restart(self):
        log.debug('Restarting')
        current_app = os.path.join(self._current_app_dir, self.name)
        if get_system() == 'mac':
            # Must be dealing with Mac .app application
            if not os.path.exists(current_app):
                log.debug('Must be a .app bundle')
                current_app += '.app'
                mac_app_binary_dir = os.path.join(current_app, 'Contents',
                                                  'MacOS')
                _file = os.listdir(mac_app_binary_dir)

                # We are making an assumption here that only 1
                # executable will be in the MacOS folder.
                current_app = os.path.join(mac_app_binary_dir, sys.executable)

        r = Restarter(current_app, name=self.name)
        r.process()

    def _win_overwrite(self):
        # Windows: Moves update to current directory of running
        #                 application then restarts application using
        #                 new update.
        exe_name = self.name + '.exe'
        current_app = os.path.join(self._current_app_dir, exe_name)
        updated_app = os.path.join(self.update_folder, exe_name)

        # detect if is a folder
        if (os.path.exists(os.path.join(self.update_folder, self.name))):
            current_app = self._current_app_dir
            updated_app = os.path.join(self.update_folder, self.name)

        update_info = dict(data_dir=self.data_dir, updated_app=updated_app,
                           name=self.name)
        r = Restarter(current_app, **update_info)
        r.process(win_restart=False)

    def _win_overwrite_restart(self):
        # Windows: Moves update to current directory of running
        #          application then restarts application using
        #          new update.

        exe_name = self.name + '.exe'
        current_app = os.path.join(self._current_app_dir, exe_name)
        updated_app = os.path.join(self.update_folder, exe_name)

        # detect if is a folder
        if (os.path.exists(os.path.join(self.update_folder, self.name))):
            current_app = self._current_app_dir
            updated_app = os.path.join(self.update_folder, self.name)

        update_info = dict(data_dir=self.data_dir, updated_app=updated_app,
                           name=self.name)
        r = Restarter(current_app, **update_info)
        r.process()
