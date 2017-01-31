# --------------------------------------------------------------------------
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
# --------------------------------------------------------------------------
from __future__ import unicode_literals
import io
import logging
import os
import sys
import time

from pyupdater import settings
from pyupdater.hooks import get_hook_dir
from pyupdater.pyinstaller_compat import pyi_makespec
from pyupdater.utils import (check_repo,
                             create_asset_archive,
                             make_archive)
from pyupdater.utils.config import ConfigManager

from dsdev_utils.exceptions import VersionError
from dsdev_utils.helpers import Version
from dsdev_utils.paths import ChDir, remove_any
from dsdev_utils.system import get_system
from PyInstaller.__main__ import run as pyi_build


log = logging.getLogger(__name__)


class Builder(object):  # pragma: no cover
    """Wrapper for Pyinstaller with some extras. After building
    executable with pyinstaller, Builder will create an archive
    of the executable.

    Args:

        args (list): Args specific to PyUpdater

        pyi_args (list): Args specific to Pyinstaller
    """

    def __init__(self, args, pyi_args):
        check_repo()
        # We only need to grab appname
        cm = ConfigManager()
        self.app_name = cm.get_app_name()
        self.args = args
        self.app_info, self.pyi_args = self._check_input_file(pyi_args)

    # Creates & archives executable
    def build(self):
        start = time.time()
        temp_name = get_system()
        # Check for spec file or python script
        self._setup()
        spec_file_path = os.path.join(self.spec_dir, temp_name + '.spec')

        # Spec file used instead of python script
        if self.app_info['type'] == 'spec':
            spec_file_path = self.app_info['name']
        else:
            # Creating spec file from script
            self._make_spec(self.pyi_args, temp_name, self.app_info)

        # Build executable
        self._build(self.args, spec_file_path)
        # Archive executable
        self._archive(self.args, temp_name)
        finished = time.time() - start
        msg = 'Build finished in {:.2f} seconds.'.format(finished)
        log.info(msg)

    def make_spec(self):
        temp_name = get_system()
        self._make_spec(self.pyi_args, temp_name,
                        self.app_info, spec_only=True)

    def _setup(self):
        # Create required directories
        self.pyi_dir = os.path.join(os.getcwd(), settings.USER_DATA_FOLDER)
        self.new_dir = os.path.join(self.pyi_dir, 'new')
        self.build_dir = os.path.join(os.getcwd(), settings.CONFIG_DATA_FOLDER)
        self.spec_dir = os.path.join(self.build_dir, 'spec')
        self.work_dir = os.path.join(self.build_dir, 'work')
        for d in [self.build_dir, self.spec_dir, self.work_dir,
                  self.pyi_dir, self.new_dir]:
            if os.path.exists(self.work_dir):
                remove_any(self.work_dir)
            if not os.path.exists(d):
                log.debug('Creating directory: %s', d)
                os.mkdir(d)

    # Ensure that a spec file or python script is present
    def _check_input_file(self, pyi_args):
        verified = False
        new_args = []
        for p in pyi_args:
            if p.endswith('.py'):
                log.debug('Building from python source file: %s', p)
                p_path = os.path.abspath(p)
                log.debug('Source file abs path: %s', p_path)
                app_info = {'type': 'script', 'name': p_path}
                verified = True

            elif p.endswith('.spec'):
                log.debug('Building from spec file: %s', p)
                app_info = {'type': 'spec', 'name': p}
                verified = True
            else:
                new_args.append(p)

        if verified is False:
            log.error('Must pass a python script or spec file')
            sys.exit(1)
        return app_info, new_args

    # Take args from PyUpdater then sanatize & combine to be
    # passed to pyinstaller
    def _make_spec(self, spec_args, temp_name,
                   app_info, spec_only=False):
        log.debug('App Info: %s', app_info)

        # Ensure that onefile mode is passed
        spec_args.append('-F')
        spec_args.append('--name={}'.format(temp_name))
        if spec_only is True:
            log.debug('*** User generated spec file ***')
            log.debug('There could be errors')
            spec_args.append('--specpath={}'.format(os.getcwd()))
        else:
            # Place spec file in .pyupdater/spec
            spec_args.append('--specpath={}'.format(self.spec_dir))

        # Use hooks included in PyUpdater package
        hook_dir = get_hook_dir()
        log.debug('Hook directory: %s', hook_dir)
        spec_args.append('--additional-hooks-dir={}'.format(hook_dir))
        spec_args.append(app_info['name'])

        log.debug('Make spec cmd: %s', ' '.join([c for c in spec_args]))
        success = pyi_makespec(spec_args)
        if success is False:
            log.error('PyInstaller > 3.0 needed for this python installation.')
            sys.exit(1)

    # Actually creates executable from spec file
    def _build(self, args, spec_file_path):
        try:
            Version(args.app_version)
        except VersionError:
            log.error('Version format incorrect: %s', args.app_version)
            log.error("""Valid version numbers: 0.10.0, 1.1b, 1.2.1a3

        Visit url for more info:

            http://semver.org/
                      """)
            sys.exit(1)
        build_args = []
        if args.clean is True:
            build_args.append('--clean')
        build_args.append('--distpath={}'.format(self.new_dir))
        build_args.append('--workpath={}'.format(self.work_dir))
        build_args.append('-y')
        build_args.append(spec_file_path)

        log.debug('Build cmd: %s', ' '.join([b for b in build_args]))
        build_args = [str(x) for x in build_args]
        pyi_build(build_args)

    # Updates name of binary from mac to applications name
    def _mac_binary_rename(self, temp_name, app_name):
        bin_dir = os.path.join(temp_name, 'Contents', 'MacOS')
        plist = os.path.join(temp_name, 'Contents', 'Info.plist')
        with ChDir(bin_dir):
            os.rename('mac', app_name)

        # We also have to update to ensure app launches correctly
        with io.open(plist, 'r', encoding='utf-8') as f:
            plist_data = f.readlines()

        new_plist_data = []
        for d in plist_data:
            if 'mac' in d:
                new_plist_data.append(d.replace('mac', app_name))
            else:
                new_plist_data.append(d)

        with io.open(plist, 'w', encoding='utf-8') as f:
            for d in new_plist_data:
                f.write(d)

    # Creates zip on windows and gzip on other platforms
    def _archive(self, args, temp_name):
        # Now archive the file
        with ChDir(self.new_dir):
            if os.path.exists(temp_name + '.app'):
                log.debug('Got mac .app')
                app_name = temp_name + '.app'
                self._mac_binary_rename(app_name, self.app_name)
            elif os.path.exists(temp_name + '.exe'):
                log.debug('Got win .exe')
                app_name = temp_name + '.exe'
            else:
                app_name = temp_name
            version = args.app_version
            log.debug('Temp Name: %s', temp_name)
            log.debug('Appname: %s', app_name)
            log.debug('Version: %s', version)

            # Time for some archive creation!
            filename = make_archive(self.app_name, app_name, version)
            log.debug('Archive name: %s', filename)
            if args.keep is False:
                if os.path.exists(temp_name):
                    log.debug('Removing: %s', temp_name)
                    remove_any(temp_name)
                if os.path.exists(app_name):
                    log.debug('Removing: %s', temp_name)
                    remove_any(app_name)
        log.info('%s has been placed in your new folder\n', filename)


class ExternalLib(object):

    def __init__(self, name, version):
        self.name = name
        self.version = version

    def archive(self):
        filename = create_asset_archive(self.name, self.version)
        log.info('Created archive for %s: %s', self.name, filename)
