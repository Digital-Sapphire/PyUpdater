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
import logging
import os
import re
import sys

from dsdev_utils.exceptions import VersionError
from dsdev_utils.helpers import Version
from dsdev_utils.paths import ChDir, remove_any

from pyupdater.utils.exceptions import PackageHandlerError, UtilsError

log = logging.getLogger(__name__)


def parse_platform(name):
    """Parses platfrom name from given string

    Args:

        name (str): Name to be parsed

    Returns:

        (str): Platform name
    """
    log.debug('Parsing "%s" for platform info', name)
    try:
        re_str = r"-(?P<platform>arm(64)?|mac|nix(64)?|win)-"
        data = re.compile(re_str).search(name)
        platform_name = data.groupdict()["platform"]
        log.debug("Platform name is: %s", platform_name)
    except AttributeError:
        raise PackageHandlerError("Could not parse platform from filename")

    return platform_name


def remove_previous_versions(directory, filename):
    """Removes previous version of named file"""
    log.debug("In remove_previous_versions")

    if filename is None:
        log.debug("Cleanup Failed - Filename is None")
        return
    log.debug("Filename: %s", filename)

    if directory is None:
        log.debug("Cleanup Failed - Directory is None")
        return
    log.debug("Directory: %s", directory)

    try:
        # We set the full path here because Package() checks if filename exists
        package_info = Package(os.path.join(directory, filename))
    except (UtilsError, VersionError):
        log.debug("Cleanup Failed: %s - Cannot parse package info.", filename)
        return

    if package_info.info["status"] is False:
        log.debug(
            "Not an archive format: %s - %s",
            package_info.name,
            package_info.info["reason"],
        )
        return

    log.debug("Current version: %s", package_info.version)
    assert package_info.name is not None
    log.debug("Name to search for: %s", package_info.name)
    with ChDir(directory):
        temp = os.listdir(os.getcwd())
        for t in temp:
            log.debug("Checking: %s", t)
            # Only attempt to remove old files of the one we
            # are updating
            temp_pkg = Package(t)
            if temp_pkg.info["status"] is False:
                continue

            if package_info.name != temp_pkg.name:
                log.debug("File does not match name of current binary")
                continue

            if package_info.channel != temp_pkg.channel:
                continue

            log.debug("Found possible match")
            log.debug("Latest name: %s", package_info.filename)
            log.debug("Old name: %s", temp_pkg.filename)

            if temp_pkg.version < package_info.version:
                old_path = os.path.join(directory, t)
                log.debug("Removing old update: %s", old_path)
                remove_any(old_path)
            else:
                log.debug("Old version: %s", temp_pkg.version)
                log.debug("Current version: %s", package_info.version)


class Package(object):
    """Holds information of update file.

    Args:

        filename (str): path to update file
    """

    # Used to parse name from archive filename
    name_regex = re.compile(r"(?P<name>[\w -]+)-[arm|mac|nix|win]")

    def __init__(self, filename):
        if sys.version_info[1] == 5:
            filename = str(filename)

        self.name = None
        self.channel = None
        self.version = None
        self.filename = os.path.basename(filename)
        self.file_hash = None
        self.file_size = None
        self.platform = None
        self.info = dict(status=False, reason="")
        self.patch = None
        # seems to produce the best diffs.
        # Tests on homepage: https://github.com/Digital-Sapphire/PyUpdater
        # Zip doesn't keep +x permissions. Only using gz for now.
        self.supported_extensions = [".zip", ".gz", ".bz2"]
        self.ignored_files = [".DS_Store"]
        self.extract_info(filename)

    def extract_info(self, package):
        """Gets version number, platform & hash for package.

        Args:

            package (str): filename
        """
        package_basename = os.path.basename(package)

        if not os.path.exists(package):
            msg = "{} does not exist".format(package)
            log.debug(msg)
            self.info["reason"] = msg
            return
        if package_basename in self.ignored_files:
            msg = "Ignored file: {}".format(package_basename)
            log.debug(msg)
            self.info["reason"] = msg
            return
        if (
            os.path.splitext(package_basename)[1].lower()
            not in self.supported_extensions
        ):
            msg = "Not a supported archive format: {}".format(package_basename)
            self.info["reason"] = msg
            log.debug(msg)
            return

        log.debug("Extracting update archive info for: %s", package_basename)
        try:
            v = Version(package_basename)
            self.channel = v.channel
            self.version = str(v)
        except VersionError:
            msg = "Package version not formatted correctly: {}"
            self.info["reason"] = msg.format(package_basename)
            log.error(msg)
            return
        log.debug("Got version info")

        try:
            self.platform = parse_platform(package_basename)
        except PackageHandlerError:
            msg = "Package platform not formatted correctly"
            self.info["reason"] = msg
            log.error(msg)
            return
        log.debug("Got platform info")

        self.name = self._parse_package_name(package_basename)
        assert self.name is not None
        log.debug("Got name of update: %s", self.name)
        self.info["status"] = True
        log.debug("Info extraction complete")

    def _parse_package_name(self, package):
        # Returns package name from update archive name
        # Changes appname-platform-version to appname
        #
        # May need to update regex if support for app names with
        # hyphens in them are requested. Example "My-App"
        log.debug("Package name: %s", package)
        basename = os.path.basename(package)

        r = self.name_regex.search(basename)
        try:
            name = r.groupdict()["name"]
        except Exception as err:
            self.info["reason"] = str(err)
            name = None

        log.debug("Regex name: %s", name)
        return name
