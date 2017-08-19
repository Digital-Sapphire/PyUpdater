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

import logging
from logging.handlers import RotatingFileHandler
import os
import sys

from appdirs import user_log_dir
from dsdev_utils.logger import logging_formatter

from pyupdater import __version__, settings
from pyupdater.cli import commands
from pyupdater.cli.options import get_parser


log = logging.getLogger()
log.setLevel(logging.DEBUG)

# Log to pyu.log if available
local_debug_file_path = os.path.join(os.getcwd(), 'pyu.log')
if os.path.exists(local_debug_file_path):  # pragma: no cover
    fh = logging.FileHandler(local_debug_file_path)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging_formatter)
    log.addHandler(fh)

# Console logger
fmt = logging.Formatter('[%(levelname)s] %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(fmt)
sh.setLevel(logging.INFO)
log.addHandler(sh)

# Default log directory
LOG_DIR = user_log_dir(settings.APP_NAME, settings.APP_AUTHOR)
if not os.path.exists(LOG_DIR):  # pragma: no cover
    os.makedirs(LOG_DIR)

log_file = os.path.join(LOG_DIR, settings.LOG_FILENAME_DEBUG)
rfh = RotatingFileHandler(log_file, maxBytes=1048576, backupCount=2)
rfh.setFormatter(logging_formatter)
rfh.setLevel(logging.DEBUG)
log.addHandler(rfh)

# The collect_debug_info command will use this
commands.LOG_DIR = LOG_DIR


def _real_main(args, namespace_test_helper=None):  # pragma: no cover
    pyi_args = None
    if args is None:
        args = sys.argv[1:]

    if namespace_test_helper is None:
        parser = get_parser()
        args, pyi_args = parser.parse_known_args(args)
    else:
        # Used for tests
        args = namespace_test_helper

    dispatch_command(args, pyi_args)


# Dispatch the passed in command to its respective function in
# pyupdater.cli.commands
def dispatch_command(args, pyi_args=None, test=False):
    # Turns collect-debug-info into collect_debug_info
    cmd_str = "_cmd_" + args.command.replace('-', '_')
    if hasattr(commands, cmd_str):
        cmd = getattr(commands, cmd_str)
        # We are just making sure we can load the function
        if test:
            return True
        cmd(args, pyi_args)
    else:
        # This should only get hit by misconfigured tests.
        # "Should" being the key word here :)
        log.error('Unknown Command: %s', cmd_str)
        return False


def main(args=None):  # pragma: no cover
    log.info('PyUpdater %s', __version__)
    try:
        _real_main(args)
    except KeyboardInterrupt:
        # Someones quick on the draw
        print('\n')
        msg = 'Exited by user'
        log.warning(msg)
    except Exception as err:
        print(err)
        log.error(err)
        log.debug(err, exc_info=True)


if __name__ == '__main__':  # pragma: no cover
    arguments = sys.argv[1:]
    main(arguments)
