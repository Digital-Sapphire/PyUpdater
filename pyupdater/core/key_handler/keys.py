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
import io
import logging
import json
import os

from appdirs import user_data_dir
from nacl.signing import SigningKey

from pyupdater import settings
from pyupdater.utils.exceptions import KeyHandlerError
from pyupdater.utils.encoding import UnpaddedBase64Encoder
from pyupdater.utils.storage import Storage


log = logging.getLogger(__name__)


class Keys(object):
    def __init__(self, test=False):
        # We use base64 encoding for easy human consumption
        self.key_encoder = UnpaddedBase64Encoder()
        self.key_data = {}

        if test:
            self.data_dir = os.path.join("private", "data")
        else:
            self.data_dir = user_data_dir("PyUpdater", "Digital Sapphire")

        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        # The name of the offline key database
        self.keypack_filename = os.path.join(self.data_dir, "offline_keys.db")
        self._load()

    def make_keypack(self, name):
        # Will generate keypack specific to app name provided
        try:
            keypack = self._gen_keypack(name)
        except AssertionError:
            log.debug("Failed to generate keypack")
            return False
        except KeyHandlerError as err:
            log.error(err)
            return False

        # Write keypack to cwd
        with io.open(settings.KEYPACK_FILENAME, "w", encoding="utf-8") as f:
            out = json.dumps(keypack, indent=2, sort_keys=True)
            f.write(out)
        return True

    def _load(self):
        if not os.path.exists(self.keypack_filename):
            self._save()
        else:
            with io.open(self.keypack_filename, "r", encoding="utf-8") as f:
                self.key_data = json.loads(f.read())

    def _save(self):
        with io.open(self.keypack_filename, "w", encoding="utf-8") as f:
            out = json.dumps(self.key_data, indent=2, sort_keys=True)
            f.write(out)

    def _gen_keypack(self, name):
        # Create new public & private key for app signing
        try:
            app_pri, app_pub = self._make_keys()
        except Exception as err:
            log.error(err)
            log.debug(err, exc_info=True)
            raise KeyHandlerError("Failed to create keypair")

        # Load app specific private & public key
        off_pri, off_pub = self._load_offline_keys(name)

        log.debug("off_pri type: %s", type(off_pri))
        off_pri = off_pri.encode()

        signing_key = SigningKey(off_pri, self.key_encoder)

        # Create signature from app signing public key
        signature = signing_key.sign(app_pub)[:64]
        signature = self.key_encoder.encode(signature).decode()

        app_pri = app_pri.decode()
        app_pub = app_pub.decode()

        keypack = {
            "upload": {"app_public": app_pub, "signature": signature},
            "client": {"offline_public": off_pub},
            "repo": {"app_private": app_pri},
        }
        return keypack

    def _load_offline_keys(self, name):
        if name not in self.key_data.keys():
            # We create new offline keys for each app
            pri, pub = self._make_keys()
            pri = pri.decode()
            pub = pub.decode()
            self.key_data[name] = {"private": pri, "public": pub}
            self._save()
        return self.key_data[name]["private"], self.key_data[name]["public"]

    def _make_keys(self):
        # Makes a set of private and public keys
        privkey = SigningKey.generate()
        pubkey = privkey.verify_key

        pri = privkey.encode(self.key_encoder)
        pub = pubkey.encode(self.key_encoder)
        return pri, pub


class KeyImporter(object):
    def __init__(self):
        self.db = Storage()

    @staticmethod
    def _look_for_keypack():
        files = os.listdir(os.getcwd())
        if settings.KEYPACK_FILENAME not in files:
            return False
        return True

    @staticmethod
    def _load_keypack():
        json_data = None
        try:
            with io.open(settings.KEYPACK_FILENAME, "r", encoding="utf-8") as f:
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
        found = KeyImporter._look_for_keypack()
        if found is False:
            return False
        keypack = KeyImporter._load_keypack()
        if keypack is None:
            return False
        self.db.save(settings.CONFIG_DB_KEY_KEYPACK, keypack)
        return True
