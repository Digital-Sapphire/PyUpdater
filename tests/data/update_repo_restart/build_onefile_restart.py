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
import logging
import os
import re
import sys
import tarfile
import zipfile

from dsdev_utils.system import get_system

log = logging.getLogger()


home_dir = os.path.dirname(os.path.abspath(__file__))


def build(app):
    # Pyinstaller's --clean is not 'multiprocessing safe',
    # let's use our own cache
    os.environ["PYINSTALLER_CONFIG_DIR"] = os.path.join(home_dir, ".cache")
    cmd = "pyupdater build -F {} --clean --path={} " "--app-version={} {}".format(
        app[2], home_dir, app[1], app[0]
    )
    os.system(cmd)


def extract(filename):
    ext = os.path.splitext(filename)[1]
    if ext == ".zip":
        archive = zipfile.ZipFile(filename, "r")
    else:
        archive = tarfile.open(filename, "r:gz")

    archive.extractall()


def main(use_custom_dir, port, windowed, split_version):
    cmd1 = "pyupdater pkg -P"
    cmd2 = "pyupdater pkg -S"

    if split_version:
        cmd2 += " --split-version"

    scripts = [
        ("app_restart_01.py", "4.1", "--windowed" if windowed else ""),
        ("app_restart_02.py", "4.2", "--windowed" if windowed else ""),
    ]

    # We use this flag to untar & move our binary to the
    # current working directory
    first = True
    # patch config_file for custom port number
    config_file = open("client_config.py", "rt").read()
    config_file = re.sub(r"localhost:\d+", "localhost:%s" % port, config_file)
    # patch config_file for use_custom_dir
    if use_custom_dir:
        config_file += "\n    USE_CUSTOM_DIR = True\n"
    open("client_config.py", "wt").write(config_file)
    for s in scripts:
        build(s)
        if first:
            if sys.platform == "win32":
                ext = ".zip"
            else:
                ext = ".tar.gz"

            # Build path to archive
            archive_path = os.path.join(
                "pyu-data", "new", "Acme-{}-4.1{}".format(get_system(), ext)
            )

            if not os.path.exists(archive_path):
                print("Archive did not build!")
                sys.exit(1)

            # We extract the Acme binary here. When we call pyupdater pkg -P
            # the Acme binary will be moved to the deploy folder. In our test
            # (test_pyupdater.TestExecution.test_execution_update_*) we
            # move all of the files from the deploy directory to the cwd
            # of the test runner.
            extract(archive_path)

            first = False

        os.system(cmd1)

    os.system(cmd2)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(
            "usage: %s <use_custom_dir> <port> <windowed> <split_version>" % sys.argv[0]
        )
    else:
        main(
            sys.argv[1] == "True",
            sys.argv[2],
            sys.argv[3] == "True",
            sys.argv[4] == "True",
        )
