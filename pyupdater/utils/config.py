# --------------------------------------------------------------------------
# Copyright (c) 2016 Digital Sapphire
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
from __future__ import unicode_literals

import logging
import os

from pyupdater import settings
from pyupdater.utils.storage import Storage

log = logging.getLogger(__name__)


class Config(dict):
    def __init__(self, *args, **kwargs):
        super(Config, self).__init__(*args, **kwargs)
        self.__dict__ = self
        self.__postinit__()

    def __postinit__(self):
        config_template = {
            # If left None "PyUpdater App" will be used
            'APP_NAME': settings.GENERIC_APP_NAME,

            # path to place client config
            'CLIENT_CONFIG_PATH': settings.DEFAULT_CLIENT_CONFIG,

            # Company/Your name
            'COMPANY_NAME': settings.GENERIC_APP_NAME,

            'PLUGIN_CONFIGS': {},

            # Support for patch updates
            'UPDATE_PATCHES': True
            }
        self.update(config_template)

    def from_object(self, obj):
        """Updates the values from the given object

        Args:

            obj (instance): Object with config attributes

        Objects are classes.

        Just the uppercase variables in that object are stored in the config.
        Example usage::

            from yourapplication import default_config
            app.config.from_object(default_config())
        """
        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)


class Loader(object):
    """Loads &  saves config file
    """

    def __init__(self):
        self.cwd = os.getcwd()
        self.db = Storage()
        self.password = os.environ.get(settings.USER_PASS_ENV)
        self.config_key = settings.CONFIG_DB_KEY_APP_CONFIG

    def load_config(self):
        """Loads config from database (json file)

            Returns (obj): Config object
        """
        config_data = self.db.load(self.config_key)
        if config_data is None:
            config_data = {}
        config = Config()
        for k, v in config_data.items():
            config[k] = v
        config.DATA_DIR = os.getcwd()
        return config

    def get_app_name(self):
        config = self.load_config()
        return config.APP_NAME

    def save_config(self, obj):
        """Saves config file to pyupdater database

        Args:

            obj (obj): config object
        """
        log.info('Saving Config')
        self.db.save(self.config_key, obj)
        log.info('Config saved')
        self._write_config_py(obj)
        log.info('Wrote client config')

    def _write_config_py(self, obj):
        """Writes client config to client_config.py

        Args:

            obj (obj): config object
        """
        keypack_data = self.db.load(settings.CONFIG_DB_KEY_KEYPACK)
        if keypack_data is None:
            public_key = None
        else:
            public_key = keypack_data['client']['offline_public']

        filename = os.path.join(self.cwd, *obj.CLIENT_CONFIG_PATH)
        attr_str_format = "    {} = '{}'\n"
        attr_format = "    {} = {}\n"
        with open(filename, 'w') as f:
            f.write('class ClientConfig(object):\n')
            if hasattr(obj, 'APP_NAME') and obj.APP_NAME is not None:
                f.write(attr_str_format.format('APP_NAME', obj.APP_NAME))
                log.debug('Wrote APP_NAME to client config')
            if hasattr(obj, 'COMPANY_NAME') and obj.COMPANY_NAME is not None:
                f.write(attr_str_format.format('COMPANY_NAME',
                        obj.COMPANY_NAME))
                log.debug('Wrote COMPANY_NAME to client config')
            if hasattr(obj, 'UPDATE_URLS') and obj.UPDATE_URLS is not None:
                f.write(attr_format.format('UPDATE_URLS', obj.UPDATE_URLS))
                log.debug('Wrote UPDATE_URLS to client config')
            f.write(attr_str_format.format('PUBLIC_KEY', public_key))
            log.debug('Wrote PUBLIC_KEY to client config')
