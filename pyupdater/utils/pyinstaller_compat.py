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
import logging
import os

try:
    from PyInstaller import __version__ as pyi_version
except ImportError:
    pyi_version = "0.0"
from PyInstaller.building import makespec as _pyi_makespec
from PyInstaller import compat as _pyi_compat
from PyInstaller import log as _pyi_log


log = logging.getLogger(__name__)


def pyi_makespec(pyi_args):  # pragma: no cover
    """Wrapper to configure make_spec for multipule pyinstaller versions"""

    def run_makespec(_args):
        """Setup args & run make_spec command"""
        # Split pathex by using the path separator
        temppaths = _args.pathex[:]
        _args.pathex = []
        for p in temppaths:
            _args.pathex.extend(p.split(os.pathsep))

        # Fix for issue #4 - Not searching cwd for modules
        _args.pathex.insert(0, os.getcwd())

        spec_file = _pyi_makespec.main(_args.scriptname, **vars(_args))
        log.debug("wrote %s", spec_file)

    parser = argparse.ArgumentParser()
    # We are hacking into pyinstaller here & are aware of the risks
    # using noqa below so landscape.io will ignore it
    _pyi_makespec.__add_options(parser)  # noqa
    _pyi_log.__add_options(parser)  # noqa
    if hasattr(_pyi_compat, "__add_obsolete_options"):
        _pyi_compat.__add_obsolete_options(parser)  # noqa
    # End hacking
    parser.add_argument("scriptname", nargs="+")

    args = parser.parse_args(pyi_args)

    # We call init because it loads logger into the global
    # namespace of the Pyinstaller.log module. logger is used
    # in the Pyinstaller.log.__process_options call
    if hasattr(_pyi_log, "init"):
        _pyi_log.init()
    # We are hacking into pyinstaller here & are aware of the risks
    # using noqa below so landscape.io will ignore it
    _pyi_log.__process_options(parser, args)  # noqa
    # End hacking

    run_makespec(args)

    return True
