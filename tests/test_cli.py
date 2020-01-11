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
from __future__ import unicode_literals

import io
import os

import pytest

from pyupdater.cli import commands, dispatch_command
from pyupdater.cli.options import (
    add_build_parser,
    add_clean_parser,
    add_keys_parser,
    add_make_spec_parser,
    add_package_parser,
    add_upload_parser,
    make_subparser,
)

commands.TEST = True


class NamespaceHelper(object):
    def __init__(self, **kwargs):
        self.reload(**kwargs)

    def _clear(self):
        self.__dict__.clear()

    def _pre_update(self):
        self.__dict__.update(test=True)

    def reload(self, **kwargs):
        self._clear()
        self._pre_update()
        self.__dict__.update(**kwargs)

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            self.__dict__[name] = None
            return None


@pytest.mark.usefixtures("cleandir")
class TestCommandDispatch(object):
    def test_build(self):
        assert dispatch_command(NamespaceHelper(command="build"), test=True) is True

    def test_clean(self):
        assert dispatch_command(NamespaceHelper(command="clean"), test=True) is True

    def test_settings(self):
        assert dispatch_command(NamespaceHelper(command="settings"), test=True) is True

    def test_init(self):
        assert dispatch_command(NamespaceHelper(command="init"), test=True) is True

    def test_keys(self):
        assert dispatch_command(NamespaceHelper(command="keys"), test=True) is True

    def test_make_spec(self):
        assert dispatch_command(NamespaceHelper(command="make-spec"), test=True) is True

    def test_pkg(self):
        assert dispatch_command(NamespaceHelper(command="pkg"), test=True) is True

    def test_collect_debug_info(self):
        assert (
            dispatch_command(NamespaceHelper(command="collect-debug-info"), test=True)
            is True
        )

    def test_upload(self):
        assert dispatch_command(NamespaceHelper(command="upload"), test=True) is True

    def test_version(self):
        assert dispatch_command(NamespaceHelper(command="version"), test=True) is True


@pytest.mark.usefixtures("cleandir")
class TestBuilder(object):
    def test_build_no_options(self, parser):
        subparser = make_subparser(parser)
        add_build_parser(subparser)
        with pytest.raises(SystemExit):
            parser.parse_known_args(["build"])

    def test_build_no_arguments(self, parser, pyu):
        pyu.setup()
        subparser = make_subparser(parser)
        add_build_parser(subparser)
        with pytest.raises(SystemExit):
            with io.open("app.py", "w", encoding="utf-8") as f:
                f.write("from __future__ import print_function\n")
                f.write('print("Hello, World!")')
            opts, other = parser.parse_known_args(["build", "app.py"])
            commands._cmd_build(opts, other)


@pytest.mark.usefixtures("cleandir", "parser")
class TestClean(object):
    def test_no_args(self, parser):
        subparser = make_subparser(parser)
        add_clean_parser(subparser)
        assert parser.parse_known_args(["clean"])

    def test_execution(self, parser):
        update_folder = "pyu-data"
        data_folder = ".pyupdater"
        subparser = make_subparser(parser)
        add_clean_parser(subparser)
        os.mkdir(update_folder)
        os.mkdir(data_folder)
        args, other = parser.parse_known_args(["clean", "-y"])
        commands._cmd_clean(args)
        assert not os.path.exists(update_folder)
        assert not os.path.exists(data_folder)

    def test_execution_no_clean(self, parser):
        update_folder = "pyu-data"
        data_folder = ".pyupdater"
        subparser = make_subparser(parser)
        add_clean_parser(subparser)
        args, other = parser.parse_known_args(["clean", "-y"])
        commands._cmd_clean(args)
        assert not os.path.exists(update_folder)
        assert not os.path.exists(data_folder)


@pytest.mark.usefixtures("cleandir", "parser")
class TestKeys(object):
    def test_no_options(self, parser):
        subparser = make_subparser(parser)
        add_keys_parser(subparser)
        assert parser.parse_known_args(["keys"])

    def test_create_keys(self):
        commands._cmd_keys(NamespaceHelper(command="keys", create_keys=True))
        assert os.path.exists("keypack.pyu")


@pytest.mark.usefixtures("cleandir", "parser", "pyu")
class TestMakeSpec(object):
    def test_deprecated_opts(self, parser, pyu):
        pyu.setup()
        subparser = make_subparser(parser)
        add_make_spec_parser(subparser)
        with io.open("app.py", "w", encoding="utf-8") as f:
            f.write('print "Hello World"')
        opts, other = parser.parse_known_args(["make-spec", "-F", "app.py"])
        commands._cmd_make_spec(opts, other)

    def test_execution(self, parser, pyu):
        pyu.setup()
        subparser = make_subparser(parser)
        add_make_spec_parser(subparser)
        with io.open("app.py", "w", encoding="utf-8") as f:
            f.write('print "Hello World"')
        opts, other = parser.parse_known_args(["make-spec", "-F", "app.py"])
        commands._cmd_make_spec(opts, other)


@pytest.mark.usefixtures("cleandir")
class TestPkg(object):
    def test_pkg_execution(self, parser, pyu):
        subparser = make_subparser(parser)
        add_package_parser(subparser)
        pyu.update_config(pyu.config)
        pyu.setup()
        cmd = ["pkg", "-P", "-S"]
        opts, other = parser.parse_known_args(cmd)
        commands._cmd_pkg(opts)

    def test_pkg_execution_no_opts(self, parser, pyu):
        subparser = make_subparser(parser)
        add_package_parser(subparser)

        pyu.update_config(pyu.config)
        pyu.setup()
        cmd = ["pkg"]

        opts, other = parser.parse_known_args(cmd)
        commands._cmd_pkg(opts)
