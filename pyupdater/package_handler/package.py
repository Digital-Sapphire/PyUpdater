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
import logging
import os
import re

from jms_utils.exceptions import VersionError
from jms_utils.helpers import Version
from jms_utils.paths import ChDir, remove_any

from pyupdater.utils import parse_platform
from pyupdater.utils.exceptions import UtilsError

log = logging.getLogger(__name__)


def cleanup_old_archives(filename=None, directory=None):
    if filename is None:
        log.debug('Cleanup Failed - Filename is None')
        return
    log.debug('Filename: %s', filename)

    if directory is None:
        log.debug('Cleanup Failed - Directory is None')
        return
    log.debug('Directory: %s', directory)

    try:
        current_version = Version(filename)
    except (UtilsError, VersionError):  # pragma: no cover
        log.warning('Cleanup Failed - Cannot parse version info.')
        return

    try:
        # We set the full path here because Package() checks if filename exists
        package_info = Package(os.path.join(directory, filename))
    except (UtilsError, VersionError):
        log.warning('Cleanup Failed - Cannot parse package info.')
        return

    if package_info.info['status'] is False:
        log.debug('Not an archive format: %s', package_info.name)
        return

    log.debug('Current version: %s', str(current_version))
    assert package_info.name is not None
    log.debug('Name to search for: %s', package_info.name)
    with ChDir(directory):
        temp = os.listdir(os.getcwd())
        for t in temp:
            log.debug('Checking: %s', t)
            # Only attempt to remove old files of the one we
            # are updating
            if package_info.name not in t:
                log.debug('File does not match name of current binary')
                continue
            else:
                log.debug('Found possible match')
                log.debug('Latest name: %s', package_info.name)
                log.debug('Old name: %s', t)

            try:
                old_version = Version(t)
            except (UtilsError, VersionError):  # pragma: no cover
                log.warning('Cannot parse version info')
                # Skip file since we can't parse
                continue
            log.debug('Found version: %s', str(old_version))

            if old_version < current_version:
                old_path = os.path.join(directory, t)
                log.info('Removing old update: %s', old_path)
                remove_any(old_path)
            else:
                log.debug('Old version: %s', old_version)
                log.debug('Current version: %s', current_version)


class Patch(object):
    """Holds information for patch file.

    Args:

        patch_info (dict): patch information
    """

    def __init__(self, patch_info):
        self.dst_path = patch_info.get('dst')
        self.patch_name = patch_info.get('patch_name')
        self.dst_filename = patch_info.get('package')
        self.ready = self._check_attrs()

    def _check_attrs(self):
        if self.dst_path is not None:
            # Cannot create patch if destination file is missing
            if not os.path.exists(self.dst_path):
                return False
        # Cannot create patch if destination file is missing
        else:
            return False
        # Cannot create patch if name is missing
        if self.patch_name is None:
            return False
        # Cannot create patch is destination filename is missing
        if self.dst_filename is None:
            return False
        return True


class Package(object):
    """Holds information of update file.

    Args:

        filename (str): name of update file
    """
    regex = re.compile('(?P<name>[\w\s]+)-[A-Za-z]+-[0-9]\.[0-9]')

    def __init__(self, filename):
        self.name = None
        self.version = None
        self.filename = filename
        self.file_hash = None
        self.file_size = None
        self.platform = None
        self.info = dict(status=False, reason='')
        self.patch_info = {}
        # seems to produce the best diffs.
        # Tests on homepage: https://github.com/JMSwag/PyUpdater
        # Zip doesn't keep +x permissions. Only using gz for now.
        self.supported_extensions = ['.zip', '.gz']
        # ToDo: May need to add more files to ignore
        self.ignored_files = ['.DS_Store', ]
        self.extract_info(filename)

    def extract_info(self, package):
        """Gets version number, platform & hash for package.

        Args:

            package (str): filename
        """
        if not os.path.exists(package):
            msg = '{} does not exists'.format(package)
            log.debug(msg)
            self.info['reason'] = msg
            return
        if package in self.ignored_files:
            msg = 'Ignored file: {}'.format(package)
            log.debug(msg)
            self.info['reason'] = msg
            return
        if os.path.splitext(package)[1].lower() not in \
                self.supported_extensions:
            msg = 'Not a supported archive format: {}'.format(package)
            self.info['reason'] = msg
            log.warning(msg)
            return

        log.info('Extracting update archive info for: %s', package)
        try:
            v = Version(package)
            self.channel = v.channel
            self.version = str(v)
        except (UtilsError, VersionError):
            msg = 'Package version not formatted correctly'
            self.info['reason'] = msg
            log.error(msg)
            return
        log.debug('Got version info')

        try:
            self.platform = parse_platform(package)
        except UtilsError:
            msg = 'Package platform not formatted correctly'
            self.info['reason'] = msg
            log.error(msg)
            return
        log.debug('Got platform info')

        self.name = self._parse_package_name(package)
        log.debug('Got name of update: %s', self.name)
        self.info['status'] = True
        log.info('Info extraction complete')

    def _parse_package_name(self, package):
        # Returns package name from update archive name
        # Changes appname-platform-version to appname
        # ToDo: May need to update regex if support for app names with
        #       hyphens in them are requested. Example "My-App"
        log.debug('Package name: %s', package)
        basename = os.path.basename(package)

        r = self.regex.search(basename)
        name = r.groupdict()['name']
        log.debug('Regex name: %s', name)
        return name
