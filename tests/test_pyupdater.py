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
from __future__ import print_function, unicode_literals

try:
    from http.server import SimpleHTTPRequestHandler as RequestHandler
except ImportError:
    from SimpleHTTPServer import SimpleHTTPRequestHandler as RequestHandler

try:
    import socketserver as socket_server
except:
    import SocketServer as socket_server

import shutil
import subprocess
import threading
import os
import sys
import time

from dsdev_utils.paths import ChDir
import pytest
import six

from pyupdater import PyUpdater
from tconfig import TConfig

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'test-data',
                             'client')


@pytest.mark.usefixtures('cleandir', 'create_keypack', 'pyu')
class TestSetup(object):

    def test_directory_creation(self):
        data_dir = os.getcwd()
        pyu_data_dir = os.path.join(data_dir, 'pyu-data')
        t_config = TConfig()
        t_config.DATA_DIR = data_dir
        pyu = PyUpdater(t_config)
        pyu.setup()
        assert os.path.exists(pyu_data_dir)
        assert os.path.exists(os.path.join(pyu_data_dir, 'deploy'))
        assert os.path.exists(os.path.join(pyu_data_dir, 'files'))
        assert os.path.exists(os.path.join(pyu_data_dir, 'new'))


@pytest.mark.usefixtures('cleandir', 'create_keypack', 'pyu')
class TestExecution(object):

    def test_execution_update(self):
        dest = os.getcwd()
        with ChDir(TEST_DATA_DIR):
            files = os.listdir(os.getcwd())
            for f in files:
                dest_path = os.path.join(dest, f)
                if os.path.isfile(f):
                    if os.path.exists(dest_path):
                        os.remove(dest_path)
                    shutil.copy(f, dest)
                else:
                    if os.path.exists(dest_path):
                        shutil.rmtree(dest_path, ignore_errors=True)
                    shutil.copytree(f, dest_path)

        PORT = 8000
        socket_server.TCPServer.allow_reuse_address = True
        httpd = socket_server.TCPServer(("", PORT), RequestHandler)

        # class MyServer(threading.Thread):

        #     def run(self):
        #         self.heartbeat = True
        #         while heartbeat:

        t = threading.Thread(target=httpd.serve_forever)
        t.daemon = True
        t.start()

        cmd = 'python app_build.py'
        os.system(cmd)

        deploy_dir = os.path.join('pyu-data', 'deploy')
        with ChDir(deploy_dir):
            files = os.listdir(os.getcwd())
            for f in files:
                shutil.move(f, dest)

        app_name = 'Acme'
        if sys.platform == 'win32':
            app_name += '.exe'

        with open('pyu.log', 'w') as f:
            f.write('')

        print(os.listdir(os.getcwd()))
        if sys.platform != 'win32':
            app_name = './{}'.format(app_name)

        print('Appname: {}'.format(app_name))
        # Call the binary to self update
        out = subprocess.check_output(app_name, shell=True)
        time.sleep(15)

        # Call again to check the output
        out = subprocess.check_output(app_name, shell=True)
        out = out.strip()

        with open('pyu.log', 'r') as f:
            data = f.read()

        print(data)
        assert out == six.b('4.2')
