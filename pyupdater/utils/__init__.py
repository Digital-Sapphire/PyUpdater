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
from __future__ import absolute_import, unicode_literals
import io
import logging
import json
import os
import re
import shutil
import subprocess
import tarfile
from typing import Optional
import zipfile

from collections.abc import MutableMapping as DictMixin

import certifi
import packaging.version
from dsdev_utils import paths
from dsdev_utils import system
from stevedore.extension import ExtensionManager
import urllib3

from pyupdater import settings


log = logging.getLogger(__name__)


class PluginManager(object):

    PLUGIN_NAMESPACES = ["pyupdater.plugins.upload", "pyupdater.plugins"]

    def __init__(self, plugin_configs: Optional[dict] = None, plugins: Optional[list] = None):
        if plugin_configs is None:
            plugin_configs = {}

        _all_plugins = plugins
        if _all_plugins is None:
            _all_plugins = []
            for pn in self.PLUGIN_NAMESPACES:
                try:
                    namespace = ExtensionManager(pn, invoke_on_load=True)
                except Exception as err:
                    log.debug(err, exc_info=True)
                else:
                    for p in namespace.extensions:
                        _all_plugins.append(p.obj)

        # Sorting by name then author
        plugins = sorted(_all_plugins, key=lambda x: (x.name, x.author))

        # Used as a counter when creating names to plugin
        # User may have multiple plugins with the same
        # name installed
        self.unique_names = {}

        # A list of dicts of all installed plugins.
        # Keys: name author plugin
        self.plugins = []
        self.configs = plugin_configs
        self._load(plugins)

    def _name_check(self, name):
        # We don't use the number 1 when adding the first
        # name in the case where there are only one name
        # it'll look better when displayed on the cli
        name = name.lower()
        if name not in self.unique_names.keys():
            self.unique_names[name] = ""

        # Create the output before we update the name count
        out = "{}{}".format(name, str(self.unique_names[name]))

        # Setup the counter for the next exact name match
        # Since we already created the output up above
        # we are just getting ready for the next call
        # to name check
        if self.unique_names[name] == "":
            self.unique_names[name] = 2
        else:
            self.unique_names[name] += 1

        return out

    def _load(self, plugins):
        # p is the initialized plugin
        for p in plugins:
            # Checking for required information from
            # plugin author. If not found plugin won't be loaded
            if not hasattr(p, "name") or p.name is None:
                log.error("Plugin does not have required name attribute")
                continue
            if not hasattr(p, "author") or p.author is None:
                log.error("Plugin does not have required author attribute")
                continue

            if not isinstance(p.name, str):
                log.error("Plugin name attribute is not a string")
                continue
            if not isinstance(p.author, str):
                log.error("Plugin author attribute is not a string")
                continue
            # We are ensuring a unique name for users
            # to select when uploading.
            name = self._name_check(p.name)
            self.plugins.append({"name": name, "author": p.author, "plugin": p})

    def config_plugin(self, name, config):
        # Load all available plugin configs from
        # app_config['PLUGIN_CONFIGS']
        configs = self._get_config(config)

        # Get the requested plugin
        plugin = self.get_plugin(name)

        # Create the key to retrieve this plugins config
        config_key = "{}-{}".format(plugin.name.lower(), plugin.author)

        # Get the config for this plugin
        plugin_config = configs.get(config_key)
        if plugin_config is None:
            plugin_config = {}
            configs[config_key] = plugin_config

        # Give the plugin its config dict for updating
        try:
            plugin.set_config(plugin_config)
        except Exception as err:
            log.error(
                "There was an error during configuration " "of %s created by %s",
                plugin.name,
                plugin.author,
            )
            log.debug(err, exc_info=True)

    def get_plugin_names(self):
        """Returns the name & author of all installed
        plugins
        """
        plugin_info = []
        for p in self.plugins:
            plugin_info.append({"name": p["name"], "author": p["author"]})
        return plugin_info

    # Init is false by default. Used when you want
    # to get a plugin without initialization
    def get_plugin(self, name, init=False):
        """Returns the named plugin"""
        plugin = self._get_plugin(name)
        if plugin is not None and init is True:
            config = self._get_plugin_config(plugin)
            plugin.init_config(config)

        return plugin

    def get_plugin_settings(self, name):
        plugin = self._get_plugin(name)
        config = self._get_plugin_config(plugin)
        return config

    def _get_plugin_config(self, plugin):
        config_key = "{}-{}".format(plugin.name.lower(), plugin.author)
        return self.configs.get(config_key, {})

    def _get_plugin(self, name):
        plugin = None
        name = name.lower()
        for p in self.plugins:
            # We match the given name to the names
            # we generate for uniqueness
            if name == p["name"].lower():
                plugin = p["plugin"]
                break
        return plugin


def check_repo():
    """Checks if current directory is a pyupdater repository"""
    repo = True
    if not os.path.exists(settings.CONFIG_DATA_FOLDER):
        log.debug("PyUpdater config data folder is missing")
        repo = False
    return repo


def get_http_pool():
    return urllib3.PoolManager(cert_reqs=str("CERT_REQUIRED"), ca_certs=certifi.where())


def get_size_in_bytes(filename):
    size = os.path.getsize(os.path.abspath(filename))
    log.debug("File size: %s bytes", size)
    return size


def create_asset_archive(name, version: str):
    """Used to make archives of file or dir. Zip on windows and tar.gz
    on all other platforms

    Args:
        name - Name to rename binary.

        version - Version of app. Used to create archive filename

    Returns:
         (str) - name of archive
    """
    file_dir = os.path.dirname(os.path.abspath(name))
    filename = "{}-{}-{}".format(
        os.path.splitext(name)[0], system.get_system(), version
    )

    # Only use zip on windows.
    # Zip does not preserve file permissions on nix & mac
    with paths.ChDir(file_dir):
        if system.get_system() == "win":
            ext = ".zip"
            with zipfile.ZipFile(filename + ext, "w") as zf:
                zf.write(name, name)
        else:
            ext = ".tar.gz"
            with paths.ChDir(file_dir):
                with tarfile.open(filename + ext, "w:gz", compresslevel=0) as tar:
                    tar.add(name, name)

    output_filename = filename + ext
    log.debug("Archive output filename: %s", output_filename)
    return output_filename


def make_archive(name, target, app_version: str, archive_format):
    """Used to make archives of file or dir. Zip on windows and tar.gz
    on all other platforms

    Args:
        name - Name to rename binary.

        version - Version of app. Used to create archive filename

        target - Name of file to archive.

    Returns:
         (str) - name of archive
    """
    log.debug("starting archive")
    ext = os.path.splitext(target)[1]
    temp_file = name + ext
    log.debug("Temp file: %s", temp_file)
    # Remove file if it exists. Found during testing...
    if os.path.exists(temp_file):
        paths.remove_any(temp_file)

    if os.path.isfile(target):
        shutil.copy(target, temp_file)
    else:
        shutil.copytree(target, temp_file, symlinks=True)
        # renames the entry-point executable
        file_ext = ".exe" if system.get_system() == "win" else ""
        src_executable = temp_file + os.sep + target + file_ext
        dst_executable = temp_file + os.sep + name + file_ext
        # is an osx bundle app so does not need to fix the executable name
        if ext != ".app":
            shutil.move(src_executable, dst_executable)

        # is a win folder so the manifest need to be renamed too
        if system.get_system() == "win":
            src_manifest = src_executable + ".manifest"
            dst_manifest = dst_executable + ".manifest"
            try:
                shutil.move(src_manifest, dst_manifest)
            except FileNotFoundError:
                # pyinstaller 4.6+ embeds the manifest by default (issue #304)
                log.debug("Manifest not found. Assuming it is embedded.")

    file_dir = os.path.dirname(os.path.abspath(target))
    filename = "{}-{}-{}".format(
        os.path.splitext(name)[0], system.get_system(), app_version
    )
    # Only use zip on windows.
    # Zip does not preserve file permissions on nix & mac
    # tar.gz creates full file path
    with paths.ChDir(file_dir):
        ext = "gztar"
        if archive_format == "default":
            if system.get_system() == "win":
                ext = "zip"
        else:
            ext = archive_format
        output_filename = shutil.make_archive(filename, ext, file_dir, temp_file)

    if os.path.exists(temp_file):
        paths.remove_any(temp_file)

    log.debug("Archive output filename: %s", output_filename)
    return output_filename


def parse_archive_name(filename):
    """
    Parse a filename created by make_archive(), to extract app_name, platform,
    version, and extension strings.

    We do not impose any versioning requirements yet, such as defined in
    packaging.version.VERSION_PATTERN.

    todo: Mention that package.parse_platform has been removed,
     use parse_archive_name instead.
    """
    archive_name_pattern = (
        r"^(?P<app_name>[\w -]+)"
        r"-"
        r"(?P<platform>arm(64)?|mac|nix(64)?|win)"
        r"-"
        r"(?P<version>.+)"
        r"(?P<extension>\.zip|\.tar\.gz)$")
    match = re.search(pattern=archive_name_pattern, string=filename)
    return match.groupdict() if match else None


def remove_dot_files(files):
    """Removes hidden dot files from file list

    Args:

        files (list): List of file names

    Returns:

        (list): List of file names with ".example" files removed.
    """
    new_list = []
    for l in files:
        if not l.startswith("."):
            new_list.append(l)
        else:
            log.debug("Removed %s from file list", l)
    return new_list


def run(cmd):
    """Logs a command before running it in subprocess.

    Args:

        cmd (str): command to be ran in subprocess

    Returns:

        (int): Exit code
    """
    log.debug("Command: %s", cmd)
    exit_code = subprocess.call(cmd, shell=True)
    return exit_code


class JSONStore(DictMixin):
    def __init__(self, path, json_kw=None):
        """Create a JSONStore object backed by the file at `path`.
        If a dict is passed in as `json_kw`, it will be used as keyword
        arguments to the json module.
        """
        self.path = path
        self.json_kw = json_kw or {}

        self._data = {}

        self._synced_json_kw = None
        self._needs_sync = False

        if not os.path.exists(path):
            self.sync(force=True)  # write empty dict to disk
            return
        try:
            # load the whole store
            with io.open(path, "r", encoding="utf-8") as fp:
                self.update(json.load(fp))
        except Exception as err:
            log.warning(err)
            log.debug(err, exc_info=True)

    def __str__(self):
        return str(self._data)

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value
        self._needs_sync = True

    def __delitem__(self, key):
        del self._data[key]
        self._needs_sync = True

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        i = []
        for k, v in self._data.items():
            i.append((k, v))
        return iter(i)

    @staticmethod
    def _sanitize(data):
        _data = {}
        for k, v in data.items():
            if hasattr(v, "__call__") is True:
                continue
            if isinstance(v, JSONStore) is True:
                continue
            if k in ["__weakref__", "__module__", "__dict__", "__doc__"]:
                continue
            _data[k] = v
        return _data

    def copy(self):
        return self._data.copy()

    def keys(self):
        return self._data.keys()

    def sync(self, json_kw=None, force=False):
        """Atomically write the entire store to disk if it's changed.
        If a dict is passed in as `json_kw`, it will be used as keyword
        arguments to the json module.
        If force is set True, a new file will be written even if the store
        hasn't changed since last sync.
        """
        json_kw = json_kw or self.json_kw
        if self._synced_json_kw != json_kw:
            self._needs_sync = True

        if not (self._needs_sync or force):
            return False

        data = JSONStore._sanitize(self._data)
        with io.open(self.path, "w", encoding="utf-8") as json_file:
            data = json.dumps(data, ensure_ascii=False, indent=2)
            json_file.write(data)

        self._synced_json_kw = json_kw
        self._needs_sync = False
        return True


class PyuVersion(packaging.version.Version):
    """
    Shim for compatibility of packaging.version.Version (PEP440 format) and
    PyUpdater's internal version format, as used in existing version files.

    Basically, this is just a packaging.version.Version that knows how to:

    - interpret a pyupdater internal version string
    - present itself as a pyupdater internal version string

    This is only to ensure backward compatibility with existing version files.

    This replaces dsdev_utils.helpers.Version, which is currently broken.

    todo: Work towards deprecating the internal version format, so we don't
     need this shim anymore.
    """
    internal_version_pattern = r"(^\d+\.\d+\.\d+)\.([012])\.(\d+$)"
    pyu_channels = "ab"

    def __init__(self, version: str) -> None:
        """
        Convert PyUpdater's internal version format to a PEP440 compatible
        format so we can feed it into packaging.version.Version.
        """
        super().__init__(version=self.ensure_pep440_compat(version))

    @classmethod
    def ensure_pep440_compat(cls, version: str) -> str:
        """
        Convert a pyupdater internal version string to a PEP440-compatible
        version string that can be parsed by packaging.version.Version().

        The pyupdater internal version format is (from dsdev-utils):

            <major>.<minor>.<patch>.<release channel>.<release number>

        Note that the N.N.N.N.N format itself is supported by PEP440, and is
        parsed without errors by packaging.version.Version, but then it is
        always interpreted as a "final release" (i.e. a "stable" release in
        pyupdater terms).

        The canonical [PEP440 format][1] is defined as follows:

            [N!]N(.N)*[{a|b|rc}N][.postN][.devN]

        However, packaging.version.Version() is more forgiving, as it also
        handles e.g. '1.2.3.alpha.4'.

        Also see [packaging.version.VERSION_PATTERN][2].

        [1]: https://www.python.org/dev/peps/pep-0440/#public-version-identifiers
        [2]: https://github.com/pypa/packaging/blob/21.3/packaging/version.py#L225
        """
        re_obj = re.compile(cls.internal_version_pattern)
        match = re_obj.match(version)
        if match:
            channel = int(match.group(2))
            # Replace internal pre-release number by a PEP440 compatible value
            if channel < 2:
                version = re_obj.sub(
                    r"\1" + cls.pyu_channels[channel] + r"\3", version)
            elif channel == 2:
                # remove the ".2.0" from the internal version number
                version = re_obj.sub(r"\1", version)
        return version

    def pyu_format(self) -> str:
        """
        Return a version string in pyupdater internal version format.

        Rather than override __str__, we use a separate method for this,
        so that it is easy to recognize where the internal version format is
        actually used.
        """
        # The release tuple must have length 3 (major, minor, micro), even if
        # the version string is e.g. "1" or "1.2.3.4.5.6"
        release = (self.major, self.minor, self.micro)
        # Assume "stable" channel
        channel = (2, 0)
        if self.is_prerelease:
            channel = (self.pyu_channels.index(self.pre[0]), self.pre[1])
        return ".".join(str(value) for value in release + channel)


def get_latest_version(
    name: str, platform: str, channel: str, manifest: dict, strict: bool
) -> Optional[PyuVersion]:
    """
    Returns the latest version from the version manifest, for the specified
    release channel.

    Args:

         name (str): app name

         platform (str): the platform we are requesting for

         channel (str): the release channel

         manifest (dict): version manifest

         strict (bool): whether or not to take the channel into consideration

    Returns:

        latest_version (Version)
    """
    # obtain all versions from the "updates" object (disregard "latest" object)
    all_versions = [
        PyuVersion(key)
        for key, value in manifest[settings.UPDATES_KEY][name].items()
        if platform in value.keys()
    ]

    # collect eligible versions
    eligible_versions = all_versions
    if strict:
        # by default, only include final releases (a.k.a. "stable")
        eligible_versions = [v for v in all_versions if not v.is_prerelease]

        # add pre-releases if requested
        included = {"stable": [], "beta": ["b"], "alpha": ["b", "a"]}[channel]
        eligible_versions.extend(
            v for v in all_versions if v.is_prerelease and v.pre[0] in included
        )

    # get latest version from eligible versions
    latest_version = None
    if eligible_versions:
        latest_version = max(eligible_versions)
    log.debug(f"Latest version: {latest_version or 'not found'}")
    return latest_version
