# --------------------------------------------------------------------------
# Copyright 2014 Digital Sapphire Development Team
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

import pytest

from pyupdater.uploader import BaseUploader, Uploader
from pyupdater.utils.exceptions import UploaderError, UploaderPluginError

from tconfig import TConfig

my_config = TConfig()


@pytest.mark.usefixtures('cleandir')
class TestUtils(object):

    def test_plugin_baseclass_not_implemented(self):

        with pytest.raises(TypeError):
            b = BaseUploader()

    def test_plugin_baseclass(self, httpbin):
        class MyUploader(BaseUploader):

            def init_config(self, config):
                pass

            def set_config(self, config):
                pass

            def upload_file(self, filename):
                # with open('testfile.txt', 'wb') as f:
                #     if six.PY3:
                #         f.write(bytes('this is some text', 'utf-8'))
                #     else:
                #         f.write('this is some text')
                # with open('testfile.txt', 'r') as f:
                #     data = f.read()
                # files = {'file': data}
                # r = requests.post(httpbin.url + '/post', files=files)
                # assert r.json()['files']['file'] == str(data)
                pass

        mu = MyUploader()
        # mu.upload_file()


@pytest.mark.usefixtures('cleandir')
class TestExecution(object):
    def test_fail_no_uploader_set_fail(self, httpbin):
        # with pytest.raises(UploaderError):
        #     u = Uploader()
        #     u.init({})
        #     u.upload()
        pass

    def test_upload(self, httpbin):
        class MyUploader(BaseUploader):

            def init_config(self, config):
                pass

            def set_config(self, config):
                pass

            def upload_file(self, filename):
                # with open('testfile.txt', 'wb') as f:
                #     f.write(bytes('this is some text', 'utf-8'))
                # with open('testfile.txt', 'rb') as f:
                #     data = f.read()
                # files = {'file': data}
                # r = requests.post(httpbin.url + '/post', files=files)
                # assert r.json()['files']['file'] == data
                pass

        # u = Uploader()
        # u.init({'test': 'test'})
        # u.uploader = MyUploader()
        # u.uploader.init(test='test')
        # u.upload()

    # def test_set_uploader_fail(self):
    #     u = Uploader()
    #     u.init({'test': 'test'})
    #     with pytest.raises(UploaderError):
    #         u.set_uploader([])

    #     with pytest.raises(UploaderPluginError):
    #         u.set_uploader('bad plugin name')
