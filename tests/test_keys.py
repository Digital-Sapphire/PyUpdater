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
import os

import pytest

from pyupdater.key_handler.keys import Keys


@pytest.mark.usefixtures("cleandir")
class TestKeyPack(object):

    def test_create_keypack(self):
        k = Keys(test=True)
        for name in ['one', 'two', 'three']:
            assert k.make_keypack(name) is True
        assert os.path.exists(k.data_dir) is True
