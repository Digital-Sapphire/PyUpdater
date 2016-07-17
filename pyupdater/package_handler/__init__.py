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
from __future__ import print_function
from __future__ import unicode_literals

import json
import logging
import multiprocessing
import os
import shutil
import sys

try:  # pragma: no cover
    import bsdiff4
except ImportError:  # pragma: no cover
    bsdiff4 = None
from jms_utils.crypto import get_package_hashes as gph
from jms_utils.helpers import EasyAccessDict

from pyupdater import settings
from pyupdater.package_handler.package import (remove_previous_versions,
                                               Package,
                                               Patch)
from pyupdater.utils import (get_size_in_bytes as in_bytes,
                             lazy_import,
                             remove_dot_files
                             )
from pyupdater.utils.exceptions import PackageHandlerError
from pyupdater.utils.storage import Storage

log = logging.getLogger(__name__)


@lazy_import
def jms_utils():
    import jms_utils
    import jms_utils.paths
    return jms_utils


class PackageHandler(object):
    """Handles finding, sorting, getting meta-data, moving packages.

    Kwargs:

        app (instance): Config object
    """

    data_dir = None

    def __init__(self, config=None):
        self.config_loaded = False
        self.db = Storage()
        if config is not None:
            self.init_app(config)

    def init_app(self, obj):
        """Sets up client with config values from obj

        Args:

            obj (instance): config object

        """
        self.patches = obj.get('UPDATE_PATCHES', True)
        if self.patches:
            log.debug('Patch support enabled')
            self.patch_support = True
        else:
            log.info('Patch support disabled')
            self.patch_support = False
        data_dir = os.getcwd()
        self.data_dir = os.path.join(data_dir, settings.USER_DATA_FOLDER)
        self.files_dir = os.path.join(self.data_dir, 'files')
        self.deploy_dir = os.path.join(self.data_dir, 'deploy')
        self.new_dir = os.path.join(self.data_dir, 'new')
        self.config_dir = os.path.join(os.path.dirname(self.data_dir),
                                       settings.CONFIG_DATA_FOLDER)
        self.config = None
        self.json_data = None

        self.setup()

    def setup(self):
        "Creates working directories & loads json files."
        if self.data_dir is not None:
            self._setup()

    def _setup(self):
        self._setup_work_dirs()
        if self.config_loaded is False:
            self.json_data = self._load_version_file()
            self.config = self._load_config()
            self.config_loaded = True

    def process_packages(self, report_errors=False):
        """Gets a list of updates to process.  Adds the name of an
        update to the version file if not already present.  Processes
        all packages.  Updates the version file meta-data. Then writes
        version file back to disk.
        """
        if self.data_dir is None:
            raise PackageHandlerError('Must init first.', expected=True)
        # Getting a list of meta data from all packages in the
        # pyu-data/new directory. Also create a patch manifest
        # to create patches.
        pkg_manifest, patch_manifest = self._get_package_list(report_errors)
        patches = self._make_patches(patch_manifest)
        self._cleanup(patch_manifest)
        pkg_manifest = self._add_patches_to_packages(pkg_manifest,
                                                         patches)
        self.json_data = self._update_version_file(self.json_data,
                                                   pkg_manifest)
        self._write_json_to_file(self.json_data)
        self._write_config_to_file(self.config)
        self._move_packages(pkg_manifest)

    def _setup_work_dirs(self):
        # Sets up work dirs on dev machine.  Creates the following folder
        #    - Data dir
        # Then inside the data folder it creates 3 more folders
        #    - New - for new updates that need to be signed
        #    - Deploy - All files ready to upload are placed here.
        #    - Files - All updates are placed here for future reference
        #
        # This is non destructive
        dirs = [self.data_dir, self.new_dir,
                self.deploy_dir, self.files_dir,
                self.config_dir]
        for d in dirs:
            if not os.path.exists(d):
                log.info('Creating dir: %s', d)
                os.mkdir(d)

    def _load_version_file(self):
        # If version file is found its loaded to memory
        # If no version file is found then one is created.
        json_data = self.db.load(settings.CONFIG_DB_KEY_VERSION_META)
        if json_data is None:  # pragma: no cover
            log.warning('Version file not found')
            json_data = {'updates': {}}
            log.info('Created new version file')
        return json_data

    def _load_config(self):
        # Loads config from db if exists.
        # If config doesn't exists create new one
        config = self.db.load(settings.CONFIG_DB_KEY_PY_REPO_CONFIG)
        if config is None:  # pragma: no cover
            log.info('Creating new config file')
            config = {
                'patches': {}
                }
        return config

    def _get_package_list(self, report_errors):
        # Adds compatible packages to internal package manifest
        # for futher processing
        # Process all packages in new folder and gets
        # url, hash and some outer info.
        log.info('Getting package list')
        # Clears manifest if sign updates runs more the once without
        # app being restarted
        package_manifest = []
        patch_manifest = []
        bad_packages = []
        with jms_utils.paths.ChDir(self.new_dir):
            # Getting a list of all files in the new dir
            packages = os.listdir(os.getcwd())
            for p in packages:
                # On package initialization we do the following
                # 1. Check for a supported archive
                # 2. get required info: version, platform, hash
                # If any check fails package.info['status'] will be False
                # You can query package.info['reason'] for the reason
                package = Package(p)
                if package.info['status'] is False:
                    # Package failed at something
                    # package.info['reason'] will tell why
                    bad_packages.append(package)
                    continue

                # Add package hash
                package.file_hash = gph(package.filename)
                package.file_size = in_bytes(package.filename)
                self.json_data = self._update_file_list(self.json_data,
                                                        package)

                package_manifest.append(package)
                self.config = self._add_package_to_config(package,
                                                          self.config)

                if self.patch_support:
                    # If channel is not stable skip patch creation
                    if package.channel != 'stable':
                        log.debug('Package %s not on stable channel: '
                                  'Skipping', p)
                        continue
                    # Will check if source file for patch exists
                    # if so will return the path and number of patch
                    # to create. If missing source file None returned
                    path = self._check_make_patch(self.json_data,
                                                  package.name,
                                                  package.platform,
                                                  )
                    if path is not None:
                        log.info('Found source file to create patch')
                        patch_name = package.name + '-' + package.platform
                        src_path = path[0]
                        patch_number = path[1]
                        patch_info = dict(src=src_path,
                                          dst=os.path.abspath(p),
                                          patch_name=os.path.join(self.new_dir,
                                                                  patch_name),
                                          patch_num=patch_number,
                                          package=package.filename)
                        # ready for patching
                        patch_manifest.append(patch_info)
                    else:
                        log.warning('No source file to patch from')

        # ToDo: Expose this & remove "pragma: no cover" once done
        if report_errors is True:  # pragma: no cover
            log.warning('Bad package & reason for being naughty:')
            for b in bad_packages:
                log.warning(b.name, b.info['reason'])
        # End ToDo

        return package_manifest, patch_manifest

    def _add_package_to_config(self, p, data):
        if 'package' not in data.keys():
            data['package'] = {}
            log.info('Initilizing config for packages')
        # First package with current name so add platform and version
        if p.name not in data['package'].keys():
            data['package'][p.name] = {p.platform: p.version}
            log.info('Adding new package to config')
        else:
            # Adding platform and version
            if p.platform not in data['package'][p.name].keys():
                data['package'][p.name][p.platform] = p.version
                log.info('Adding new arch to package-config: %s', p.platform)
            else:
                # Getting current version for platform
                value = data['package'][p.name][p.platform]
                # Updating version if applicable
                if p.version > value:
                    log.info('Adding new version to package-config')
                    data['package'][p.name][p.platform] = p.version
        return data

    def _cleanup(self, patch_manifest):
        # Remove old archives that were previously used to create patches
        if len(patch_manifest) < 1:
            return
        log.info('Cleaning up files directory')
        for p in patch_manifest:
            filename = os.path.basename(p['src'])
            directory = os.path.dirname(p['src'])
            remove_previous_versions(directory, filename)

    def _make_patches(self, patch_manifest):
        pool_output = []
        if len(patch_manifest) < 1:
            return pool_output
        log.info('Starting patch creation')
        if sys.platform != 'win32':
            try:
                cpu_count = multiprocessing.cpu_count() * 2
            except Exception as err:
                log.debug(err, exc_info=True)
                log.warning('Cannot get cpu count from os. Using default 2')
                cpu_count = 2

            pool = multiprocessing.Pool(processes=cpu_count)
            pool_output = pool.map(PackageHandler._make_patch,
                                                        patch_manifest)
        else:
            pool_output = []
            for p in patch_manifest:
                pool_output.append(PackageHandler._make_patch(p))
        return pool_output

    def _add_patches_to_packages(self, package_manifest, patches):
        if patches is not None and len(patches) >= 1:
            log.info('Adding patches to package list')
            for p in patches:
                # We'll skip if patch meta data is incomplete
                if hasattr(p, 'ready') is False:
                    continue
                if hasattr(p, 'ready') and p.ready is False:
                    continue
                for pm in package_manifest:
                    #
                    if p.dst_filename == pm.filename:
                        pm.patch_info['patch_name'] = \
                            os.path.basename(p.patch_name)
                        # Don't try to get hash on a ghost file
                        if not os.path.exists(p.patch_name):
                            p_name = ''
                            p_size = 0
                        else:
                            p_name = gph(p.patch_name)
                            p_size = in_bytes(p.patch_name)
                        pm.patch_info['patch_hash'] = p_name
                        pm.patch_info['patch_size'] = p_size
                        # No need to keep searching
                        # We have the info we need for this patch
                        break
                    else:
                        log.debug('No patch match found')
        else:
            if self.patch_support is True:
                log.warning('No patches found')
        return package_manifest

    def _update_file_list(self, json_data, package_info):
        files = json_data[settings.UPDATES_KEY]
        latest = json_data.get('latest')
        if latest is None:
            json_data['latest'] = {}
        filename = files.get(package_info.name)
        if filename is None:
            log.debug('Adding %s to file list', package_info.name)
            json_data[settings.UPDATES_KEY][package_info.name] = {}

        latest_package = json_data['latest'].get(package_info.name)
        if latest_package is None:
            json_data['latest'][package_info.name] = {}

        latest_package = json_data['latest'][package_info.name]
        latest_channel = latest_package.get(package_info.channel)
        if latest_channel is None:
            json_data['latest'][package_info.name][package_info.channel] = {}
        return json_data

    def _manifest_to_version_file_compat(self,  package_info):
        # Checking for patch info. Patch info maybe be none
        patch_name = package_info.patch_info.get('patch_name')
        patch_hash = package_info.patch_info.get('patch_hash')
        patch_size = package_info.patch_info.get('patch_size')

        # Converting info to format compatible for version file
        info = {'file_hash': package_info.file_hash,
                    'file_size': package_info.file_size,
                    'filename': package_info.filename}

        # Adding patch info if available
        if patch_name and patch_hash:
            info['patch_name'] = patch_name
            info['patch_hash'] = patch_hash
            info['patch_size'] = patch_size

        return info

    def _update_version_file(self, json_data, package_manifest):
        # Adding version metadata from scanned packages to our
        # version manifest
        log.info('Adding package meta-data to version manifest')
        easy_dict = EasyAccessDict(json_data)
        for p in package_manifest:
            info = self._manifest_to_version_file_compat(p)

            version_key = '{}*{}*{}'.format(settings.UPDATES_KEY,
                                            p.name, p.version)
            version = easy_dict.get(version_key)
            log.debug('Package Info: %s', version)

            # If we cannot get a version number this must be the first version
            # of its kind.
            if version is None:
                log.debug('Adding new version to file')

                # First version with this package name
                json_data[settings.UPDATES_KEY][p.name][p.version] = {}
                platform_key = '{}*{}*{}*{}'.format(settings.UPDATES_KEY,
                                                    p.name, p.version,
                                                    'platform')

                platform = easy_dict.get(platform_key)
                if platform is None:
                    _name = json_data[settings.UPDATES_KEY][p.name]
                    _name[p.version][p.platform] = info

            else:
                # package already present, adding another version to it
                log.debug('Appending info data to version file')
                _updates = json_data[settings.UPDATES_KEY]
                _updates[p.name][p.version][p.platform] = info

            # Add each package to latests section separated by release channel
            json_data['latest'][p.name][p.channel][p.platform] = p.version
        return json_data

    def _write_json_to_file(self, json_data):
        # Writes json data to disk
        log.debug('Saving version meta-data')
        self.db.save(settings.CONFIG_DB_KEY_VERSION_META, json_data)

    def _write_config_to_file(self, json_data):
        log.debug('Saving config data')
        self.db.save(settings.CONFIG_DB_KEY_PY_REPO_CONFIG, json_data)

    def _move_packages(self, package_manifest):
        if len(package_manifest) < 1:
            return
        log.info('Moving packages to deploy folder')
        for p in package_manifest:
            patch = p.patch_info.get('patch_name')
            with jms_utils.paths.ChDir(self.new_dir):
                if patch:
                    if os.path.exists(os.path.join(self.deploy_dir, patch)):
                        os.remove(os.path.join(self.deploy_dir, patch))
                    log.debug('Moving %s to %s', patch, self.deploy_dir)
                    if os.path.exists(patch):
                        shutil.move(patch, self.deploy_dir)

                shutil.copy(p.filename, self.deploy_dir)
                log.debug('Copying %s to %s', p.filename, self.deploy_dir)

                if os.path.exists(os.path.join(self.files_dir, p.filename)):
                    os.remove(os.path.join(self.files_dir, p.filename))
                shutil.move(p.filename, self.files_dir)
                log.debug('Moving %s to %s', p.filename, self.files_dir)

    def _check_make_patch(self, json_data, name, platform):
        # Check to see if previous version is available to
        # make patch updates. Also calculates patch number
        log.debug(json.dumps(json_data['latest'], indent=2))
        log.info('Checking if patch creation is possible')
        if bsdiff4 is None:
            log.warning('Bsdiff is missing. Cannot create patches')
            return None
        src_file_path = None
        if os.path.exists(self.files_dir):
            with jms_utils.paths.ChDir(self.files_dir):
                files = os.listdir(os.getcwd())
                log.debug('Found %s files in files dir', len(files))

            files = remove_dot_files(files)
            # No src files to patch from. Exit quickly
            if len(files) == 0:
                log.debug('No src file to patch from')
                return None
            # If latest not available in version file. Exit
            try:
                log.debug('Looking for %s on %s', name, platform)
                latest = json_data['latest'][name]['stable'][platform]
                log.debug('Found latest version for patches')
            except KeyError:
                log.debug('Cannot find latest version in version meta')
                return None
            try:
                latest_platform = json_data[settings.UPDATES_KEY][name][latest]
                log.debug('Found latest platform for patches')
                try:
                    filename = latest_platform[platform]['filename']
                    log.debug('Found filename for patches')
                except KeyError:
                    log.error('Found old version file. Please read '
                              'the upgrade section in the docs.')
                    log.debug('Found old verison file')
                    return None
            except Exception as err:
                log.debug(err, exc_info=True)
                return None
            log.debug('Generating src file path')
            src_file_path = os.path.join(self.files_dir, filename)

            try:
                patch_num = self.config['patches'][name]
                log.debug('Found patch number')
                self.config['patches'][name] += 1
            except KeyError:
                log.debug('Cannot find patch number')
                # If no patch number we will start at 1
                patch_num = 1
                if 'patches' not in self.config.keys():
                    log.debug('Adding patches to version meta')
                    self.config['patches'] = {}
                if name not in self.config['patches'].keys():
                    log.debug('Adding %s to patches version meta', name)
                    self.config['patches'][name] = patch_num + 1
            num = patch_num + 1
            log.debug('Patch Number: %s', num)
            return src_file_path, num
        return None

    @staticmethod
    def _make_patch(patch_info):
        # Does with the name implies. Used with multiprocessing
        patch = Patch(patch_info)
        patch_name = patch_info['patch_name']
        dst_path = patch_info['dst']
        patch_number = patch_info['patch_num']
        src_path = patch_info['src']
        patch_name += '-' + str(patch_number)
        # Updating with full name - number included
        patch.patch_name = patch_name
        if not os.path.exists(src_path):
            log.warning('Src file does not exist to create patch')

        else:
            log.debug('Patch source path: %s', src_path)
            log.debug('Patch destination path: %s', dst_path)
            if patch.ready is True:
                log.info('Creating patch... %s', os.path.basename(patch_name))
                bsdiff4.file_diff(src_path, patch.dst_path, patch.patch_name)
                base_name = os.path.basename(patch_name)
                log.info('Done creating patch... %s', base_name)
            else:
                log.error('Missing patch attr')
        return patch
