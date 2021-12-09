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
import json
import os
import pathlib

import pytest

from pyupdater import settings
from pyupdater.cli import commands, dispatch_command
from pyupdater.cli.options import (
    add_build_parser,
    add_clean_parser,
    add_keys_parser,
    add_make_spec_parser,
    add_package_parser,
    add_undo_parser,
    add_upload_parser,
    make_subparser,
)
from pyupdater.utils.storage import Storage

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

    def test_undo(self):
        assert dispatch_command(NamespaceHelper(command="undo"), test=True) is True

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


@pytest.mark.usefixtures("cleandir")
class TestUndo(object):
    @pytest.fixture
    def packages(self, shared_datadir, pyu):
        """ populate config.pyu and create corresponding dummy files """
        # collect dummy data for config.pyu
        version_meta = json.loads((shared_datadir / "version.json").read_text())
        version_meta.pop("signature", None)
        latest_key = settings.LATEST_KEY
        app_name = next(iter(version_meta[latest_key]))
        channel = next(iter(version_meta[latest_key][app_name]))
        platform = next(iter(version_meta[latest_key][app_name][channel]))
        py_repo_config = {
            "patches": {app_name: 4},  # depends on version.json...
            "package": {app_name: version_meta[latest_key][app_name][channel]}
        }
        keypack_pyu = json.loads((shared_datadir / "keypack.pyu").read_text())
        config_pyu = {
            settings.CONFIG_DB_KEY_VERSION_META: version_meta,
            settings.CONFIG_DB_KEY_PY_REPO_CONFIG: py_repo_config,
            settings.CONFIG_DB_KEY_KEYPACK: keypack_pyu,
        }
        # update the config.pyu file
        storage = Storage()
        storage.db.update(config_pyu)
        storage.db.sync()
        # set up pyu and get paths
        pyu.update_config(pyu.config)
        pyu.setup()
        files_path = pathlib.Path(pyu.ph.files_dir)
        deploy_path = pathlib.Path(pyu.ph.deploy_dir)
        # create dummy files in pyu-data/files and pyu-data/deploy
        latest_version_key = version_meta[latest_key][app_name][channel][platform]
        for key, version in version_meta[settings.UPDATES_KEY][app_name].items():
            # create file(s) in pyu-data/deploy
            filename = version[platform]["filename"]
            patch_name = version[platform].get("patch_name", None)
            for name in [filename, patch_name]:
                if name is not None:
                    (deploy_path / name).touch()
            # create file in pyu-data/files
            if key == latest_version_key:
                (files_path / filename).touch()

    def test_packages_fixture(self, packages, pyu):
        """
        Make sure our fixture does what it is supposed to do.

        Notes:
        - pyu references the same object as pyu in the packages fixture
        - numbers are based on inspection of "version.json"
        """
        assert len(pyu.ph.version_data[settings.UPDATES_KEY]["Acme"]) == 4
        deploy_path = pathlib.Path(pyu.ph.deploy_dir)
        assert len(list(deploy_path.iterdir())) == 7
        files_path = pathlib.Path(pyu.ph.files_dir)
        assert len(list(files_path.iterdir())) == 1

    def test_no_options(self, parser):
        subparser = make_subparser(parser)
        add_undo_parser(subparser)
        with pytest.raises(SystemExit):
            parser.parse_known_args(["undo"])

    @pytest.mark.parametrize(
        ["channel", "platform"],
        [("invalid channel", "win"), (None, "win"), ("stable", None)])
    def test_invalid_options(self, parser, channel, platform):
        subparser = make_subparser(parser)
        add_undo_parser(subparser)
        cmd = ["undo"]
        if channel:
            cmd.extend(["-c", channel])
        if platform:
            cmd.extend(["-p", platform])
        with pytest.raises(SystemExit):
            parser.parse_known_args(cmd)

    def test_no_packages(self, parser, pyu):
        subparser = make_subparser(parser)
        add_undo_parser(subparser)
        pyu.update_config(pyu.config)
        pyu.setup()
        cmd = ["undo", "-c", "stable", "-p", "win"]
        opts, other = parser.parse_known_args(cmd)
        commands._cmd_undo(opts)

    def test_packages(self, parser, packages, pyu, monkeypatch):
        """
        This tests the normal expected behavior, assuming we have a number of
        packages available.

        Note: pyu references the same object as pyu in the packages fixture.
        """
        # constants from tests/data/version.json
        app_name = "Acme"
        channel = "stable"
        platform = "mac"
        old_latest_key = "4.4.0.2.0"
        new_latest_key = "4.3.0.2.0"

        # helpers
        def get_latest_key():
            return pyu.ph.version_data[settings.LATEST_KEY][app_name][channel][platform]

        def get_all_versions():
            return pyu.ph.version_data[settings.UPDATES_KEY][app_name]

        # reference state (before undo)
        key_to_be_removed = get_latest_key()
        assert key_to_be_removed == old_latest_key
        version_to_be_removed = get_all_versions()[key_to_be_removed][platform]
        archive_to_be_removed = version_to_be_removed["filename"]
        patch_to_be_removed = version_to_be_removed["patch_name"]
        # Monkey patching builtins is discouraged by pytest docs, but it's
        # probably safe to make an exception for input()?
        monkeypatch.setattr("builtins.input", lambda __: key_to_be_removed)
        # Ensure our command uses the test configuration.
        monkeypatch.setattr(
            "pyupdater.utils.config.ConfigManager.load_config",
            lambda __: pyu.config)
        # Run the undo command
        subparser = make_subparser(parser)
        add_undo_parser(subparser)
        cmd = ["undo", "-c", "stable", "-p", "mac"]
        opts, __ = parser.parse_known_args(cmd)
        commands._cmd_undo(opts)
        # Refresh pyu package handler
        pyu.ph.config_loaded = False
        pyu.ph.setup()
        # Check config.pyu content
        assert get_latest_key() == new_latest_key
        remaining_versions = get_all_versions()
        assert key_to_be_removed not in remaining_versions.keys()
        # Check files
        deploy_path = pathlib.Path(pyu.ph.deploy_dir)
        files_path = pathlib.Path(pyu.ph.files_dir)
        assert not (deploy_path / archive_to_be_removed).exists()
        assert not (deploy_path / patch_to_be_removed).exists()
        assert not (files_path / archive_to_be_removed).exists()
        new_filename = remaining_versions[new_latest_key][platform]["filename"]
        assert (files_path / new_filename).exists()
        assert (deploy_path / "versions.gz").exists()
