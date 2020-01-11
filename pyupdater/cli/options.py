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
import argparse


def make_parser():
    parser = argparse.ArgumentParser(usage="%(prog)s ")
    return parser


def make_subparser(parser):
    subparsers = parser.add_subparsers(help="commands", dest="command")
    return subparsers


def _build_make_spec_common(subparser):
    subparser.add_argument(
        "--pyinstaller-log-info",
        dest="pyi_log_info",
        action="store_true",
        help="Prints PyInstaller execution info to console",
    )

    # This will be set to the pyu-data/new directory.
    # When we make the final compressed archive we will look
    # for an exe in that dir.
    subparser.add_argument("-o", "--distpath", help=argparse.SUPPRESS)

    # Will be set to .pyupdater/spec/
    # Trying to keep root dir clean
    subparser.add_argument("--specpath", help=argparse.SUPPRESS)

    # Will be set to .pyupdater/build
    # Trying to keep root dir clean
    subparser.add_argument("--workpath", help=argparse.SUPPRESS)

    # Will be set to platform name i.e. mac, win, nix, nix64, arm\
    # When archiving we will change the name to the value passed to
    # --app-name
    subparser.add_argument("-n", "--name", help=argparse.SUPPRESS)


def add_archive_parser(subparsers):
    archive_parser = subparsers.add_parser(
        "archive",
        help="Archive an asset "
        "which needs updating. Can be "
        "another executable, .so, .dll, "
        ".img, etc.",
        usage="%(prog)s [opts] filename",
    )
    archive_parser.add_argument(
        "--name", required=True, help="Name of the " "asset to archive"
    )
    archive_parser.add_argument("--version", required=True, help="Version of " "file")
    archive_parser.add_argument(
        "-k",
        "--keep",
        action="store_true",
        help="Will not delete source file " "after archiving",
    )


def add_build_parser(subparsers):
    build_parser = subparsers.add_parser(
        "build", help="Compiles script " "or spec file", usage="%(prog)s [opts]<script>"
    )
    build_parser.add_argument(
        "--archive-format",
        default="default",
        choices=["zip", "gztar", "bztar", "default"],
    )
    # start a clean build
    build_parser.add_argument(
        "--clean", action="store_true", help="Clean build. Bypass the cache"
    )

    build_parser.add_argument("--app-version", dest="app_version", required=True)
    build_parser.add_argument(
        "-k",
        "--keep",
        dest="keep",
        action="store_true",
        help="Will not delete executable " "after archiving",
    )

    _build_make_spec_common(build_parser)


def add_clean_parser(subparsers):
    clean_parser = subparsers.add_parser(
        "clean",
        help="* WARNING * removes all " "traces of pyupdater from the " "current repo",
    )
    clean_parser.add_argument(
        "-y",
        "--yes",
        help="Confirms removal of " "pyu-data & .pyupdater folder",
        action="store_true",
    )


def add_debug_parser(subparsers):
    log_parser = subparsers.add_parser(
        "collect-debug-info", help="Upload debug logs to github " "gist and return url."
    )
    log_parser.add_argument("--dummy", help=argparse.SUPPRESS)


def add_init_parser(subparsers):
    init_parser = subparsers.add_parser("init", help="Initializes a " "src directory")
    # used to suppress landscape.io warning
    init_parser.add_argument("--dummy", help=argparse.SUPPRESS)


def add_make_spec_parser(subparsers):
    make_spec_parser = subparsers.add_parser(
        "make-spec", help="Creates " "spec file", usage="%(prog)s <script> " "[opts]"
    )

    _build_make_spec_common(make_spec_parser)


def add_keys_parser(subparsers):
    keys_parser = subparsers.add_parser("keys", help="Manage signing keys")
    keys_parser.add_argument(
        "-i",
        "--import",
        help="Imports a keypack from " "the current working directory",
        action="store_true",
        dest="import_keys",
    )
    keys_parser.add_argument(
        "-c",
        "--create",
        help="Creates keypack. Should " "only be used on your off-line machine",
        action="store_true",
        dest="create_keys",
    )


def add_package_parser(subparsers):
    package_parser = subparsers.add_parser(
        "pkg", help="Manage creation of " "file meta-data & signing"
    )
    package_parser.add_argument(
        "-p",
        "-P",
        "--process",
        help="Adds update metadata to version file & "
        "moves files from the new to deploy "
        "directory.",
        action="store_true",
        dest="process",
    )

    package_parser.add_argument(
        "-s", "-S", "--sign", help="Sign version file", action="store_true", dest="sign"
    )

    package_parser.add_argument(
        "--split-version",
        action="store_true",
        dest="split_version",
        help="Creates a version manifest for the current platform only. For CI/CD",
    )

    package_parser.add_argument(
        "-v",
        "--verbose",
        help="More output messages",
        action="store_true",
        dest="verbose",
    )


def add_plugin_parser(subparsers):
    plugin_parser = subparsers.add_parser("plugins", help="Shows installed " "plugins")
    plugin_parser.add_argument("--dummy", help=argparse.SUPPRESS)


def add_settings_parser(subparsers):
    settings_parser = subparsers.add_parser(
        "settings", help="Updated " "config settings"
    )
    settings_parser.add_argument(
        "--company", help="Change company name", action="store_true"
    )
    settings_parser.add_argument(
        "--config-path",
        help="Path to place your client config. "
        "You'll need to import this file to ini"
        "tialize the update process.",
        action="store_true",
    )
    settings_parser.add_argument(
        "--http-timeout",
        help="Settings the timeout, in seconds, for the FileDownloader",
        action="store_true",
    )
    settings_parser.add_argument(
        "--max-download-retries",
        help="Set the max " "number of times to try a download.",
        action="store_true",
    )
    settings_parser.add_argument(
        "--patches", help="Changed patch support", action="store_true"
    )
    settings_parser.add_argument(
        "--plugin", help="Change the named plugin's " "settings", dest="plugin"
    )
    settings_parser.add_argument(
        "--show-plugin", help="Show the name " "plugin's settings", dest="show_plugin"
    )
    settings_parser.add_argument(
        "--urls", help="Change update urls", action="store_true"
    )


def add_upload_parser(subparsers):
    upload_parser = subparsers.add_parser("upload", help="Uploads files")
    upload_parser.add_argument(
        "--keep", help="Keep files after upload", action="store_true"
    )
    upload_parser.add_argument(
        "-s", "--service", help="The plugin used for " "uploads", dest="service"
    )


def add_version_parser(subparsers):
    version_parser = subparsers.add_parser("version", help="Show version")
    version_parser.add_argument("--dummy", help=argparse.SUPPRESS)


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
