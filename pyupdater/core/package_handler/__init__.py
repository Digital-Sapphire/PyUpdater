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
from __future__ import print_function, unicode_literals
import logging
import multiprocessing
import os
import shutil
import sys
from typing import Optional

from dsdev_utils.crypto import get_package_hashes as gph
from dsdev_utils.helpers import EasyAccessDict
from dsdev_utils.paths import ChDir

from pyupdater import settings
from pyupdater.utils import get_size_in_bytes as in_bytes
from pyupdater.utils.storage import Storage

from .package import remove_previous_versions, Package
from .patch import make_patch, Patch

log = logging.getLogger(__name__)


class PackageHandler(object):
    """Handles finding, sorting, getting meta-data, moving packages.

    Kwargs:

        patch_support (bool): whether or not to support patch updates
    """

    def __init__(self, patch_support: Optional[bool] = None):
        if patch_support is None:
            patch_support = False
        self.patch_support = patch_support

        # Version manifest
        self.version_data = None

        # Used to store config information
        self.db = Storage()

        # References the pyu-data folder in the root of repo
        self.data_dir = os.path.join(os.getcwd(), settings.USER_DATA_FOLDER)
        self.files_dir = os.path.join(self.data_dir, "files")
        self.deploy_dir = os.path.join(self.data_dir, "deploy")
        self.new_dir = os.path.join(self.data_dir, "new")
        self.config_dir = os.path.join(os.getcwd(), settings.CONFIG_DATA_FOLDER)

        self.setup()

    def setup(self):
        """Creates working directories & loads json files."""
        if self.data_dir is not None:
            # TODO: create all directories and files as part of the cli init
            #  command, do *not* create them automatically when instantiating
            #  a PackageHandler
            self._setup_work_dirs()
            self.version_data = self._load_version_data()

    def process_packages(self, report_errors=False):
        """Gets a list of updates to process.  Adds the name of an
        update to the version file if not already present.  Processes
        all packages.  Updates the version file meta-data. Then writes
        version file back to disk.
        """
        if self.patch_support:
            log.info("Patch support enabled")
        else:
            log.info("Patch support disabled")

        # Getting a list of meta data from all packages in the
        # pyu-data/new directory. Also create a patch manifest
        # to create patches.
        pkg_manifest, patch_manifest = self._get_package_list(report_errors)

        patches = PackageHandler._make_patches(patch_manifest)
        PackageHandler._cleanup(patch_manifest)
        PackageHandler._add_patches_to_packages(
            pkg_manifest, patches, self.patch_support
        )
        PackageHandler._update_version_meta(self.version_data, pkg_manifest)

        self._write_version_meta_to_file(self.version_data)
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
        dirs = [
            self.data_dir,
            self.new_dir,
            self.deploy_dir,
            self.files_dir,
            self.config_dir,
        ]
        for d in dirs:
            if not os.path.exists(d):
                log.info("Creating dir: %s", d)
                os.mkdir(d)

    def _load_version_data(self):
        # If version data is found in the config cache (i.e. config.pyu),
        # it is loaded into memory. If version data is not found, and empty
        # dict is created.
        version_data = self.db.load(settings.CONFIG_DB_KEY_VERSION_META)
        if version_data is None:  # pragma: no cover
            log.warning("Version data not found in config cache")
            version_data = {settings.UPDATES_KEY: {}}
            log.debug("Created new version file")
        return version_data

    def _get_package_list(self, report_errors):
        # Adds compatible packages to internal package manifest
        # for further processing
        # Process all packages in new folder and gets
        # url, hash and some outer info.
        log.info("Generating package list")
        # Clears manifest if sign updates runs more the once without
        # app being restarted
        package_manifest = []
        patch_manifest = []
        bad_packages = []
        with ChDir(self.new_dir):
            # Getting a list of all files in the new dir
            packages = os.listdir(os.getcwd())
            for p in packages:
                # On package initialization we do the following
                # 1. Check for a supported archive
                # 2. get required info: version, platform, hash
                # If any check fails new_pkg.info['status'] will be False
                # You can query new_pkg.info['reason'] for the reason
                new_pkg = Package(p)
                if new_pkg.info["status"] is False:
                    # Package failed at something
                    # new_pkg.info['reason'] will tell why
                    bad_packages.append(new_pkg)
                    continue

                # Add package hash
                new_pkg.file_hash = gph(new_pkg.filename)
                new_pkg.file_size = in_bytes(new_pkg.filename)

                # Add app name key to version_data if missing
                if new_pkg.name not in self.version_data[settings.UPDATES_KEY]:
                    self.version_data[settings.UPDATES_KEY][new_pkg.name] = {}

                package_manifest.append(new_pkg)

                if self.patch_support:
                    data = {
                        "filename": p,
                        "files_dir": self.files_dir,
                        "new_dir": self.new_dir,
                        "version_data": self.version_data,
                        "pkg_info": new_pkg,
                    }
                    _patch = Patch(**data)

                    if _patch.ok:
                        patch_manifest.append(_patch)

        if report_errors is True:  # pragma: no cover
            log.warning("Bad package & reason for being naughty:")
            for b in bad_packages:
                log.warning(b.name, b.info["reason"])

        return package_manifest, patch_manifest

    @staticmethod
    def _cleanup(patch_manifest):
        # Remove old archives that were previously used to create patches
        if len(patch_manifest) < 1:
            return
        log.info("Cleaning up stale files")
        for p in patch_manifest:
            remove_previous_versions(os.path.dirname(p.src), p.dst)

    @staticmethod
    def _make_patches(patch_manifest):
        pool_output = []
        if len(patch_manifest) < 1:
            return pool_output
        log.info("Starting patch creation")
        if sys.platform != "win32":
            try:
                cpu_count = multiprocessing.cpu_count() * 2
            except Exception as err:
                log.debug(err, exc_info=True)
                log.warning("Cannot get cpu count from os. Using default 2")
                cpu_count = 2

            pool = multiprocessing.Pool(processes=cpu_count)
            pool_output = pool.map(make_patch, patch_manifest)
        else:
            pool_output = []
            for p in patch_manifest:
                pool_output.append(make_patch(p))
        return pool_output

    @staticmethod
    def _add_patches_to_packages(package_manifest, patches, patch_support):
        if patches is not None and len(patches) >= 1:
            log.debug("Adding patches to package list")
            for p in patches:
                if not p.ok or not os.path.exists(p.patch_name):
                    continue

                log.debug("We have a good patch: %s", p)
                for pm in package_manifest:
                    if p.dst_filename == pm.filename:
                        pm.patch = p
                        pm.patch.hash = gph(pm.patch.patch_name)
                        pm.patch.size = in_bytes(pm.patch.patch_name)
                        break
                    else:
                        log.debug("No patch match found")
        else:
            if patch_support is True:
                log.debug("No patches found: %s", patches)

    @staticmethod
    def _manifest_to_version_file_compat(package_info):
        # Converting info to version file format
        info = {
            "file_hash": package_info.file_hash,
            "file_size": package_info.file_size,
            "filename": package_info.filename,
        }

        # Adding patch info if available
        if package_info.patch is not None:
            info["patch_name"] = package_info.patch.basename
            info["patch_hash"] = package_info.patch.hash
            info["patch_size"] = package_info.patch.size

        return info

    @staticmethod
    def _update_version_meta(version_data, package_manifest):
        # Adding version metadata from scanned packages to our version manifest
        log.info("Adding package meta-data to version manifest")
        easy_dict = EasyAccessDict(version_data)
        for p in package_manifest:
            info = PackageHandler._manifest_to_version_file_compat(p)

            version_key = p.version.pyu_format()
            easy_key = "{}*{}*{}".format(settings.UPDATES_KEY, p.name, version_key)
            existing_version = easy_dict.get(easy_key)
            log.debug("Package Info: %s", existing_version or "none")

            # If we cannot get a version number this must be the first version
            # of its kind.
            if existing_version is None:
                log.debug("Adding new version to file")

                # First version with this package name
                version_data[settings.UPDATES_KEY][p.name][version_key] = {}
                platform_key = "{}*{}*{}*{}".format(
                    settings.UPDATES_KEY, p.name, version_key, "platform"
                )

                platform = easy_dict.get(platform_key)
                if platform is None:
                    _name = version_data[settings.UPDATES_KEY][p.name]
                    _name[version_key][p.platform] = info

            else:
                # package already present, adding another version to it
                log.debug("Appending info data to version file")
                _updates = version_data[settings.UPDATES_KEY]
                _updates[p.name][version_key][p.platform] = info

        return version_data

    def _write_version_meta_to_file(self, version_data):
        # Writes json data to disk
        log.debug("Saving version meta-data")
        self.db.save(settings.CONFIG_DB_KEY_VERSION_META, version_data)

    def _move_packages(self, package_manifest):
        if len(package_manifest) < 1:
            return
        log.info("Moving packages to deploy folder")
        for p in package_manifest:
            with ChDir(self.new_dir):
                if p.patch is not None:
                    if os.path.exists(os.path.join(self.deploy_dir, p.patch.basename)):
                        os.remove(os.path.join(self.deploy_dir, p.patch.basename))
                    log.debug("Moving %s to %s", p.patch.basename, self.deploy_dir)
                    if os.path.exists(p.patch.basename):
                        shutil.move(p.patch.basename, self.deploy_dir)

                shutil.copy(p.filename, self.deploy_dir)
                log.debug("Copying %s to %s", p.filename, self.deploy_dir)

                if os.path.exists(os.path.join(self.files_dir, p.filename)):
                    os.remove(os.path.join(self.files_dir, p.filename))
                shutil.move(p.filename, self.files_dir)
                log.debug("Moving %s to %s", p.filename, self.files_dir)
