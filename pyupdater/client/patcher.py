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
from __future__ import unicode_literals, print_function

import logging
import os

try:
    import bsdiff4
except ImportError:  # pragma: no cover
    bsdiff4 = None
from jms_utils.crypto import get_package_hashes
from jms_utils.helpers import EasyAccessDict, lazy_import, Version
from jms_utils.paths import remove_any

from pyupdater.client.downloader import FileDownloader
from pyupdater import settings
from pyupdater.utils.exceptions import PatcherError

if bsdiff4 is None:  # pragma: no cover
    from pyupdater.utils import bsdiff4_py as bsdiff4

log = logging.getLogger(__name__)


@lazy_import
def jms_utils():
    import jms_utils
    import jms_utils.paths
    import jms_utils.system
    return jms_utils


_platform = jms_utils.system.get_system()


class Patcher(object):
    """Downloads, verifies, and patches binaries

    Kwargs:

        name (str): Name of binary to patch

        json_data (dict): Info dict with all package meta data

        current_version (str): Version number of currently installed binary

        latest_version (str): Newest version available

        update_folder (str): Path to update folder to place updated binary in

        update_urls (list): List of urls to use for file download

        verify (bool) Meaning:

            True: Verify https connection

            False: Don't verify https connection
    """

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.json_data = kwargs.get('json_data')
        self.star_access_update_data = EasyAccessDict(self.json_data)
        self.current_version = Version(kwargs.get('current_version'))
        self.latest_version = kwargs.get('latest_version')
        self.update_folder = kwargs.get('update_folder')
        self.update_urls = kwargs.get('update_urls', [])
        self.verify = kwargs.get('verify', True)
        self.progress_hooks = kwargs.get('progress_hooks', [])
        self.patch_data = []
        self.patch_binary_data = []
        self.og_binary = None
        # ToDo: Update tests with linux archives.
        # Used for testing.
        self.platform = kwargs.get('platform', _platform)
        self.current_filename = kwargs.get('current_filename')
        self.current_file_hash = kwargs.get('current_file_hash')

        file_info = self._get_info(self.name, self.current_version,
                                   option='file')
        if self.current_filename is None:
            self.current_filename = file_info['filename']
        if self.current_file_hash is None:
            self.current_file_hash = file_info['file_hash']

    def start(self):
        "Starts patching process"

        log.debug('Starting patch updater...')
        # Check hash on installed binary to begin patching
        binary_check = self._verify_installed_binary()
        if not binary_check:
            log.error('Binary check failed...')
            return False
        # Getting all required patch meta-data
        all_patches = self._get_patch_info()
        if all_patches is False:
            log.error('Cannot find all patches...')
            return False

        # Download and verify patches in 1 go
        download_check = self._download_verify_patches()
        if download_check is False:
            log.error('Patch check failed...')
            return False

        try:
            self._apply_patches_in_memory()
        except PatcherError:
            log.error('Failed to apply patches in memory')
            return False
        else:
            try:
                self._write_update_to_disk()
            except PatcherError as err:
                log.error(err, exc_info=True)
                log.error('Failed to write patched binary to disk')
                return False
        # Looks like all is well
        return True

    def _verify_installed_binary(self):
        # Verifies latest downloaded archive against known hash
        log.debug('Checking for current installed binary to patch')

        with jms_utils.paths.ChDir(self.update_folder):
            if not os.path.exists(self.current_filename):
                log.debug('Cannot find archive to patch')
                return False

            installed_file_hash = get_package_hashes(self.current_filename)
            if self.current_file_hash != installed_file_hash:
                log.debug('Binary hash mismatch')
                return False
            # Read binary into memory to begin patching
            with open(self.current_filename, 'rb') as f:
                self.og_binary = f.read()
        log.debug('Binary found and verified')
        return True

    # We will take all versions.  Then append any version
    # thats greater then the current version to the list
    # of needed patches.
    def _get_patch_info(self):
        # Taking the list of needed patches and extracting the
        # patch data from it. If any loop fails, will return False
        # and start full binary update.
        log.debug('Getting patch meta-data')
        required_patches = self._get_required_patches(self.name)

        if len(required_patches) == 0:
            log.debug('No patches to process')
            return False

        # If we can't get the file size for all patches & the latest
        # full update we fall back to the old patch update limit of 4
        # We will only patch update if the total size of all needed
        # patches are less than the size of a full update
        fall_back = False
        total_patch_size = 0
        # Loop through all required patches and get file name, hash
        # and file size.
        for p in required_patches:
            info = {}
            platform_key = '{}*{}*{}*{}'.format(settings.UPDATES_KEY,
                                                self.name, str(p),
                                                self.platform)
            platform_info = self.star_access_update_data.get(platform_key)

            try:
                info['patch_name'] = platform_info['patch_name']
                info['patch_urls'] = self.update_urls
                info['patch_hash'] = platform_info['patch_hash']
                patch_size = platform_info.get('patch_size')
                if patch_size is None:
                    fall_back = True
                else:
                    try:
                        total_patch_size += int(patch_size)
                    except Exception as err:
                        log.debug(err, exc_info=True)
                        fall_back = True
                self.patch_data.append(info)
            except Exception as err:  # pragma: no cover
                log.debug(err, exc_info=True)
                log.error('Missing required patch meta-data')
                return False

        latest_info = self._get_info(self.name, self.latest_version,
                                     option='file')
        latest_file_size = latest_info.get('file_size')
        if latest_file_size is None:
            fall_back = True

        if fall_back is True:
            if len(required_patches) > 4:
                return False
            else:
                return True
        else:
            return self._calc_diff(total_patch_size, latest_file_size)

    def _calc_diff(self, patch_size, file_size):
        if patch_size < file_size:
            return True
        else:
            return False

    def _get_required_patches(self, name):
        # Gathers patch name, hash & URL
        needed_patches = []
        try:
            # Get list of Version objects initialized with keys
            # from update manifest
            version_key = '{}*{}'.format(settings.UPDATES_KEY, name)
            version_info = self.star_access_update_data(version_key)
            versions = map(Version, version_info.keys())
        except KeyError:  # pragma: no cover
            log.debug('No updates found in updates dict')
            # Will cause error to be thrown in _get_pacth_info
            # which will cause patch update to return False
            versions = [1]

        # Only stable packages have patch info
        versions = [v for v in versions if v.channel == 'stable']

        log.debug('Getting required patches')
        for i in versions:
            if i > self.current_version:
                needed_patches.append(i)

        # Used to guarantee patches are only added once
        needed_patches = list(set(needed_patches))

        # Ensuring we apply patches in correct order
        return sorted(needed_patches)

    def _download_verify_patches(self):
        # Downloads & verifies all patches
        log.debug('Downloading patches')
        downloaded = 0
        total = len(self.patch_data)
        for p in self.patch_data:
            # Initialize downloader
            fd = FileDownloader(p['patch_name'], p['patch_urls'],
                                hexdigest=p['patch_hash'], verify=self.verify)

            # Attempt to download resource
            data = fd.download_verify_return()
            if data is not None:
                self.patch_binary_data.append(data)
                downloaded += 1
                status = {'total': total,
                          'downloaed': downloaded,
                          'status': 'downloading'}
                self._call_progress_hooks(status)
            else:
                # Since patches are applied sequentially
                # we cannot continue successfully
                status = {'total': total,
                          'downloaded': downloaded,
                          'status': 'failed to download all patches'}
                self._call_progress_hooks(status)
                return False
        status = {'total': total,
                  'downloaed': downloaded,
                  'status': 'finished'}
        self._call_progress_hooks(status)
        return True

    def _call_progress_hooks(self, data):
        for ph in self.progress_hooks:
            try:
                ph(data)
            except Exception as err:
                log.debug(err, exc_info=True)
                log.error('Exception in callback: %s', ph.__name__)

    def _apply_patches_in_memory(self):
        # Applies a sequence of patches in memory
        log.debug('Applying patches')
        for i in self.patch_binary_data:
            try:
                self.og_binary = bsdiff4.patch(self.og_binary, i)
                log.debug('Applied patch successfully')
            except Exception as err:
                log.debug(err, exc_info=True)
                log.error(err)
                raise PatcherError('Patch failed to apply')

    def _write_update_to_disk(self):  # pragma: no cover
        # Writes updated binary to disk
        log.debug('Writing update to disk')
        filename_key = '{}*{}*{}*{}*{}'.format(settings.UPDATES_KEY,
                                               self.name,
                                               self.latest_version,
                                               self.platform,
                                               'filename')
        filename = self.star_access_update_data.get(filename_key)

        if filename is None:
            raise PatcherError('Filename missing in version file')

        with jms_utils.paths.ChDir(self.update_folder):
            try:
                with open(filename, 'wb') as f:
                    f.write(self.og_binary)
                log.debug('Wrote update file')
            except IOError:
                # Removes file if it got created
                if os.path.exists(filename):
                    remove_any(filename)
                log.error('Failed to open file for writing')
                raise PatcherError('Failed to open file for writing')
            else:
                file_info = self._get_info(self.name,
                                           self.latest_version, option='file')

                new_file_hash = file_info['file_hash']
                log.debug('checking file hash match')
                if new_file_hash != get_package_hashes(filename):
                    log.error('Version file hash: %s', new_file_hash)
                    log.error('Actual file hash: %s',
                              get_package_hashes(filename))
                    log.error('File hash does not match')
                    remove_any(filename)
                    raise PatcherError('Bad hash on patched file',
                                       expected=True)

    def _get_info(self, name, version, option='file'):
        if option == 'file':
            _name = 'filename'
            _hash = 'file_hash'
            _size = 'file_size'
        else:
            _name = 'patch_name'
            _hash = 'patch_hash'
            _size = 'patch_size'

        # Returns filename and hash for given name and version
        platform_key = '{}*{}*{}*{}'.format(settings.UPDATES_KEY, name,
                                            version, self.platform)
        platform_info = self.star_access_update_data.get(platform_key)

        info = {}
        if platform_info is not None:
            filename = platform_info.get(_name)
            log.debug('Current Info - Filename: %s', filename)

            file_hash = platform_info.get(_hash, '')
            log.debug('Current Info - File hash: %s', file_hash)

            file_size = platform_info.get(_size)
            log.debug('Current Info - File size: %s', file_size)
            _info = dict(filename=filename, file_hash=file_hash,
                         file_size=file_size)
            info.update(_info)
        return info
