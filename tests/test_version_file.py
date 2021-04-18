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

import json

from nacl.signing import VerifyKey
import pytest

from pyupdater.utils.encoding import UnpaddedBase64Encoder


@pytest.mark.usefixtures("cleandir")
class TestVersionFile(object):
    def test_signature(self, shared_datadir):
        json_raw = (shared_datadir / "version.json").read_text()
        version_data = json.loads(json_raw)

        sig = version_data["signature"]
        del version_data["signature"]

        data = json.dumps(version_data, sort_keys=True)

        version_data = bytes(data, "utf-8")

        jms_pub = (shared_datadir / "jms.pub").read_text()
        public_key = VerifyKey(jms_pub, UnpaddedBase64Encoder())

        sig = UnpaddedBase64Encoder.decode(sig)
        public_key.verify(version_data, sig)
