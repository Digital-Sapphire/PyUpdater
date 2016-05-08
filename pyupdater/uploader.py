# --------------------------------------------------------------------------
# Copyright 2015 Digital Sapphire Development Team
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

from abc import ABCMeta, abstractmethod
import logging
import os
import time

from jms_utils.terminal import get_correct_answer
import six
from straight.plugin import load

from pyupdater import settings
from pyupdater.utils import remove_dot_files
from pyupdater.utils.exceptions import UploaderError, UploaderPluginError

log = logging.getLogger(__name__)

class PluginManager(object):

    PLUGIN_NAMESPACE = 'pyupdater.plugins'

    def __init__(self, config):
        plugins_namespace = load(self.PLUGIN_NAMESPACE, subclass=BaseUploader)
        plugins = plugins_namespace.produce()
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
            # Todo: This could break build scripts since the
            #       load order of the plugins could be
            #       different. Maybe sort by original name
            #       and author before the above for loop
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
        config_key = '{}-{}'.format(plugin.name, plugin.author)
        # Get the config for this plugin
        plugin_config = configs.get(config_key, {})
        # Get the plugin its config dict for updating
        try:
            plugin.set_config(plugin_config)
        except Exception as err:
            log.error('There was an error during configuration '
                      'of {} crated by {}'.format(plugin.name, plugin.author))
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

    def get_plugin(self, name):
        "Returns the named plugin"
        plugin = None
        for k, v in self.plugins.items():
            # We match the given name to the names
            # we generate for uniqueness
            if name == v['name']:
                plugin = v['plugin']
                break
        if plugin is not None:
            config_key = '{}-{}'.format(v['name'], v['author'])
            config = self.configs.get(config_key, {})
            plugin.init_config(config)

        return plugin


class Uploader(object):
    """Uploads updates to configured servers.  SSH, SFTP, S3
    Will automatically pick the correct uploader depending on
    what is configured thorough the config object

    Sets up client with config values from obj

        Args:

            obj (instance): config object
    """
    def __init__(self, config=None):
        if config:
            self.init(config)

    def init(self, obj):
        """Sets up client with config values from obj

        Args:

            obj (instance): config object
        """
        data_dir = os.path.join(os.getcwd(), settings.USER_DATA_FOLDER)
        self.deploy_dir = os.path.join(data_dir, 'deploy')
        self.uploader = None
        # Files to be uploaded
        self.files = []
        self.test = False

        # Extension Manager
        self.mgr = PluginManager(obj)

    def get_plugin_names(self):
        return self.mgr.get_plugin_names()

    def set_uploader(self, requested_uploader):
        """Returns an uploader object. 1 of S3, SCP, SFTP.
        SFTP uploaders not supported at this time.

        Args:

            requested_uploader (string): Either s3 or scp

        Returns:

            object (instance): Uploader object
        """
        if isinstance(requested_uploader, six.string_types) is False:
            raise UploaderError('Must pass str to set_uploader',
                                expected=True)

        self.uploader = self.mgr.get_plugin(requested_uploader)
        if self.uploader is None:
            log.debug('PLUGIN_NAMESPACE: %s', self.mgr.PLUGIN_NAMESPACE)
            raise UploaderPluginError('Requested uploader is not installed',
                                      expected=True)

        msg = 'Requested uploader: {}'.format(requested_uploader)
        log.debug(msg)
        try:
            _files = os.listdir(self.deploy_dir)
        except OSError:
            _files = []

        files = []
        for f in _files:
            files.append(os.path.join(self.deploy_dir, f))

        self.files = remove_dot_files(files)

    def upload(self):
        """Uploads all files in file_list"""
        failed_uploads = []
        self.files_completed = 1
        self.file_count = len(self.files)
        log.info('Plugin: %s', self.uploader.name)
        log.info('Author: %s', self.uploader.author)
        for f in self.files:
            msg = '\n\nUploading: {}' .format(f)
            msg2 = ' - File {} of {}\n'.format(self.files_completed,
                                               self.file_count)
            print(msg + msg2)
            complete = self.uploader.upload_file(f)
            basename = os.path.basename(f)
            if complete:
                log.debug('%s uploaded successfully', basename)
                os.remove(f)
                self.files_completed += 1
            else:
                log.debug('%s failed to upload.  will retry', basename)
                failed_uploads.append(f)
        if len(failed_uploads) > 0:
            failed_uploads = self._retry_upload(failed_uploads)
        if len(failed_uploads) < 1:
            print("\nUpload Complete")
            time.sleep(3)
            return True
        else:
            print('The following files were not uploaded')
            for i in failed_uploads:
                log.error('%s failed to upload', os.path.basename(i))
                print(i)
            return False

    def _retry_upload(self, failed_uploads):
        # Takes list of failed downloads and tries to re upload them
        retry = failed_uploads[:]
        failed_uploads = []
        failed_count = len(retry)
        count = 1
        for f in retry:
            msg = '\n\nRetyring: {} - File {} of {}\n'.format(f, count,
                                                              failed_count)
            print(msg)
            complete = self.plugin.upload_file(f)
            if complete:
                log.debug('%s uploaded on retry', f)
                count += 1
            else:
                failed_uploads.append(f)

        return failed_uploads



@six.add_metaclass(ABCMeta)
class BaseUploader(object):
    """Base Uploader.  All uploaders should subclass
    this base class
    """
    def get_answer(self, question):
        return get_correct_answer(question, required=True)

    @abstractmethod
    def init_config(self, config):
        """Used to initialize plugin with saved config.

        Args:

            config (dict): config dict for plugin
        """
        raise NotImplementedError('Must be implemented in subclass.')

    @abstractmethod
    def set_config(self, config):
        """Used to ask user questions and return config
        for saving

        Args:

            config (dict): config dict that can be used to query
                            already set values

        """
        raise NotImplementedError('Must be implemented in a subclass.')

    @abstractmethod
    def upload_file(self, filename):
        """Uploads file to remote repository

        Args:
            filename (str): file to upload

        Returns:
            (bool) Meaning::

                True - Upload Successful

                False - Upload Failed
        """
        raise NotImplementedError('Must be implemented in subclass.')
