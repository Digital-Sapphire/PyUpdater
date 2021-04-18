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
        """Loads & saves config file to file-system."""
        self.config_dir = os.path.join(os.getcwd(), settings.CONFIG_DATA_FOLDER)
        if not os.path.exists(self.config_dir):
            log.debug("Creating config dir")
            os.mkdir(self.config_dir)
        log.debug("Config Dir: %s", self.config_dir)
        self.filename = os.path.join(self.config_dir, settings.CONFIG_FILE_USER)
        log.debug("Config DB: %s", self.filename)
        self.db = JSONStore(self.filename)
        self.count = 0
        self._load_db()

    def __getattr__(self, name):
        return self.__class__.__dict__.get(name)

    def __setattr__(self, name, value):
        setattr(self.__class__, name, value)

    def __delattr__(self, name):
        raise AttributeError("Cannot delete attributes!")

    def __getitem__(self, name):
        try:
            return self.__class__.__dict__[name]
        except KeyError:
            return self.__dict__[name]

    def __setitem__(self, name, value):
        setattr(Storage, name, value)

    def _load_db(self):
        """Loads database into memory."""
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
        log.debug("Syncing db to filesystem")
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
