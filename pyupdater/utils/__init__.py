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
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import sys
try:
    from UserDict import DictMixin as dictmixin
except ImportError:
    from collections import MutableMapping as dictmixin

import certifi
from jms_utils.helpers import lazy_import, Version
from jms_utils.paths import remove_any
from stevedore.extension import ExtensionManager
import urllib3

from pyupdater import settings
from pyupdater.utils.exceptions import UtilsError

log = logging.getLogger(__name__)


@lazy_import
def bz2():
    import bz2
    return bz2


@lazy_import
def gzip():
    import gzip
    return gzip


@lazy_import
def hashlib():
    import hashlib
    return hashlib


@lazy_import
def io():
    import io
    return io


@lazy_import
def json():
    try:
        import simplejson as json
    except ImportError:
        import json
    return json


@lazy_import
def os():
    import os
    return os


@lazy_import
def re():
    import re
    return re


@lazy_import
def shutil():
    import shutil
    return shutil


@lazy_import
def subprocess():
    import subprocess
    return subprocess


@lazy_import
def tarfile():
    import tarfile
    return tarfile


@lazy_import
def time():
    import time
    return time


@lazy_import
def zipfile():
    import zipfile
    return zipfile


@lazy_import
def jms_utils():
    import jms_utils
    import jms_utils.system
    import jms_utils.terminal
    return jms_utils


@lazy_import
def six():
    import six
    import six.moves
    return six


class PluginManager(object):

    PLUGIN_NAMESPACE = 'pyupdater.plugins'

    def __init__(self, config):
        plugins_namespace = ExtensionManager(self.PLUGIN_NAMESPACE,
                                             invoke_on_load=True)
        plugins = []
        for p in plugins_namespace.extensions:
            plugins.append(p.obj)
        # Sorting by name then author
        plugins = sorted(plugins, key=lambda x: (x.name, x.author))

        # Used as a counter when creating names to plugin
        # User may have multiple plugins with the same
        # name installed
        self.unique_names = {}

        # A list of dicts of all installed plugins.
        # Keys: name author plugin
        self.plugins = []
        self.configs = self._get_config(config)
        self._load(plugins)

    # Created a function here since we are doing
    # this in two locations in this class
    def _get_config(self, config):
        return config.get('PLUGIN_CONFIGS')

    def _name_check(self, name):
        # We don't use the number 1 when adding the first
        # name in the case where there are only one name
        # it'll look better when displayed on the cli
        name = name.lower()
        if name not in self.unique_names.keys():
            self.unique_names[name] = ''

        # Create the output before we update the name count
        out = '{}{}'.format(name, str(self.unique_names[name]))

        # Setup the counter for the next exact name match
        # Since we already created the output up above
        # we are just getting ready for the next call
        # to name check
        if self.unique_names[name] == '':
            self.unique_names[name] = 2
        else:
            self.unique_names[name] += 1

        return out

    def _load(self, plugins):
        # p is the initialized plugin
        for p in plugins:
            # Checking for required information from
            # plugin author. If not found plugin won't be loaded
            if not hasattr(p, 'name') or p.name is None:
                log.error('Plugin does not have required name attribute')
                continue
            if not hasattr(p, 'author') or p.author is None:
                log.error('Plugin does not have required author attribute')
                continue

            if not isinstance(p.name, six.string_types):
                log.error('Plugin name attribute is not a string')
                continue
            if not isinstance(p.author, six.string_types):
                log.error('Plugin author attribute is not a string')
                continue
            # We are ensuring a unique name for users
            # to select when uploading.
            name = self._name_check(p.name)
            self.plugins.append({'name': name,
                                'author': p.author,
                                'plugin': p})

    def config_plugin(self, name, config):
        # Load all available plugin configs from
        # app_config['PLUGIN_CONFIGS']
        configs = self._get_config(config)
        # Get the requested plugin
        plugin = self.get_plugin(name)
        # Create the key to retrieve this plugins config
        config_key = '{}-{}'.format(plugin.name.lower(), plugin.author)
        # Get the config for this plugin
        plugin_config = configs.get(config_key)
        if plugin_config is None:
            plugin_config = {}
            configs[config_key] = plugin_config
        # Get the plugin its config dict for updating
        try:
            plugin.set_config(plugin_config)
        except Exception as err:
            log.error('There was an error during configuration '
                      'of %s crated by %s', plugin.name, plugin.author)
            log.error(err)
            log.debug(err, exc_info=True)

    def get_plugin_names(self):
        """Returns the name & author of all installed
        plugins
        """
        plugin_info = []
        for p in self.plugins:
            plugin_info.append({'name': p['name'],
                               'author': p['author']})
        return plugin_info

    # Init is false by default. Used when you want
    # to get a plugin without initialization
    def get_plugin(self, name, init=False):
        "Returns the named plugin"
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
        config_key = '{}-{}'.format(plugin.name.lower(),
                                    plugin.author)
        return self.configs.get(config_key, {})

    def _get_plugin(self, name):
        plugin = None
        name = name.lower()
        for p in self.plugins:
            # We match the given name to the names
            # we generate for uniqueness
            if name == p['name'].lower():
                plugin = p['plugin']
                break
        return plugin


def print_plugin_settings(plugin_name, config):
    pm = PluginManager(config)
    config = pm.get_plugin_settings(plugin_name)
    if len(config.keys()) == 0:
        print('No config found for {}'.format(plugin_name))
    else:
        print(plugin_name)
        print(config)


def get_http_pool(secure=True):
    if secure is True:
        return urllib3.PoolManager(cert_reqs=str('CERT_REQUIRED'),
                                   ca_certs=certifi.where())
    else:
        return urllib3.PoolManager()


def check_repo():
    "Checks if current directory is a pyupdater repository"
    repo = True
    if not os.path.exists(settings.CONFIG_DATA_FOLDER):
        log.debug('PyUpdater config data folder is missing')
        repo = False
    return repo


def get_filename(name, version, platform, easy_data):
    """Gets full filename for given name & version combo

    Args:

        name (str): name of file to get full filename for

       version (str): version of file to get full filename for

       easy_data (dict): data file to search

    Returns:

       (str) Filename with extension
    """
    filename_key = '{}*{}*{}*{}*{}'.format(settings.UPDATES_KEY, name,
                                           version, platform, 'filename')
    filename = easy_data.get(filename_key)

    log.debug("Filename for %s-%s: %s", name, version, filename)
    return filename


def get_hash(data):
    """Get hash of object

    Args:

        data (object): Object you want hash of.

    Returns:

        (str): sha256 hash
    """
    if six.PY3:
        if not isinstance(data, bytes):
            data = bytes(data, 'utf-8')
    hash_ = hashlib.sha256(data).hexdigest()
    log.debug('Hash for binary data: %s', hash_)
    return hash_


def get_highest_version(name, plat, channel, easy_data):
    """Parses version file and returns the highest version number.

    Args:

       name (str): name of file to search for updates

       easy_data (dict): data file to search

    Returns:

       (str) Highest version number
    """
    version_key_alpha = '{}*{}*{}*{}'.format('latest', name, 'alpha', plat)
    version_key_beta = '{}*{}*{}*{}'.format('latest', name, 'beta', plat)
    version_key_stable = '{}*{}*{}*{}'.format('latest', name, 'stable', plat)
    version = None

    alpha = easy_data.get(version_key_alpha)
    if alpha is None:
        alpha = '0.0'

    beta = easy_data.get(version_key_beta)
    if beta is None:
        beta = '0.0'

    stable = easy_data.get(version_key_stable)

    if alpha is not None and channel == 'alpha':
        version = alpha
        if Version(version) < Version(stable):
            version = stable
        if Version(version) < Version(beta):
            version = beta

    if beta is not None and channel == 'beta':
        version = beta
        if Version(version) < Version(stable):
            version = stable

    if stable is not None and channel == 'stable':
        version = stable

    if version is not None:
        log.debug('Highest version: %s', version)
    else:
        log.error('No updates for "%s" on %s exists', name, plat)

    return version


def get_size_in_bytes(filename):
    size = os.path.getsize(os.path.abspath(filename))
    log.debug('File size: %s bytes', size)
    return size


def setup_appname(config):  # pragma: no cover
    if config.APP_NAME is not None:
        default = config.APP_NAME
    else:
        default = None
    config.APP_NAME = jms_utils.terminal.get_correct_answer('Please enter '
                                                            'app name',
                                                            required=True,
                                                            default=default)


def setup_company(config):  # pragma: no cover
    if config.COMPANY_NAME is not None:
        default = config.COMPANY_NAME
    else:
        default = None
    temp = jms_utils.terminal.get_correct_answer('Please enter your comp'
                                                 'any or name',
                                                 required=True,
                                                 default=default)
    config.COMPANY_NAME = temp


def setup_client_config_path(config): # pragma: no cover
    _default_dir = os.path.basename(os.path.abspath(os.getcwd()))
    question = ("Please enter the path to where pyupdater "
                "will write the client_config.py file. "
                "You'll need to import this file to "
                "initialize the update process. \nExamples:\n\n"
                "lib/utils, src/lib, src. \n\nLeave blank to use "
                "the current directory")
    answer = jms_utils.terminal.get_correct_answer(question,
                                                   default=_default_dir)

    if answer == _default_dir:
        config.CLIENT_CONFIG_PATH = settings.DEFAULT_CLIENT_CONFIG
    else:
        answer = answer.split(os.sep)
        answer.append(settings.DEFAULT_CLIENT_CONFIG[0])

        config.CLIENT_CONFIG_PATH = answer


def setup_urls(config):  # pragma: no cover
    url = jms_utils.terminal.get_correct_answer('Enter a url to ping for '
                                                'updates.', required=True)
    config.UPDATE_URLS = [url]
    while 1:
        answer = jms_utils.terminal.ask_yes_no('Would you like to add '
                                               'another url for backup?',
                                               default='no')
        if answer is True:
            url = jms_utils.terminal.get_correct_answer('Enter another url.',
                                                        required=True)
            config.UPDATE_URLS.append(url)
        else:
            break


def setup_patches(config):  # pragma: no cover
    config.UPDATE_PATCHES = jms_utils.terminal.ask_yes_no('Would you like to '
                                                          'enable patch upda'
                                                          'tes?',
                                                          default='yes')

def setup_plugin(name, config):
    pgm = PluginManager(config)
    plugin = pgm.get_plugin(name)
    if plugin is None:
        sys.exit('Invalid plugin name...')

    pgm.config_plugin(name, config)


def setup_scp(config):  # pragma: no cover
    _temp = jms_utils.terminal.get_correct_answer('Enter remote dir',
                                                  required=True)
    config.SSH_REMOTE_DIR = _temp
    config.SSH_HOST = jms_utils.terminal.get_correct_answer('Enter host',
                                                            required=True)

    config.SSH_USERNAME = jms_utils.terminal.get_correct_answer('Enter '
                                                                'usernmae',
                                                                required=True)


def initial_setup(config):  # pragma: no cover
    setup_appname(config)
    setup_company(config)
    setup_urls(config)
    setup_patches(config)
    setup_client_config_path(config)
    return config


def make_archive(name, target, version, external=False):
    """Used to make archives of file or dir. Zip on windows and tar.gz
    on all other platforms

    Args:
        name - Name to rename binary.

        version - Version of app. Used to create archive filename

        target - Name of file to archive.

        external - True when archiving external binary otherwise false

    Returns:
         (str) - name of archive
    """
    file_dir = os.path.dirname(os.path.abspath(target))
    filename = '{}-{}-{}'.format(os.path.splitext(name)[0],
                                 jms_utils.system.get_system(), version)
    filename_path = os.path.join(file_dir, filename)

    log.debug('starting archive')
    # ToDo: Fix this stuff. This seems janky
    temp_file = name
    if external is False:
        ext = os.path.splitext(target)[1]
        temp_file = name + ext
    # Remove file if it exists. Found during testing...
    log.debug('Temp file: %s', temp_file)
    if os.path.exists(temp_file):
        remove_any(temp_file)

    if os.path.isfile(target):
        shutil.copy(target, temp_file)
    else:
        shutil.copytree(target, temp_file)
    # End ToDo: End of janky

    # Only use zip on windows.
    # Zip doens't preserve file permissions on nix & mac
    # tar.gz creates full file path
    if jms_utils.system.get_system() == 'win':
        ext = '.zip'
        with zipfile.ZipFile(filename_path + '.zip', 'w') as zf:
            zf.write(target, temp_file)
    else:
        ext = '.tar.gz'
        if os.path.isfile(target):
            with tarfile.open(filename_path + '.tar.gz', 'w:gz') as tar:
                tar.add(target, temp_file)
        else:
            shutil.make_archive(filename, 'gztar', file_dir, temp_file)

    if os.path.exists(temp_file):
        remove_any(temp_file)

    output_filename = filename + ext
    log.debug('Archive output filename: %s', output_filename)
    return output_filename


def parse_platform(name):
    """Parses platfrom name from given string

    Args:

        name (str): Name to be parsed

    Returns:

        (str): Platform name
    """
    try:
        re_str = '[mnw]{1}[ai]{1}[cnx]{1}[6]?[4]?'
        platform_name = re.compile(re_str).findall(name)[0]
        log.debug('Platform name is: %s', platform_name)
    except IndexError:
        raise UtilsError('')

    return platform_name


def pretty_time(sec):
    """Turns seconds into a human readable format. Example: 2020/07/31 12:22:83

    Args:

        sec (int): seconds since unix epoch

    Returns:

        (str): Human readable time
    """
    return time.strftime("%Y/%m/%d, %H:%M:%S", time.localtime(sec))


def remove_dot_files(files):
    """Removes hidden dot files from file list

    Args:

        files (list): List of file names

    Returns:

        (list): List of filenames with ".example" files removed.
    """
    new_list = []
    for l in files:
        if not l.startswith('.'):
            new_list.append(l)
        else:
            log.debug('Removed %s from file list', l)
    return new_list


def run(cmd):
    """Logs a command before running it in subprocess.

    Args:

        cmd (str): command to be ran in subprocess

    Returns:

        (int): Exit code
    """
    log.debug('Command: %s', cmd)
    exit_code = subprocess.call(cmd, shell=True)
    return exit_code


# Used in debugging
def dict_to_str_sanatize(data):
    _data = data.copy()
    new_data = {}
    for k, v in _data.items():
        if hasattr(v, '__call__') is True:
            continue
        if k in ['__weakref__', '__module__', '__dict__', '__doc__']:
            continue
        new_data[k] = v
    return new_data


def _decode_offt(_bytes):
    """Decode an off_t value from a string.

    This decodes a signed integer into 8 bytes.  I'd prefer some sort of
    signed vint representation, but this is the format used by bsdiff4.
    """
    if sys.version_info[0] < 3:
        _bytes = map(ord, _bytes)
    x = _bytes[7] & 0x7F
    for b in xrange(6, -1, -1):
        x = x * 256 + _bytes[b]
    if _bytes[7] & 0x80:
        x = -x
    return x


class bsdiff4_py(object):
    """Pure-python version of bsdiff4 module that can only patch, not diff.

    By providing a pure-python fallback, we don't force frozen apps to
    bundle the bsdiff module in order to make use of patches.  Besides,
    the patch-applying algorithm is very simple.
    """
    @staticmethod
    def patch(source, patch):  # pragma: no cover
        #  Read the length headers
        l_bcontrol = _decode_offt(patch[8:16])
        l_bdiff = _decode_offt(patch[16:24])
        #  Read the three data blocks
        e_bcontrol = 32 + l_bcontrol
        e_bdiff = e_bcontrol + l_bdiff
        bcontrol = bz2.decompress(patch[32:e_bcontrol])
        bdiff = bz2.decompress(patch[e_bcontrol:e_bdiff])
        bextra = bz2.decompress(patch[e_bdiff:])
        #  Decode the control tuples
        tcontrol = []
        for i in xrange(0, len(bcontrol), 24):
            tcontrol.append((
                _decode_offt(bcontrol[i:i+8]),
                _decode_offt(bcontrol[i+8:i+16]),
                _decode_offt(bcontrol[i+16:i+24]),
            ))
        #  Actually do the patching.
        #  This is the bdiff4 patch algorithm in slow, pure python.
        source = six.BytesIO(source)
        result = six.BytesIO()
        bdiff = six.BytesIO(bdiff)
        bextra = six.BytesIO(bextra)
        for (x, y, z) in tcontrol:
            diff_data = bdiff.read(x)
            orig_data = source.read(x)
            if sys.version_info[0] < 3:
                for i in xrange(len(diff_data)):
                    result.write(chr((ord(diff_data[i]) +
                                 ord(orig_data[i])) % 256))
            else:
                for i in xrange(len(diff_data)):
                    result.write(bytes([(diff_data[i] + orig_data[i]) % 256]))
            result.write(bextra.read(y))
            source.seek(z, os.SEEK_CUR)
        return result.getvalue()


class JSONStore(dictmixin):

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
            with io.open(path, 'r', encoding='utf-8') as fp:
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

    def _sanatize(self, data):
        _data = {}
        for k, v in data.items():
            if hasattr(v, '__call__') is True:
                continue
            if isinstance(v, JSONStore) is True:
                continue
            if k in ['__weakref__', '__module__', '__dict__', '__doc__']:
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

        data = self._sanatize(self._data)
        with io.open(self.path, 'w', encoding='utf-8') as json_file:
            data = json.dumps(data, ensure_ascii=False, indent=2)
            if six.PY2:
                # unicode(data) auto-decodes data to unicode if str
                data = unicode(data)
            json_file.write(data)

        self._synced_json_kw = json_kw
        self._needs_sync = False
        return True


class Restarter(object):

    def __init__(self, current_app, **kwargs):
        self.current_app = current_app
        self.is_win = sys.platform == 'win32'
        self.data_dir = kwargs.get('data_dir')
        self.updated_app = kwargs.get('updated_app')
        log.debug('Current App: %s', self.current_app)
        if self.is_win is True:
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
        subprocess.Popen(self.current_app).wait()

    def _win_overwrite(self):
        bat_file = os.path.join(self.data_dir, 'update.bat')
        vbs_file = os.path.join(self.data_dir, 'invis.vbs')
        with io.open(bat_file, 'w', encoding='utf-8') as bat:
            bat.write("""
@echo off
echo Updating to latest version...
ping 127.0.0.1 -n 5 -w 1000 > NUL
move /Y "{}" "{}" > NUL
DEL invis.vbs
DEL "%~f0"
""".format(self.updated_app, self.current_app))
        with io.open(vbs_file, 'w', encoding='utf-8') as vbs:
            # http://www.howtogeek.com/131597/can-i-run-a-windows-batch-file-without-a-visible-command-prompt/
            vbs.write('CreateObject("Wscript.Shell").Run """" '
                      '& WScript.Arguments(0) & """", 0, False')
        log.info('Starting update batch file')
        # os.startfile(bat)
        args = ['wscript.exe', vbs_file, bat_file]
        subprocess.Popen(args)
        sys.exit(0)

    def _win_overwrite_restart(self):
        bat_file = os.path.join(self.data_dir, 'update.bat')
        vbs_file = os.path.join(self.data_dir, 'invis.vbs')
        with io.open(bat_file, 'w', encoding='utf-8') as bat:
            bat.write("""
@echo off
echo Updating to latest version...
ping 127.0.0.1 -n 5 -w 1000 > NUL
move /Y "{}" "{}" > NUL
echo restarting...
start "" "{}"
DEL invis.vbs
DEL "%~f0"
""".format(self.updated_app, self.current_app, self.current_app))
        with io.open(vbs_file, 'w', encoding='utf-8') as vbs:
            # http://www.howtogeek.com/131597/can-i-run-a-windows-batch-file-without-a-visible-command-prompt/
            vbs.write('CreateObject("Wscript.Shell").Run """" '
                      '& WScript.Arguments(0) & """", 0, False')
        log.info('Starting update batch file')
        # os.startfile(bat)
        args = ['wscript.exe', vbs_file, bat_file]
        subprocess.Popen(args)
        sys.exit(0)
