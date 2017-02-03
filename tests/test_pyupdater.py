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

import shutil
import subprocess
import os
import sys
import time

from dsdev_utils.paths import ChDir
import pytest
import six

from pyupdater import PyUpdater
from tconfig import TConfig

AUTO_UPDATE_PAUSE = 25
if sys.platform == 'win32':
    AUTO_UPDATE_PAUSE += 10


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


@pytest.mark.usefixtures('cleandir')
class TestExecutionExtraction(object):

    def test_execution_onefile_extract(self, datadir, simpleserver, pyu):
        data_dir = datadir['update_repo_extract']
        pyu.setup()

        # We are moving all of the files from the deploy directory to the
        # cwd. We will start a simple http server to use for updates
        with ChDir(data_dir):
            simpleserver.start(8000)

            cmd = 'python build_onefile_extract.py'
            os.system(cmd)

            # Moving all files from the deploy directory to the cwd
            # since that is where we will start the simple server
            deploy_dir = os.path.join('pyu-data', 'deploy')
            assert os.path.exists(deploy_dir)
            test_cwd = os.getcwd()
            with ChDir(deploy_dir):
                files = os.listdir(os.getcwd())
                for f in files:
                    if f == '.DS_Store':
                        continue
                    shutil.move(f, test_cwd)

            app_name = 'Acme'
            if sys.platform == 'win32':
                app_name += '.exe'

            with open('pyu.log', 'w') as f:
                f.write('')

            if sys.platform != 'win32':
                app_name = './{}'.format(app_name)

            # Call the binary to self update
            subprocess.call(app_name, shell=True)
            # Allow enough time for update process to complete.
            time.sleep(AUTO_UPDATE_PAUSE)

            # Call again to check the output
            out = subprocess.check_output(app_name, shell=True)
            out = out.strip()

            simpleserver.stop()

            assert out == six.b('4.2')


@pytest.mark.usefixtures('cleandir')
class TestExecutionRestart(object):

    def test_execution_one_file_restart(self, datadir, simpleserver, pyu):
        data_dir = datadir['update_repo_restart']
        pyu.setup()

        # We are moving all of the files from the deploy directory to the
        # cwd. We will start a simple http server to use for updates
        with ChDir(data_dir):
            simpleserver.start(8001)

            cmd = 'python build_onefile_restart.py'
            os.system(cmd)

            # Moving all files from the deploy directory to the cwd
            # since that is where we will start the simple server
            deploy_dir = os.path.join('pyu-data', 'deploy')
            assert os.path.exists(deploy_dir)
            test_cwd = os.getcwd()
            with ChDir(deploy_dir):
                files = os.listdir(os.getcwd())
                for f in files:
                    if f == '.DS_Store':
                        continue
                    shutil.move(f, test_cwd)

            app_name = 'Acme'
            if sys.platform == 'win32':
                app_name += '.exe'

            with open('pyu.log', 'w') as f:
                f.write('')

            if sys.platform != 'win32':
                app_name = './{}'.format(app_name)

            # Call the binary to self update
            subprocess.call(app_name)
            # Allow enough time for update process to complete.
            time.sleep(AUTO_UPDATE_PAUSE)

            simpleserver.stop()

            assert os.path.exists('version2.txt')
            with open('version2.txt', 'r') as f:
                output = f.read().strip()
            assert output == '4.2'
