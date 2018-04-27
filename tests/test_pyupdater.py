# ------------------------------------------------------------------------------
# Copyright (c) 2015-2017 Digital Sapphire
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

import shutil
import subprocess
import os
import sys
import time
import filelock
from dsdev_utils.paths import ChDir
import pytest
import appdirs

from pyupdater import PyUpdater
from tconfig import TConfig

AUTO_UPDATE_PAUSE = 30
if sys.platform == 'win32':
    AUTO_UPDATE_PAUSE += 10

LOCK_TIMEOUT = 5*60  # ten minutes timeout
APP_NAME = 'Acme'

import logging
logging.basicConfig(level=logging.DEBUG)

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


class TestExecutionExtraction(object):

    @pytest.mark.parametrize("custom_dir, port, windowed",
                             [(True, 8000, True), (True, 8001, False),
                              (False, 8002, True), (False, 8003, False)])
    def test_execution_one_file_extract(self, cleandir, datadir, simpleserver,
                                        pyu, custom_dir, port,windowed):
        data_dir = datadir['update_repo_extract']
        pyu.setup()

        # We are moving all of the files from the deploy directory to the
        # cwd. We will start a simple http server to use for updates
        with ChDir(data_dir):
            simpleserver.start(port)

            cmd = 'python build_onefile_extract.py %s %s %s' % (custom_dir, port,windowed)
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

            app_run_command = app_name
            if sys.platform != 'win32':
                app_run_command = './{}'.format(app_name)

            if (sys.platform == 'darwin' and windowed):
                app_run_command = './{}.app/Contents/MacOS/{}'.format(app_name,app_name)
                app_name = '{}.app'.format(app_name)

            if custom_dir:
                # update with custom_dir is multiprocessing-safe
                lock_path = 'pyu.lock'
            else:
                if not os.path.exists(appdirs.user_data_dir(APP_NAME)):
                    os.makedirs(appdirs.user_data_dir(APP_NAME))
                lock_path = os.path.join(appdirs.user_data_dir(APP_NAME),
                                         'pyu.lock')

            update_lock = filelock.FileLock(lock_path, LOCK_TIMEOUT)

            output_file = 'version1.txt'
            with update_lock.acquire(LOCK_TIMEOUT, 5):
                count = 0
                while count < 5:
                    # Call the binary to self update
                    subprocess.call(app_run_command, shell=True)
                    if os.path.exists(output_file):
                        break
                    count += 1
                    print("Retrying app launch")
                    # Allow enough time for update process to complete.
                    time.sleep(AUTO_UPDATE_PAUSE)

            # Call the binary to ensure it's
            # the updated binary
            subprocess.call(app_run_command, shell=True)

            simpleserver.stop()
            # Detect if it was an overwrite error

            assert os.path.exists(app_name)
            assert os.path.exists(output_file)
            with open(output_file, 'r') as f:
                output = f.read().strip()
            assert output == '4.2'

            if os.path.exists(app_name):
                if (os.path.isdir(app_name)):
                    shutil.rmtree(app_name)
                else:
                    os.remove(app_name)

            if os.path.exists(output_file):
                os.remove(output_file)

    @pytest.mark.parametrize("custom_dir, port, windowed",
                             [(True, 8004, True), (True, 8005, False),
                              (False, 8006, True), (False, 8007, False)])
    def test_execution_one_dir_extract(self, cleandir, datadir, simpleserver,
                                       pyu, custom_dir, port, windowed):
        data_dir = datadir['update_repo_extract']
        pyu.setup()

        # We are moving all of the files from the deploy directory to the
        # cwd. We will start a simple http server to use for updates
        with ChDir(data_dir):
            simpleserver.start(port)

            cmd = 'python build_onedir_extract.py %s %s %s' % (custom_dir,
                                                               port, windowed)
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

            dir_name = 'Acme'
            if (not os.path.exists(dir_name)):
                dir_name = dir_name+'.app'

            assert os.path.exists(dir_name)
            assert os.path.isdir(dir_name)

            with open('pyu.log', 'w') as f:
                f.write('')

            app_name = 'Acme'
            if (sys.platform == 'darwin' and windowed):
                pass
            else:
                app_name = os.path.join(dir_name, app_name)

            if sys.platform != 'win32':
                app_name = './{}'.format(app_name)

            if sys.platform == 'win32':
                app_name += '.exe'

            with open('pyu.log', 'w') as f:
                f.write('')

            app_run_command = app_name
            if sys.platform != 'win32':
                app_run_command = './{}'.format(app_name)

            if (sys.platform == 'darwin' and windowed):
                app_run_command = './{}.app/Contents/MacOS/{}'.format(app_name,
                                                                      app_name)
                app_name = '{}.app'.format(app_name)

            if custom_dir:
                # update with custom_dir is multiprocessing-safe
                lock_path = 'pyu.lock'
            else:
                if not os.path.exists(appdirs.user_data_dir(APP_NAME)):
                    os.makedirs(appdirs.user_data_dir(APP_NAME))
                lock_path = os.path.join(appdirs.user_data_dir(APP_NAME),
                                         'pyu.lock')

            update_lock = filelock.FileLock(lock_path, LOCK_TIMEOUT)

            output_file = 'version1.txt'
            with update_lock.acquire(LOCK_TIMEOUT, 5):
                count = 0
                while count < 5:
                    # Call the binary to self update
                    subprocess.call(app_run_command, shell=True)
                    if os.path.exists(output_file):
                        break
                    count += 1
                    print("Retrying app launch")
                    # Allow enough time for update process to complete.
                    time.sleep(AUTO_UPDATE_PAUSE)

            # Call the binary to ensure it's
            # the updated binary
            subprocess.call(app_run_command, shell=True)

            simpleserver.stop()
            # Detect if it was an overwrite error
            assert os.path.exists(app_name)
            assert os.path.exists(output_file)
            with open(output_file, 'r') as f:
                output = f.read().strip()
            assert output == '4.2'

            if os.path.exists(app_name):
                if (os.path.isdir(app_name)):
                    shutil.rmtree(app_name)
                else:
                    shutil.rmtree(os.path.dirname(app_name))

            if os.path.exists(output_file):
                os.remove(output_file)


class TestExecutionRestart(object):

    @pytest.mark.parametrize("custom_dir, port, windowed",
                             [(True, 8008, True), (False, 8009, True),
                              (True, 8010, False), (False, 8011, False)])
    def test_execution_one_file_restart(self, cleandir, datadir, simpleserver,
                                        pyu, custom_dir, port, windowed):
        data_dir = datadir['update_repo_restart']
        pyu.setup()

        # We are moving all of the files from the deploy directory to the
        # cwd. We will start a simple http server to use for updates
        with ChDir(data_dir):
            print("***** CWD *****")
            print(os.path.abspath(data_dir))
            simpleserver.start(port)

            cmd = 'python build_onefile_restart.py %s %s %s' % (custom_dir,
                                                                port, windowed)
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

            app_run_command = app_name
            if sys.platform != 'win32':
                app_run_command = './{}'.format(app_name)

            if (sys.platform == 'darwin' and windowed):
                app_run_command = './{}.app/Contents/MacOS/{}'.format(app_name,
                                                                      app_name)
                app_name = '{}.app'.format(app_name)

            if custom_dir:
                # update with custom_dir is multiprocessing-safe
                lock_path = 'pyu.lock'
            else:
                if not os.path.exists(appdirs.user_data_dir(APP_NAME)):
                    os.makedirs(appdirs.user_data_dir(APP_NAME))
                lock_path = os.path.join(appdirs.user_data_dir(APP_NAME),
                                         'pyu.lock')

            update_lock = filelock.FileLock(lock_path, LOCK_TIMEOUT)

            version_file = 'version2.txt'
            with update_lock.acquire(LOCK_TIMEOUT, 5):
                count = 0
                while count < 5:
                    # Call the binary to self update
                    subprocess.call(app_run_command, shell=True)
                    if os.path.exists(version_file):
                        break
                    count += 1
                    print("Retrying app launch!")
                    # Allow enough time for update process to complete.
                    time.sleep(AUTO_UPDATE_PAUSE)

            simpleserver.stop()
            # Detect if it was an overwrite error
            assert os.path.exists(app_name)
            assert os.path.exists(version_file)
            with open(version_file, 'r') as f:
                output = f.read().strip()
            assert output == '4.2'

            if os.path.exists(app_name):
                if (os.path.isdir(app_name)):
                    shutil.rmtree(app_name)
                else:
                    os.remove(app_name)

            if os.path.exists(version_file):
                os.remove(version_file)

    @pytest.mark.parametrize("custom_dir, port, windowed",
                             [(True, 8012, True), (False, 8013, True),
                              (True, 8014, False), (False, 8015, False)])
    def test_execution_one_dir_restart(self, cleandir, datadir, simpleserver,
                                       pyu, custom_dir, port, windowed):
        data_dir = datadir['update_repo_restart']
        pyu.setup()

        # We are moving all of the files from the deploy directory to the
        # cwd. We will start a simple http server to use for updates
        with ChDir(data_dir):
            print("***** CWD *****")
            print(os.path.abspath(data_dir))
            simpleserver.start(port)

            cmd = 'python build_onedir_restart.py %s %s %s' % (custom_dir,
                                                               port, windowed)
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

            dir_name = 'Acme'
            if (not os.path.exists(dir_name)):
                dir_name = dir_name+'.app'

            assert os.path.exists(dir_name)
            assert os.path.isdir(dir_name)

            with open('pyu.log', 'w') as f:
                f.write('')

            app_name = 'Acme'
            if (sys.platform == 'darwin' and windowed):
                pass
            else:
                app_name = os.path.join(dir_name, app_name)

            if sys.platform != 'win32':
                app_name = './{}'.format(app_name)

            if sys.platform == 'win32':
                app_name += '.exe'

            with open('pyu.log', 'w') as f:
                f.write('')

            app_run_command = app_name
            if sys.platform != 'win32':
                app_run_command = './{}'.format(app_name)

            if (sys.platform == 'darwin' and windowed):
                app_run_command = './{}.app/Contents/MacOS/{}'.format(app_name,
                                                                      app_name)
                app_name = '{}.app'.format(app_name)

            if custom_dir:
                # update with custom_dir is multiprocessing-safe
                lock_path = 'pyu.lock'
            else:
                if not os.path.exists(appdirs.user_data_dir(APP_NAME)):
                    os.makedirs(appdirs.user_data_dir(APP_NAME))
                lock_path = os.path.join(appdirs.user_data_dir(APP_NAME),
                                         'pyu.lock')

            update_lock = filelock.FileLock(lock_path, LOCK_TIMEOUT)

            version_file = 'version2.txt'
            with update_lock.acquire(LOCK_TIMEOUT, 5):
                count = 0
                while count < 5:
                    # Call the binary to self update
                    subprocess.call(app_run_command, shell=True)
                    if os.path.exists(version_file):
                        break
                    count += 1
                    print("Retrying app launch!")
                    # Allow enough time for update process to complete.
                    time.sleep(AUTO_UPDATE_PAUSE)

            simpleserver.stop()
            # Detect if it was an overwrite error
            assert os.path.exists(app_name)
            assert os.path.exists(version_file)
            with open(version_file, 'r') as f:
                output = f.read().strip()
            assert output == '4.2'

            if os.path.exists(app_name):
                if (os.path.isdir(app_name)):
                    shutil.rmtree(app_name)
                else:
                    shutil.rmtree(os.path.dirname(app_name))

            if os.path.exists(version_file):
                os.remove(version_file)
