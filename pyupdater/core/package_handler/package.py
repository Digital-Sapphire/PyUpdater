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
from typing import Optional

from dsdev_utils.paths import ChDir, remove_any
import packaging.version

from pyupdater.cli.options import VALID_CHANNELS
from pyupdater.utils import parse_archive_name
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
    except (UtilsError, packaging.version.InvalidVersion):
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
    def __init__(self, filename):
        if sys.version_info[1] == 5:
            filename = str(filename)

        self.name = None
        self.version: Optional[packaging.version.Version] = None
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

    @property
    def channel(self):
        """
        todo: this information is already contained in the Version object,
         so it may be clearer just to drop the whole channel attribute
        """
        channel_index = 2
        if self.version.is_prerelease:
            # alpha or beta
            channel_index = "ab".index(self.version.pre[0])
        return VALID_CHANNELS[channel_index]

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

        log.debug(f"Extracting update archive info for: {package_basename}")
        parts = parse_archive_name(package_basename)
        self.name = parts["app_name"]
        self.platform = parts["platform"]
        msg = None
        try:
            # parse PEP440 version string
            self.version = packaging.version.Version(parts["version"])
            log.debug("Got version info")
        except TypeError:
            msg = "Package filename does not match expected format"
        except packaging.version.InvalidVersion:
            msg = "Package version may not be PEP440 compliant"
        finally:
            if msg is not None:
                reason = f"{msg}: {package_basename}"
                self.info["reason"] = reason
                log.error(reason)
                return

        self.info["status"] = True
        log.debug("Info extraction complete")
