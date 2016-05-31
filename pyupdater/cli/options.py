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
import argparse


def make_parser():
    parser = argparse.ArgumentParser(usage='%(prog)s ')
    return parser


def make_subparser(parser):
    subparsers = parser.add_subparsers(help='commands', dest='command')
    return subparsers


def _build_make_spec_commom(subparser):
    # Start of args override
    # start a clean build
    subparser.add_argument('--clean', help='Clean build. '
                           'Bypass the cache', action="store_true")

    # This will be set to the pyu-data/new directory.
    # When we make the final compressed archive we will look
    # for an exe in that dir.
    subparser.add_argument('-o', '--distpath', help=argparse.SUPPRESS)

    # Will be set to .pyupdater/spec/
    # Trying to keep root dir clean
    subparser.add_argument('--specpath', help=argparse.SUPPRESS)

    # Will be set to .pyupdater/build
    # Trying to keep root dir clean
    subparser.add_argument('--workpath', help=argparse.SUPPRESS)

    # Will be set to platform name i.e. mac, win, nix, nix64, arm\
    # When archiving we will change the name to the value passed to
    # --app-name
    subparser.add_argument('-n', '--name', help=argparse.SUPPRESS)

    # Just capturing these argument.
    # PyUpdater only supports onefile mode at the moment
    subparser.add_argument('-D', '--onedir', action="store_true",
                           help=argparse.SUPPRESS)

    # Just capturing these argument.
    # Will be added later to pyinstaller build command
    subparser.add_argument('-F', '--onefile', action="store_true",
                           help=argparse.SUPPRESS)

    # End of args override

    subparser.add_argument('--app-version', dest="app_version",
                           required=True)
    subparser.add_argument('-k', '--keep', dest='keep', action='store_true',
                           help='Will not delete executable after archiving')


def add_archive_parser(subparsers):
    archive_parser = subparsers.add_parser('archive', help='Archives external '
                                           'file which needs updating. Can be '
                                           'binary, library, anything really.',
                                           usage='%(prog)s [opts] filename')
    archive_parser.add_argument('--name', required=True, help='Name used when '
                                'renaming binary before archiving.')
    archive_parser.add_argument('--target-name', required=True, help='Name of '
                                'file to be archived')
    archive_parser.add_argument('--version', required=True, help='Version of '
                                'file')
    archive_parser.add_argument('-k', '--keep', action='store_true',
                                help='Will not delete source file '
                                'after archiving')


def add_build_parser(subparsers):
    build_parser = subparsers.add_parser('build', help='compiles script '
                                         'or spec file',
                                         usage='%(prog)s [opts]<script>')
    _build_make_spec_commom(build_parser)


def add_make_spec_parser(subparsers):
    make_spec_parser = subparsers.add_parser('make-spec', help='Creates '
                                             'spec file',
                                             usage='%(prog)s <script> '
                                             '[opts]')
    _build_make_spec_commom(make_spec_parser)


def add_clean_parser(subparsers):
    clean_parser = subparsers.add_parser('clean',
                                         help='* WARNING * removes all '
                                         'traces of pyupdater for the '
                                         'current repo')
    clean_parser.add_argument('-y', '--yes', help='Confirms removal of '
                              'pyu-data & .pyupdater folder',
                              action='store_true')


def add_init_parser(subparsers):
    init_parser = subparsers.add_parser('init', help='initializes a '
                                        'src directory')
    # used to suppress landscape.io warning
    init_parser.add_argument('--dummy', help=argparse.SUPPRESS)


def add_keys_parser(subparsers):
    keys_parser = subparsers.add_parser('keys', help='Manage signing keys')
    keys_parser.add_argument('-i', '--import', help='Imports a keypack from '
                             'the current working directory',
                             action='store_true', dest='import_keys')
    keys_parser.add_argument('-c', '--create', help='Creates keypack. Should '
                             'only be used on your off-line machine',
                             action='store_true',)
    keys_parser.add_argument('-y', '--yes', help='Will run command without '
                             'conformation prompt', action='store_true')


def add_debug_parser(subparsers):
    log_parser = subparsers.add_parser('collect-debug-info',
                                       help='Upload debug logs to github '
                                       'gist and return url.')
    log_parser.add_argument('--dummy', help=argparse.SUPPRESS)


def add_package_parser(subparsers):
    package_parser = subparsers.add_parser('pkg', help='Manages creation of '
                                           'file meta-data & signing')
    package_parser.add_argument('-p', '-P', '--process',
                                help='Adds update metadata to version file & '
                                'moves files from the new to deploy '
                                'directory.',
                                action='store_true', dest='process')

    package_parser.add_argument('-s', '-S', '--sign', help='Sign version file',
                                action='store_true', dest='sign')

    package_parser.add_argument('-v', '--verbose', help='More output messages',
                                action='store_true', dest='verbose')

def add_plugin_parser(subparsers):
    plugin_parser = subparsers.add_parser('plugins', help='Shows installed '
                                          'plugins')
    plugin_parser.add_argument('--dummy', help=argparse.SUPPRESS)


def add_settings_parser(subparsers):
    settings_parser = subparsers.add_parser('settings', help='Updated '
                                            'config settings')
    settings_parser.add_argument('--config-path',
                                 help='Path to place your client config. '
                                 'You\'ll need to import this file to ini'
                                 'tialize the update process.',
                                 action='store_true')
    settings_parser.add_argument('--company',
                                 help='Change company name',
                                 action='store_true')
    settings_parser.add_argument('--urls', help='Change update urls',
                                 action='store_true')
    settings_parser.add_argument('--patches', help='Changed patch support',
                                 action='store_true')
    settings_parser.add_argument('--plugin', help='Change the named plugin\'s '
                                 'settings', dest='plugin')
    settings_parser.add_argument('--show-plugin', help='Show the name '
                                 'plugin\'s settings', dest='show_plugin')


def add_upload_parser(subparsers):
    upload_parser = subparsers.add_parser('upload', help='Uploads files')
    upload_parser.add_argument('--keep', help='Keep files after upload',
                               action='store_true')
    upload_parser.add_argument('-s', '--service', help='The plugin for '
                               'uploads', dest='service')


def add_version_parser(subparsers):
    version_parser = subparsers.add_parser('version', help='Show version')
    version_parser.add_argument('--dummy', help=argparse.SUPPRESS)


def get_parser():
    parser = make_parser()
    subparsers = make_subparser(parser)
    add_archive_parser(subparsers)
    add_build_parser(subparsers)
    add_clean_parser(subparsers)
    add_debug_parser(subparsers)
    add_init_parser(subparsers)
    add_keys_parser(subparsers)
    add_make_spec_parser(subparsers)
    add_package_parser(subparsers)
    add_plugin_parser(subparsers)
    add_settings_parser(subparsers)
    add_upload_parser(subparsers)
    add_version_parser(subparsers)
    return parser
