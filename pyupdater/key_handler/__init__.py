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
from __future__ import print_function
from __future__ import unicode_literals

from pyupdater import settings
from pyupdater.utils import lazy_import
from pyupdater.utils.storage import Storage


@lazy_import
def gzip():
    import gzip
    return gzip


@lazy_import
def json():
    import json
    return json


@lazy_import
def logging():
    import logging
    return logging


@lazy_import
def os():
    import os
    return os


@lazy_import
def shutil():
    import shutil
    return shutil


@lazy_import
def ed25519():
    import ed25519
    return ed25519


@lazy_import
def six():
    import six
    return six


log = logging.getLogger(__name__)


class KeyHandler(object):
    """KeyHanlder object is used to manage keys used for signing updates

    Kwargs:

        app (obj): Config object to get config values from
    """

    def __init__(self):
        self.db = Storage()

        self.key_encoding = 'base64'
        data_dir = os.getcwd()
        self.data_dir = os.path.join(data_dir, settings.USER_DATA_FOLDER)
        self.deploy_dir = os.path.join(self.data_dir, 'deploy')
        self.keypack_filename = os.path.join(data_dir,
                                             settings.CONFIG_DATA_FOLDER,
                                             settings.KEYPACK_FILENAME)
        self.version_file = os.path.join(self.deploy_dir,
                                         settings.VERSION_FILE)
        self.key_file = os.path.join(self.deploy_dir,
                                     settings.KEY_FILE)

    def sign_update(self):
        """Signs version file with private key

        Proxy method for :meth:`_add_sig`
        """
        # Loads private key
        # Loads version file to memory
        # Signs Version file
        # Writes version file back to disk
        self._add_sig()

    def _load_private_keys(self):
        # Loads private key
        log.debug('Loading private key')
        keypack_data = self.db.load(settings.CONFIG_DB_KEY_KEYPACK)
        private_key = None
        if keypack_data is not None:
            try:
                private_key = keypack_data['repo']['app_private']
            except KeyError:
                # We will exit in _add_sig if private_key is None
                pass
        return private_key

    def _add_sig(self):
        # Adding new signature to version file
        # Raw private key will need to be converted into
        # a signing key object
        private_key_raw = self._load_private_keys()
        if private_key_raw is None:
            log.error('Private Key not found. Please '
                      'import a keypack & try again')
            return

        update_data = self._load_update_data()
        if 'signature' in update_data:
            log.debug('Removing signatures from version file')
            del update_data['signature']
        update_data_str = json.dumps(update_data, sort_keys=True)

        log.debug('Key type before: %s', type(private_key_raw))
        private_key_raw = private_key_raw.encode('utf-8')
        log.debug('Key type after: %s', type(private_key_raw))

        # Creating signing key object
        private_key = ed25519.SigningKey(private_key_raw,
                                         encoding=self.key_encoding)
        # Signs update data with private key
        signature = private_key.sign(six.b(update_data_str),
                                     encoding=self.key_encoding).decode()
        log.debug('Sig: %s', signature)

        update_data = json.loads(update_data_str)
        # Add signatures to update data
        update_data['signature'] = signature
        log.info('Adding sig to update data')
        # Write updated version file to filesystem
        self._write_update_data(update_data)
        self._write_key_file()

    def _write_update_data(self, data):
        # Save update data to repo database
        self.db.save(settings.CONFIG_DB_KEY_VERSION_META, data)
        log.debug('Saved version meta data')
        log.debug('Upload manifest: \n%s', data)
        # Gzip update date
        with gzip.open(self.version_file, 'wb') as f:
            new_data = json.dumps(data)
            if six.PY2:
                f.write(new_data)
            else:
                f.write(bytes(new_data, 'utf-8'))
        log.info('Created gzipped version manifest in deploy dir')

    def _write_key_file(self):
        keypack_data = self.db.load(settings.CONFIG_DB_KEY_KEYPACK)
        if keypack_data is None:
            log.error('Private Key not found. Please '
                      'import a keypack & try again')
            return

        upload_data = keypack_data['upload']
        with gzip.open(self.key_file, 'wb') as f:
            new_data = json.dumps(upload_data)
            if six.PY2:
                f.write(new_data)
            else:
                f.write(bytes(new_data, 'utf-8'))
        log.info('Created gzipped key file in deploy dir')

    def _load_update_data(self):
        log.debug("Loading version data")
        update_data = self.db.load(settings.CONFIG_DB_KEY_VERSION_META)
        # If update_data is None, create a new one
        if update_data is None:
            update_data = {}
            log.error('Version meta data not found')
            self.db.save(settings.CONFIG_DB_KEY_VERSION_META, update_data)
            log.info('Created new version meta data')
        log.debug('Version file loaded')
        return update_data
