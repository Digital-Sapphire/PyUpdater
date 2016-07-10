import argparse
import logging
import os
# Optpare is deprecated
try:
    import optparse
except ImportError:
    optparse = None

try:
    from PyInstaller import __version__ as pyi_version
except ImportError:
    pyi_version = '0.0'
from PyInstaller.building import makespec as _pyi_makespec
from PyInstaller import compat as _pyi_compat
from PyInstaller import log as _pyi_log


log = logging.getLogger(__name__)

# PyInstaller versions 3.0 & prior used optparse
is_pyi30 = pyi_version == '3.0'


def pyi_makespec(pyi_args):  # pragma: no cover
    """Wrapper to configure make_spec for multipule pyinstaller versions"""
    def run_makespec(args, opts=None):
        """Setup args & run make_spec command"""
        if is_pyi30:
            # Split pathex by using the path separator
            temppaths = opts.pathex[:]
            opts.pathex = []
            for p in temppaths:
                opts.pathex.extend(p.split(os.pathsep))

            # Fix for issue #4 - Not searching cwd for modules
            opts.pathex.insert(0, os.getcwd())

            spec_file = _pyi_makespec.main(args, **opts.__dict__)
        else:
            # Split pathex by using the path separator
            temppaths = args.pathex[:]
            args.pathex = []
            for p in temppaths:
                args.pathex.extend(p.split(os.pathsep))

            # Fix for issue #4 - Not searching cwd for modules
            args.pathex.insert(0, os.getcwd())

            spec_file = _pyi_makespec.main(args.scriptname, **vars(args))
        log.info('wrote %s', spec_file)


    if is_pyi30:
        # We will exit with an error message in builder.py
        if optparse is None:
            log.debug('optparse is not available in this python distribution')
            return False
        parser = optparse.OptionParser(usage=('%prog [opts] <scriptname> [ '
                                              '<scriptname> ...] | <specfil'
                                              'e>'))
        _pyi_makespec.__add_options(parser)
        _pyi_log.__add_options(parser)
        _pyi_compat.__add_obsolete_options(parser)

        opts, args = parser.parse_args(pyi_args)
        _pyi_log.__process_options(parser, opts)

        run_makespec(args, opts)
    else:
        parser = argparse.ArgumentParser()
        _pyi_makespec.__add_options(parser)
        _pyi_log.__add_options(parser)
        _pyi_compat.__add_obsolete_options(parser)
        parser.add_argument('scriptname', nargs='+')

        args = parser.parse_args(pyi_args)

        # We call init because it loads logger into the global
        # namespace of the Pyinstaller.log module. logger is used
        # in the Pyinstaller.log.__process_options call
        _pyi_log.init()
        _pyi_log.__process_options(parser, args)

        run_makespec(args)

    return True
