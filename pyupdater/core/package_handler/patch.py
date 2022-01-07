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
import json
import logging
import os

try:  # pragma: no cover
    import bsdiff4
except ImportError:  # pragma: no cover
    bsdiff4 = None
from dsdev_utils.paths import ChDir

from pyupdater import settings
from pyupdater.utils import remove_dot_files, get_latest_version


log = logging.getLogger(__name__)


def make_patch(patch):
    log.debug("Patch source path: %s", patch.src)
    log.debug("Patch destination path: %s", patch.dst)
    log.info("Creating patch... %s", patch.basename)

    bsdiff4.file_diff(patch.src, patch.dst, patch.patch_name)

    log.info("Done creating patch... %s", patch.basename)

    return patch


class Patch(object):
    def __init__(self, **kwargs):
        self._pkg_info = kwargs.get("pkg_info")
        self._filename = kwargs.get("filename")
        self._files_dir = kwargs.get("files_dir")
        self._new_dir = kwargs.get("new_dir")
        self._version_data = kwargs.get("version_data")

        self.ok = False
        self.src = None
        self.dst = None
        self.patch_name = None
        self.basename = None
        self.hash = None
        self.size = None

        self._check_make_patch()

        if self.ok:
            self.dst = os.path.abspath(self._filename)
            # Patch filename should match archive filename, except for suffix
            # todo: use Path().with_suffix() when pathlib becomes available
            _patch_name = "{}-{}-{}{}".format(
                self._pkg_info.name,
                self._pkg_info.platform,
                self._pkg_info.version,
                settings.PATCH_SUFFIX,
            )
            self.patch_name = os.path.join(self._new_dir, _patch_name)
            self.basename = os.path.basename(self.patch_name)
            self.dst_filename = self._pkg_info.filename

    def __str__(self):
        tmpl = "Patch(ok={ok}, patch_name={patch_name}, basename={basename})"
        return tmpl.format(
            ok=self.ok, patch_name=self.patch_name, basename=self.basename
        )

    def _check_make_patch(self):
        """
        Check to see if archive file for the current latest version is
        available, as the basis for patch creation.
        """
        log.debug("Checking if patch creation is possible")
        if bsdiff4 is None:
            log.warning("Bsdiff is missing. Cannot create patches")
            return

        if os.path.exists(self._files_dir):
            with ChDir(self._files_dir):
                files = os.listdir(os.getcwd())
                log.debug("Found %s files in files dir", len(files))

            files = remove_dot_files(files)
            # No src files to patch from. Exit quickly
            if len(files) == 0:
                log.debug("No src file to patch from")
                return

            _name = self._pkg_info.name
            _plat = self._pkg_info.platform

            log.debug("Looking for %s on %s", _name, _plat)
            latest_version = get_latest_version(
                app_name=_name,
                platform=_plat,
                manifest=self._version_data,
                channel=None,  # all channels
            )
            if latest_version is None:
                log.debug("Cannot find latest version in version meta")
                return
            log.debug(f"Found latest version for patches: {latest_version}")
            try:
                u_key = settings.UPDATES_KEY
                version_key = latest_version.pyu_format()
                latest_platforms = self._version_data[u_key][_name][version_key]
                log.debug("Found latest platform for patches")
                try:
                    filename = latest_platforms[_plat]["filename"]
                    log.debug("Found filename for patches")
                except KeyError:
                    log.error("Could not find filename for patch creation.")
                    return
            except Exception as err:
                log.debug(err, exc_info=True)
                return

            log.debug("Generating src file path")
            self.src = os.path.join(self._files_dir, filename)
            log.debug("Source path: %s", self.src)
            if not os.path.exists(self.src):
                log.warning("Source path does not exist: %s", filename)
                return

            self.ok = True
