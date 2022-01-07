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
import pathlib
import platform

import pytest

from pyupdater.utils import (
    check_repo,
    create_asset_archive,
    make_archive,
    parse_archive_name,
    PluginManager,
    remove_dot_files,
    run,
    PyuVersion,
    get_latest_version,
)


@pytest.mark.usefixtures("cleandir")
class TestUtils(object):
    def test_make_archive(self):
        with io.open("hash-test1.txt", "w", encoding="utf-8") as f:
            f.write("I should find some lorem text" * 11)

        with io.open("hash-test2.txt", "w", encoding="utf-8") as f:
            f.write("I should find some lorem text" * 5)

        filename1 = make_archive("hash", "hash-test1.txt", "0.2", "default")
        filename2 = make_archive("hash", "hash-test2.txt", "0.3", "default")

        assert os.path.exists(filename1)
        assert os.path.exists(filename2)

    def test_make_archive_issue_304(self):
        platform_map = dict(linux="nix", darwin="max", windows="win")
        target = platform_map.get(platform.system().lower())
        # create dir and dummy executable
        target_dir = pathlib.Path(target)
        target_dir.mkdir()
        target_file = target_dir / f"{target}"
        if target == "win":
            target_file = target_file.with_suffix(".exe")
        target_file.touch()
        # make archive
        make_archive(
            name="name", target=target, app_version="0.1", archive_format="default"
        )

    @pytest.mark.parametrize(
        ["filename", "expected"],
        [
            ("Acme-mac-4.1.tar.gz", ("Acme", "mac", "4.1", ".tar.gz")),
            ("with spaces-nix-0.0.1b1.zip", ("with spaces", "nix", "0.0.1b1", ".zip")),
            ("with spaces-win-0.0.1a2.zip", ("with spaces", "win", "0.0.1a2", ".zip")),
            ("pyu-win-1.tar.gz", ("pyu", "win", "1", ".tar.gz")),
            ("pyu-win-0.0.2.xz", None),
            ("pyu-wi-1.1.tar.gz", None),
            ("anything", None),
        ],
    )
    def test_parse_archive_name(self, filename, expected):
        parts = parse_archive_name(filename)
        assert parts == expected or tuple(parts.values()) == expected

    def test_create_asset_archive(self):
        with io.open("hash-test1.dll", "w", encoding="utf-8") as f:
            f.write("I should find some lorem text" * 20)

        with io.open("hash-test2.so", "w", encoding="utf-8") as f:
            f.write("I should find some lorem text" * 11)

        with io.open("binary", "w", encoding="utf-8") as f:
            f.write("I should find some lorem text" * 5)

        filename = create_asset_archive("hash-test1.dll", "0.1")
        filename1 = create_asset_archive("hash-test2.so", "0.2")
        filename2 = create_asset_archive("binary", "0.3")

        assert os.path.exists(filename)
        assert os.path.exists(filename1)
        assert os.path.exists(filename2)

    def test_check_repo_fail(self):
        assert check_repo() is False

    def test_remove_dot_files(self):
        bad_list = [".DS_Store", "test", "stuff", ".trash"]
        good_list = ["test", "stuff"]
        for n in remove_dot_files(bad_list):
            assert n in good_list

    def test_run(self):
        assert run('echo "hello world!"') == 0

    @pytest.mark.parametrize(
        "n, a",
        [("test", None), (None, "test"), (1, "test"), ("test", 1), ("test", "test")],
    )
    def test_plugin_manager_load(self, n, a):
        class Plugin(object):
            name = n
            author = a

        pm = PluginManager(plugins=[Plugin()])

        if isinstance(n, str) and isinstance(a, str):
            assert len(pm.plugins) == 1
        else:
            assert len(pm.plugins) == 0

    def test_default_plugin_detection_s3(self):
        pm = PluginManager()

        plugin_names = [n["name"] for n in pm.plugins]
        assert "s3" in plugin_names

    def test_default_plugin_detection_scp(self):
        pm = PluginManager()

        plugin_names = [n["name"] for n in pm.plugins]
        assert "scp" in plugin_names

    def test_plugin_unique_names(self):
        class Plugin1(object):
            name = "test"
            author = "test1"

        class Plugin2(object):
            name = "test"
            author = "test2"

        pm = PluginManager(plugins=[Plugin1(), Plugin2()])

        plugin_names = [n["name"] for n in pm.plugins]

        assert "test" in plugin_names
        assert "test2" in plugin_names

    def test_plugin_config(self):
        class TPlugin(object):
            name = "test"
            author = "test1"
            bucket = ""

            def init_config(self, config):
                self.bucket = config.get("bucket", "bad")

        pm = PluginManager(
            plugin_configs={"test-test1": {"bucket": "test_bucket"}},
            plugins=[TPlugin()],
        )

        p = pm.get_plugin("test", False)
        assert p.bucket == ""

        p = pm.get_plugin("test", True)
        assert p.bucket == "test_bucket"


class TestPyuVersion(object):
    @pytest.mark.parametrize(
        ["internal_version", "expected"],
        [
            ("4.4.3.2.0", "4.4.3"),
            ("0.0.0.2.3", "0.0.0"),
            ("0.0.0.3.0", "0.0.0.3.0"),  # not an internal version number
            ("4.4.2.0.5", "4.4.2a5"),
            ("4.4.1.1.0", "4.4.1b0"),
            ("1.2.3a5+something", "1.2.3a5+something"),
            ("1.2.3", "1.2.3"),
            ("v1.2.3", "v1.2.3"),
            ("invalid", "invalid"),
        ],
    )
    def test_ensure_pep440_compat(self, internal_version, expected):
        # Note that non-internal versions (including invalid ones) are passed
        # unmodified, as we leave the actual parsing to packaging.version.
        # Note that the trailing ".2.0" must be removed from the internal
        # version number, otherwise it is interpreted as part of the "stable"
        # release number, so that e.g. 1.0.0.2.0 > 1.0.0 would return True (
        # when using internal version numbers, these should be equal)
        assert PyuVersion.ensure_pep440_compat(internal_version) == expected

    @pytest.mark.parametrize(
        ["pep440_version", "expected"],
        [
            ("1", "1.0.0.2.0"),
            ("1.0", "1.0.0.2.0"),
            ("1.0.0", "1.0.0.2.0"),
            ("1.0.0.0", "1.0.0.2.0"),
            ("1.2.3a5", "1.2.3.0.5"),
            ("4.5.6beta8", "4.5.6.1.8"),
        ],
    )
    def test_pyu_format(self, pep440_version, expected):
        assert PyuVersion(pep440_version).pyu_format() == expected


class TestGetLatestVersion(object):
    @pytest.mark.parametrize(
        ["channel", "expected"],
        [("alpha", "1.2a0"), ("beta", "1.1"), ("stable", "1.1")]
    )
    def test_channel(self, version_manifest, channel, expected):
        args = ("Acme", "win", channel, version_manifest)
        assert get_latest_version(*args, strict=True) == PyuVersion(expected)

    def test_no_eligible_versions(self, version_manifest):
        # remove all final releases from the manifest
        version_manifest["updates"]["Acme"].pop("1.0.0.2.0")
        version_manifest["updates"]["Acme"].pop("1.1.0.2.0")
        # check only stable versions
        args = ("Acme", "win", "stable", version_manifest)
        assert get_latest_version(*args, strict=True) is None

    def test_platform_not_available(self, version_manifest):
        args = ("Acme", "mac", "stable", version_manifest)
        assert get_latest_version(*args, strict=True) is None

    def test_not_strict(self, version_manifest):
        args = ("Acme", "win", "stable", version_manifest)
        assert get_latest_version(*args, strict=False) == PyuVersion("1.2a0")
