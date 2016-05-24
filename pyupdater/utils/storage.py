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
from __future__ import print_function, unicode_literals

import logging
import os

from pyupdater import settings
from pyupdater.utils import JSONStore

log = logging.getLogger(__name__)


# Used by KeyHandler, PackageHandler & Config to
# store data in a json file
class Storage(object):

    def __init__(self):
        """Loads & saves config file to file-system.

            Args:

                config_dir (str): Path to directory where config will be stored
        """
        self.config_dir = os.path.join(os.getcwd(),
                                       settings.CONFIG_DATA_FOLDER)
        if not os.path.exists(self.config_dir):
            log.info('Creating config dir')
            os.mkdir(self.config_dir)
        log.debug('Config Dir: %s', self.config_dir)
        self.filename = os.path.join(self.config_dir,
                                     settings.CONFIG_FILE_USER)
        log.debug('Config DB: %s', self.filename)
        self.db = JSONStore(self.filename)
        self.sync_threshold = 3
        self.count = 0
        self._load_db()

    def __getattr__(self, name):
        return self.__class__.__dict__.get(name)

    def __setattr__(self, name, value):
        setattr(self.__class__, name, value)

    def __delattr__(self, name):
        raise AttributeError('Cannot delete attributes!')

    def __getitem__(self, name):
        try:
            return self.__class__.__dict__[name]
        except KeyError:
            return self.__dict__[name]

    def __setitem__(self, name, value):
        setattr(Storage, name, value)

    def _load_db(self):
        "Loads database into memory."
        for k, v in self.db:
            setattr(Storage, k, v)

    def save(self, key, value):
        """Saves key & value to database

        Args:

            key (str): used to retrieve value from database

            value (obj): python object to store in database

        """
        setattr(Storage, key, value)
        for k, v in Storage.__dict__.items():
            self.db[k] = v
        log.debug('Syncing db to filesystem')
        self.db.sync()

    def load(self, key):
        """Loads value for given key

            Args:

                key (str): The key associated with the value you want
                form the database.

            Returns:

                Object if exists or else None
        """
        return self.__class__.__dict__.get(key)
