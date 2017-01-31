# --------------------------------------------------------------------------
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
# --------------------------------------------------------------------------
from __future__ import absolute_import
from __future__ import unicode_literals
import io
import logging
try:
    import simplejson as json
except ImportError:
    import json
import os
import shutil
import subprocess
import sys
import tarfile
import time
import zipfile
try:
    from UserDict import DictMixin as dictmixin
except ImportError:
    from collections import MutableMapping as dictmixin

from dsdev_utils import paths
from dsdev_utils import system
from dsdev_utils import terminal
import six
from stevedore.extension import ExtensionManager

from pyupdater import settings

log = logging.getLogger(__name__)


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
            self.plugins.append({'name': name, 'author': p.author,
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


def check_repo():
    "Checks if current directory is a pyupdater repository"
    repo = True
    if not os.path.exists(settings.CONFIG_DATA_FOLDER):
        log.debug('PyUpdater config data folder is missing')
        repo = False
    return repo


def get_size_in_bytes(filename):
    size = os.path.getsize(os.path.abspath(filename))
    log.debug('File size: %s bytes', size)
    return size


def setup_appname(config):  # pragma: no cover
    if config.APP_NAME is not None:
        default = config.APP_NAME
    else:
        default = None
    config.APP_NAME = terminal.get_correct_answer('Please enter '
                                                              'app name',
                                                              required=True,
                                                              default=default)


def setup_client_config_path(config):  # pragma: no cover
    _default_dir = os.path.basename(os.path.abspath(os.getcwd()))
    question = ("Please enter the path to where pyupdater "
                "will write the client_config.py file. "
                "You'll need to import this file to "
                "initialize the update process. \nExamples:\n\n"
                "lib/utils, src/lib, src. \n\nLeave blank to use "
                "the current directory")
    answer = terminal.get_correct_answer(question,
                                                     default=_default_dir)

    if answer == _default_dir:
        config.CLIENT_CONFIG_PATH = settings.DEFAULT_CLIENT_CONFIG
    else:
        answer = answer.split(os.sep)
        answer.append(settings.DEFAULT_CLIENT_CONFIG[0])

        config.CLIENT_CONFIG_PATH = answer


def setup_company(config):  # pragma: no cover
    if config.COMPANY_NAME is not None:
        default = config.COMPANY_NAME
    else:
        default = None
    temp = terminal.get_correct_answer('Please enter your comp'
                                                   'any or name',
                                                   required=True,
                                                   default=default)
    config.COMPANY_NAME = temp


def setup_max_download_retries(config):  # pragma: no cover
    default = config.MAX_DOWNLOAD_RETRIES
    while 1:
        temp = terminal.get_correct_answer('Enter max download '
                                                       'retries',
                                                       required=True,
                                                       default=default)
        try:
            temp = int(temp)
        except Exception as err:
            log.error(err)
            log.debug(err, exc_info=True)
            continue

        if temp > 10 or temp < 1:
            log.error('Max retries can only be from 1 to 10')
            continue

        break

    config.MAX_DOWNLOAD_RETRIES = temp


def setup_patches(config):  # pragma: no cover
    question = 'Would you like to enable patch updates?'
    config.UPDATE_PATCHES = terminal.ask_yes_no(question,
                                                            default='yes')


def setup_plugin(name, config):
    pgm = PluginManager(config)
    plugin = pgm.get_plugin(name)
    if plugin is None:
        sys.exit('Invalid plugin name...')

    pgm.config_plugin(name, config)


def setup_urls(config):  # pragma: no cover
    url = terminal.get_correct_answer('Enter a url to ping for '
                                                  'updates.', required=True)
    config.UPDATE_URLS = [url]
    while 1:
        answer = terminal.ask_yes_no('Would you like to add '
                                                 'another url for backup?',
                                                 default='no')
        if answer is True:
            url = terminal.get_correct_answer('Enter another url.',
                                                          required=True)
            config.UPDATE_URLS.append(url)
        else:
            break


def initial_setup(config):  # pragma: no cover
    setup_appname(config)
    setup_company(config)
    setup_urls(config)
    setup_patches(config)
    setup_client_config_path(config)
    return config


def create_asset_archive(name, version):
    """Used to make archives of file or dir. Zip on windows and tar.gz
    on all other platforms

    Args:
        name - Name to rename binary.

        version - Version of app. Used to create archive filename

    Returns:
         (str) - name of archive
    """
    file_dir = os.path.dirname(os.path.abspath(name))
    filename = '{}-{}-{}'.format(os.path.splitext(name)[0],
                                 system.get_system(), version)

    # Only use zip on windows.
    # Zip doens't preserve file permissions on nix & mac
    with paths.ChDir(file_dir):
        if system.get_system() == 'win':
            ext = '.zip'
            with zipfile.ZipFile(filename + ext, 'w') as zf:
                zf.write(name, name)
        else:
            ext = '.tar.gz'
            with paths.ChDir(file_dir):
                with tarfile.open(filename + ext, 'w:gz',
                                  compresslevel=0) as tar:
                    tar.add(name, name)

    output_filename = filename + ext
    log.debug('Archive output filename: %s', output_filename)
    return output_filename


def make_archive(name, target, version):
    """Used to make archives of file or dir. Zip on windows and tar.gz
    on all other platforms

    Args:
        name - Name to rename binary.

        version - Version of app. Used to create archive filename

        target - Name of file to archive.

    Returns:
         (str) - name of archive
    """
    log.debug('starting archive')
    ext = os.path.splitext(target)[1]
    temp_file = name + ext
    log.debug('Temp file: %s', temp_file)
    # Remove file if it exists. Found during testing...
    if os.path.exists(temp_file):
        paths.remove_any(temp_file)

    if os.path.isfile(target):
        shutil.copy(target, temp_file)
    else:
        shutil.copytree(target, temp_file)

    file_dir = os.path.dirname(os.path.abspath(target))
    filename = '{}-{}-{}'.format(os.path.splitext(name)[0],
                                 system.get_system(), version)

    # Only use zip on windows.
    # Zip doens't preserve file permissions on nix & mac
    # tar.gz creates full file path
    with paths.ChDir(file_dir):
        if system.get_system() == 'win':
            ext = '.zip'
            with zipfile.ZipFile(filename + ext, 'w') as zf:
                zf.write(target, temp_file)
        else:
            ext = '.tar.gz'
            with tarfile.open(filename + ext, 'w:gz',
                              compresslevel=0) as tar:
                tar.add(target, temp_file)

    if os.path.exists(temp_file):
        paths.remove_any(temp_file)

    output_filename = filename + ext
    log.debug('Archive output filename: %s', output_filename)
    return output_filename


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
                data = unicode(data)
            json_file.write(data)

        self._synced_json_kw = json_kw
        self._needs_sync = False
        return True
