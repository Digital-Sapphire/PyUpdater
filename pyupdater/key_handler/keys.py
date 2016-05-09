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
from __future__ import unicode_literals

import io
import logging
import json
import os

from appdirs import user_data_dir
import ed25519
import six

from pyupdater.utils import check_repo
from pyupdater.utils.storage import Storage
from pyupdater import settings

log = logging.getLogger(__name__)


class Keys(object):

    def __init__(self, test=False):
        self.check = check_repo()
        self.key_encoding = 'base64'
        # Used for testing
        # When _load is called it'll cause an empty dict to be created
        if test is False:
            self.data_dir = user_data_dir('PyUpdater', 'Digital Sapphire')
        else:
            self.data_dir = os.path.join('private', 'data')
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        self.keypack_filename = os.path.join(self.data_dir, 'offline_keys.db')
        self._load()

    def make_keypack(self, name):
        # Will generate keypack specific to app name provided
        try:
            keypack = self._gen_keypack(name)
        except AssertionError:
            log.debug('Failed to generate keypack')
            return False
        # Write keypack to cwd
        with io.open(settings.KEYPACK_FILENAME, 'w', encoding="utf-8") as f:
            out = json.dumps(keypack, indent=2, sort_keys=True)
            if six.PY2:
                out = unicode(out)
            f.write(out)
        return True

    def _load(self):
        if not os.path.exists(self.keypack_filename):
            self.key_data = {}
            self._save()
        else:
            with io.open(self.keypack_filename, 'r', encoding="utf-8") as f:
                self.key_data = json.loads(f.read())

    def _save(self):
        if self.keypack_filename is not None:
            with io.open(self.keypack_filename, 'w', encoding="utf-8") as f:
                out = json.dumps(self.key_data, indent=2, sort_keys=True)
                if six.PY2:
                    out = unicode(out)
                f.write(out)

    def _gen_keypack(self, name):
        app_pri, app_pub = self._make_keys()
        off_pri, off_pub = self._load_offline_keys(name)
        log.debug('off_pri type: %s', off_pri)

        off_pri = off_pri.encode()
        if six.PY2:
            app_pub = six.b(app_pub)
            log.debug('off_pri type: %s', type(off_pri))
        signing_key = ed25519.SigningKey(off_pri, encoding='base64')

        signature = signing_key.sign(app_pub,
                                     encoding='base64').decode()

        if six.PY3:
            app_pri = app_pri.decode()
            app_pub = app_pub.decode()

        keypack = {
            'upload': {
                'app_public': app_pub,
                'signature': signature
                },
            'client': {
                'offline_public': off_pub
                },
            'repo': {
                'app_private': app_pri
                }
            }
        return keypack

    def _load_offline_keys(self, name):
        if name not in self.key_data.keys():
            # We create new offline keys for each app
            pri, pub = self._make_keys()
            if six.PY3:
                pri = pri.decode()
                pub = pub.decode()
            self.key_data[name] = {'private': pri, 'public': pub}
            self._save()
        return self.key_data[name]['private'], self.key_data[name]['public']

    def _make_keys(self):
        # Makes a set of private and public keys
        # Used for authentication
        privkey, pubkey = ed25519.create_keypair()
        pri = privkey.to_ascii(encoding=self.key_encoding)
        pub = pubkey.to_ascii(encoding=self.key_encoding)
        return pri, pub


# ToDo: Add some sanitation checks
class KeyImporter(object):

    def __init__(self):
        self.db = Storage()

    def _look_for_keypack(self):
        files = os.listdir(os.getcwd())
        if settings.KEYPACK_FILENAME not in files:
            return False
        return True

    def _load_keypack(self):
        json_data = None
        try:
            with io.open(settings.KEYPACK_FILENAME, 'r',
                         encoding='utf-8') as f:
                data = f.read()
        except Exception as err:
            log.debug(err, exc_info=True)
        else:
            try:
                json_data = json.loads(data)
            except Exception as err:
                log.debug(err, exc_info=True)
        return json_data

    def start(self):
        found = self._look_for_keypack()
        if found is False:
            return False
        keypack = self._load_keypack()
        if keypack is None:
            return False
        self.db.save(settings.CONFIG_DB_KEY_KEYPACK, keypack)
        return True
